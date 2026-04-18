from __future__ import annotations

import os

from .base import http_get_json, q
from ..models import PriceResult

BASE = "https://www.alphavantage.co/query"


def fetch_close(symbol: str, requested_close_date: str) -> PriceResult:
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return PriceResult(symbol, requested_close_date, None, None, None, "alpha_vantage", None, None, "unresolved", "low", error="Missing ALPHA_VANTAGE_API_KEY")
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
            return PriceResult(symbol, requested_close_date, requested_close_date, float(row["4. close"]), "USD", "alpha_vantage", "TIME_SERIES_DAILY_ADJUSTED", "4. close", "fresh_close", "high")
        if series:
            dt = sorted(series.keys())[-1]
            row = series[dt]
            return PriceResult(symbol, requested_close_date, dt, float(row["4. close"]), "USD", "alpha_vantage", "TIME_SERIES_DAILY_ADJUSTED", "4. close", "fresh_fallback_source", "medium")
        return PriceResult(symbol, requested_close_date, None, None, None, "alpha_vantage", None, None, "unresolved", "low", error="No time series returned")
    except Exception as exc:
        return PriceResult(symbol, requested_close_date, None, None, None, "alpha_vantage", None, None, "unresolved", "low", error=str(exc))
