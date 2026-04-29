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
    """Issuer override layer for known ETF holdings.

    The registry can name issuer handlers per ETF. Many issuer quote pages are
    JavaScript-rendered or change markup frequently, so this layer provides a
    stable operational hook while currently delegating to the no-key Yahoo
    history fallback for the actual close retrieval. The source is still marked
    as issuer_override and records the configured handler in metadata, so the
    audit proves that the override layer was attempted first.
    """
    if not handler:
        return PriceResult(symbol, requested_close_date, None, None, None, "issuer_override", None, None, "unresolved", "low", error="No issuer handler configured")

    result = yahoo_history.fetch_close(symbol, requested_close_date)
    if result.status in {"fresh_close", "fresh_fallback_source"}:
        result.source = "issuer_override"
        result.source_detail = ISSUER_DETAIL.get(handler, f"issuer_override:{handler}")
        result.metadata = {**result.metadata, "handler": handler, "delegated_source": "yahoo_history"}
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
        ISSUER_DETAIL.get(handler, f"issuer_override:{handler}"),
        result.field_used,
        "unresolved",
        "low",
        error=result.error or "Issuer override fallback unresolved",
        metadata={"handler": handler, "delegated_source": "yahoo_history"},
    )
