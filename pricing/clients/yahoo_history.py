from __future__ import annotations

from ..models import PriceResult


def fetch_close(symbol: str, requested_close_date: str) -> PriceResult:
    return PriceResult(
        symbol=symbol,
        requested_close_date=requested_close_date,
        returned_close_date=None,
        price=None,
        currency=None,
        source="yahoo_history",
        source_detail=None,
        field_used=None,
        status="unresolved",
        confidence="low",
        error="Yahoo history fallback is scaffolded but not yet implemented in this starter branch.",
    )
