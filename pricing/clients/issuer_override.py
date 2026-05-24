from __future__ import annotations

from ..models import PriceResult
from . import yahoo_history


ISSUER_DETAIL = {
    "ssga_spy": "issuer_override:ssga_spy",
    "ssga_gld": "issuer_override:ssga_gld",
    "vaneck_smh": "issuer_override:vaneck_smh",
    "globalx_pave": "issuer_override:globalx_pave",
    "sprott_urnm": "issuer_override:sprott_urnm",
    "invesco_ppa": "issuer_override:invesco_ppa",
}


def fetch_close(
    symbol: str,
    requested_close_date: str,
    handler: str | None = None,
    canonical_symbol: str | None = None,
    provider_exchange: str | None = None,
) -> PriceResult:
    """Last-resort issuer override hook for known ETF holdings.

    This layer is intentionally last in the holding source order. It is not a
    live issuer scraper yet; until issuer-native scrapers exist it delegates to
    the no-key Yahoo history fallback and keeps the delegated source visible in
    metadata. The registry-level source name remains issuer_override only to
    prove this last-resort hook was used.
    """
    canonical = canonical_symbol or symbol
    if not handler:
        return PriceResult(canonical, requested_close_date, None, None, None, "issuer_override", None, None, "unresolved", "low", error="No issuer handler configured", provider_symbol=symbol, provider_exchange=provider_exchange)

    result = yahoo_history.fetch_close(symbol, requested_close_date, canonical_symbol=canonical, provider_exchange=provider_exchange)
    detail = ISSUER_DETAIL.get(handler, f"issuer_override:{handler}")
    if result.status in {"fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}:
        result.source = "issuer_override"
        result.source_detail = f"{detail}:delegated_yahoo_history"
        result.metadata = {**result.metadata, "handler": handler, "delegated_source": "yahoo_history", "last_resort": True}
        if result.confidence == "high":
            result.confidence = "medium"
        return result

    return PriceResult(
        canonical,
        requested_close_date,
        result.returned_close_date,
        result.price,
        result.currency,
        "issuer_override",
        f"{detail}:delegated_yahoo_history",
        result.field_used,
        "unresolved",
        "low",
        error=result.error or "Issuer override fallback unresolved",
        metadata={"handler": handler, "delegated_source": "yahoo_history", "last_resort": True},
        provider_symbol=symbol,
        provider_exchange=provider_exchange,
        raw_close=result.raw_close,
        adjusted_close=result.adjusted_close,
        selected_close=result.selected_close,
        selected_close_type=result.selected_close_type,
        provider_timestamp=result.provider_timestamp,
        provider_timezone=result.provider_timezone,
        is_final_eod_bar=result.is_final_eod_bar,
    )
