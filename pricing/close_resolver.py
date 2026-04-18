from __future__ import annotations

from pathlib import Path

from .budget_manager import BudgetManager
from .cache import load_daily_cache, save_daily_cache, cache_get, cache_put
from .models import PriceRequest, PriceResult
from .symbol_resolver import SymbolResolver
from .clients import twelve_data, fmp, alpha_vantage


class CloseResolver:
    def __init__(self, registry_file: str | Path, rate_limit_file: str | Path, run_date: str):
        self.symbol_resolver = SymbolResolver(registry_file)
        self.budget = BudgetManager(rate_limit_file)
        self.run_date = run_date
        self.cache = load_daily_cache(run_date)

    def _fetch_from_source(self, source: str, req: PriceRequest) -> PriceResult:
        if source == "twelve_data":
            return twelve_data.fetch_close(req.symbol, req.requested_close_date)
        if source == "fmp":
            return fmp.fetch_close(req.symbol, req.requested_close_date)
        if source == "alpha_vantage":
            return alpha_vantage.fetch_close(req.symbol, req.requested_close_date)
        return PriceResult(req.symbol, req.requested_close_date, None, None, None, source, None, None, "unresolved", "low", error="Source not yet implemented in starter branch")

    def resolve(self, req: PriceRequest) -> PriceResult:
        source_order = self.symbol_resolver.get_source_order(req.symbol, req.kind)

        for source in source_order:
            if source not in {"twelve_data", "fmp", "alpha_vantage"}:
                continue

            cached = cache_get(self.cache, req.symbol, req.requested_close_date, source)
            if cached:
                return PriceResult(**cached)

            if source in self.budget.budgets:
                if not self.budget.can_spend(source, req.kind):
                    continue
                self.budget.sleep_if_needed(source)

            result = self._fetch_from_source(source, req)

            if source in self.budget.budgets:
                self.budget.register_spend(source)

            cache_put(self.cache, result.to_dict())
            save_daily_cache(self.run_date, self.cache)

            if result.status in {"fresh_close", "fresh_fallback_source"}:
                return result

        return PriceResult(req.symbol, req.requested_close_date, None, None, None, None, None, None, "unresolved", "low", error="All configured API sources unresolved")
