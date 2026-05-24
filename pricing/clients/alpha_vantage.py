from __future__ import annotations

import os

from .base import http_get_json, q
from ..models import PriceResult

BASE = "https://www.alphavantage.co/query"


def fetch_close(symbol: str, requested_close_date: str, canonical_symbol: str | None = None, provider_exchange: str | None = None) -> PriceResult:
    canonical = canonical_symbol or symbol
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return PriceResult(canonical, requested_close_date, None, None, None, "alpha_vantage", None, None, "unresolved", "low", error="Missing ALPHA_VANTAGE_API_KEY", provider_symbol=symbol, provider_exchange=provider_exchange)
    try:
        url = BASE + "?" + q({
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": api_key,
        })
        data = http_get_json(url)
        series = data.get("Time Series (Daily)") or {}
        if requested_close_date in series:
            row = series[requested_close_date]
            raw_close = float(row["4. close"])
            adj_close = float(row["5. adjusted close"]) if row.get("5. adjusted close") is not None else None
            return PriceResult(canonical, requested_close_date, requested_close_date, raw_close, "USD", "alpha_vantage", "TIME_SERIES_DAILY_ADJUSTED", "4. close", "fresh_exact_unverified", "high", provider_symbol=symbol, provider_exchange=provider_exchange, raw_close=raw_close, adjusted_close=adj_close, selected_close=raw_close, selected_close_type="raw_close", provider_timezone="provider_daily_bar", is_final_eod_bar=True, metadata={"provider": "alpha_vantage", "endpoint": "TIME_SERIES_DAILY_ADJUSTED"})
        if series:
            dt = sorted(series.keys())[-1]
            row = series[dt]
            raw_close = float(row["4. close"])
            adj_close = float(row["5. adjusted close"]) if row.get("5. adjusted close") is not None else None
            return PriceResult(canonical, requested_close_date, dt, raw_close, "USD", "alpha_vantage", "TIME_SERIES_DAILY_ADJUSTED", "4. close", "prior_valid_close", "medium", provider_symbol=symbol, provider_exchange=provider_exchange, raw_close=raw_close, adjusted_close=adj_close, selected_close=raw_close, selected_close_type="raw_close", provider_timezone="provider_daily_bar", is_final_eod_bar=True, metadata={"provider": "alpha_vantage", "endpoint": "TIME_SERIES_DAILY_ADJUSTED"})
        return PriceResult(canonical, requested_close_date, None, None, None, "alpha_vantage", None, None, "unresolved", "low", error="No time series returned", provider_symbol=symbol, provider_exchange=provider_exchange)
    except Exception as exc:
        return PriceResult(canonical, requested_close_date, None, None, None, "alpha_vantage", None, None, "unresolved", "low", error=str(exc), provider_symbol=symbol, provider_exchange=provider_exchange)
