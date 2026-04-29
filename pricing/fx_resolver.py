from __future__ import annotations

from .clients import twelve_data, ecb_reference
from .models import FXResult


def resolve_fx(requested_date: str) -> FXResult:
    """Resolve EUR/USD through the configured FX hierarchy.

    Twelve Data remains the preferred market close source when the key is
    available. ECB is a no-key reference-rate fallback so USD/EUR valuation does
    not become unresolved merely because one API key is unavailable.
    """
    primary = twelve_data.fetch_eurusd(requested_date)
    if primary.status in {"fresh_close", "fresh_fallback_source"} and primary.rate is not None:
        return primary

    fallback = ecb_reference.fetch_eurusd(requested_date)
    if fallback.status in {"fresh_close", "fresh_fallback_source"} and fallback.rate is not None:
        fallback.metadata = {**fallback.metadata, "primary_error": primary.error, "primary_source": primary.source}
        return fallback

    return FXResult(
        "EUR/USD",
        requested_date,
        None,
        None,
        "fx_hierarchy",
        "unresolved",
        error=f"twelve_data={primary.error}; ecb_reference={fallback.error}",
    )
