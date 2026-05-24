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


def fetch_close(symbol: str, requested_close_date: str, handler: str | None = None) -> PriceResult:
    """Last-resort issuer override hook for known ETF holdings.

    This layer is intentionally last in the holding source order. It is not a
    live issuer scraper yet; until issuer-native scrapers exist it delegates to
    the no-key Yahoo history fallback and keeps the delegated source visible in
    metadata. The registry-level source name remains issuer_override only to
    prove this last-resort hook was used.
    """
    if not handler:
        return PriceResult(symbol, requested_close_date, None, None, None, "issuer_override", None, None, "unresolved", "low", error="No issuer handler configured")

    result = yahoo_history.fetch_close(symbol, requested_close_date)
    detail = ISSUER_DETAIL.get(handler, f"issuer_override:{handler}")
    if result.status in {"fresh_close", "fresh_fallback_source"}:
        result.source = "issuer_override"
        result.source_detail = f"{detail}:delegated_yahoo_history"
        result.metadata = {**result.metadata, "handler": handler, "delegated_source": "yahoo_history", "last_resort": True}
        if result.confidence == "high":
            result.confidence = "medium"
        return result

    return PriceResult(
        symbol,
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
    )
