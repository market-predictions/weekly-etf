from __future__ import annotations

from ..models import PriceResult


def fetch_close(symbol: str, requested_close_date: str, handler_name: str | None) -> PriceResult:
    return PriceResult(
        symbol=symbol,
        requested_close_date=requested_close_date,
        returned_close_date=None,
        price=None,
        currency=None,
        source="issuer_override",
        source_detail=handler_name,
        field_used=None,
        status="unresolved",
        confidence="low",
        error="Issuer-page handlers are scaffolded but not yet implemented in this starter branch.",
    )
