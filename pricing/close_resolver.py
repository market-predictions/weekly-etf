from __future__ import annotations

from pathlib import Path

from .budget_manager import BudgetManager
from .cache import cache_get, cache_put, load_daily_cache, save_daily_cache
from .models import PRICED_CLOSE_STATUSES, PriceRequest, PriceResult
from .symbol_resolver import SymbolResolver
from .clients import alpha_vantage, fmp, issuer_override, twelve_data, yahoo_history

SUCCESS_STATUSES = PRICED_CLOSE_STATUSES


def _apply_request_lineage(result: PriceResult, req: PriceRequest) -> PriceResult:
    """Attach role/tier context that is only known at resolver level."""
    result.asset_role = req.kind
    if req.kind in {"holding", "challenger"}:
        result.pricing_tier = "valuation_grade"
    else:
        result.pricing_tier = "research_grade"
    return result


class CloseResolver:
    def __init__(self, registry_file: str | Path, rate_limit_file: str | Path, run_date: str):
        self.symbol_resolver = SymbolResolver(registry_file)
        self.budget = BudgetManager(rate_limit_file)
        self.run_date = run_date
        self.cache = load_daily_cache(run_date)

    def _fetch_from_source(self, source: str, req: PriceRequest) -> PriceResult:
        provider_symbol = self.symbol_resolver.get_provider_symbol(req.symbol, source)
        provider_exchange = self.symbol_resolver.get_expected_exchange(req.symbol)
        if source == "issuer_override":
            handler = self.symbol_resolver.get_issuer_handler(req.symbol)
            return issuer_override.fetch_close(provider_symbol, req.requested_close_date, handler, canonical_symbol=req.symbol, provider_exchange=provider_exchange)
        if source == "twelve_data":
            return twelve_data.fetch_close(provider_symbol, req.requested_close_date, canonical_symbol=req.symbol, provider_exchange=provider_exchange)
        if source == "fmp":
            return fmp.fetch_close(provider_symbol, req.requested_close_date, canonical_symbol=req.symbol, provider_exchange=provider_exchange)
        if source == "alpha_vantage":
            return alpha_vantage.fetch_close(provider_symbol, req.requested_close_date, canonical_symbol=req.symbol, provider_exchange=provider_exchange)
        if source == "yahoo_history":
            return yahoo_history.fetch_close(provider_symbol, req.requested_close_date, canonical_symbol=req.symbol, provider_exchange=provider_exchange)
        return PriceResult(req.symbol, req.requested_close_date, None, None, None, source, None, None, "unresolved", "low", error="Unknown source")

    def resolve(self, req: PriceRequest) -> PriceResult:
        source_order = self.symbol_resolver.get_source_order(req.symbol, req.kind)
        unresolved_cached: list[PriceResult] = []

        for source in source_order:
            cached = cache_get(self.cache, req.symbol, req.requested_close_date, source)
            if cached:
                cached_result = _apply_request_lineage(PriceResult(**cached), req)
                if cached_result.status in SUCCESS_STATUSES and cached_result.price is not None:
                    return cached_result
                # Do not return an unresolved cached row. Earlier versions did
                # that, which prevented fallback sources such as yahoo_history
                # from repairing missing challenger closes in the same run.
                unresolved_cached.append(cached_result)
                continue

            if source in self.budget.budgets:
                if not self.budget.can_spend(source, req.kind):
                    continue
                self.budget.sleep_if_needed(source)

            result = _apply_request_lineage(self._fetch_from_source(source, req), req)

            if source in self.budget.budgets:
                self.budget.register_spend(source)

            cache_put(self.cache, result.to_dict())
            save_daily_cache(self.run_date, self.cache)

            if result.status in SUCCESS_STATUSES and result.price is not None:
                return result

        if unresolved_cached:
            details = "; ".join(
                f"{item.source}:{item.status}:{item.error or 'no close'}" for item in unresolved_cached[:5]
            )
            return _apply_request_lineage(PriceResult(
                req.symbol,
                req.requested_close_date,
                None,
                None,
                None,
                None,
                None,
                None,
                "unresolved",
                "low",
                error=f"All configured API sources unresolved; cached unresolved attempts: {details}",
            ), req)

        return _apply_request_lineage(PriceResult(req.symbol, req.requested_close_date, None, None, None, None, None, None, "unresolved", "low", error="All configured API sources unresolved"), req)
