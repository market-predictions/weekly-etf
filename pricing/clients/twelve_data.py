from __future__ import annotations

import os

from .base import http_get_json, q
from ..models import PriceResult, FXResult

BASE = "https://api.twelvedata.com"


def fetch_close(symbol: str, requested_close_date: str) -> PriceResult:
    api_key = os.environ.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return PriceResult(symbol, requested_close_date, None, None, None, "twelve_data", None, None, "unresolved", "low", error="Missing TWELVE_DATA_API_KEY")

    try:
        url = f"{BASE}/time_series?" + q({
            "symbol": symbol,
            "interval": "1day",
            "outputsize": 5,
            "format": "JSON",
            "apikey": api_key,
        })
        data = http_get_json(url)
        values = data.get("values") or []
        for row in values:
            dt = str(row.get("datetime", ""))[:10]
            if dt == requested_close_date:
                return PriceResult(symbol, requested_close_date, dt, float(row["close"]), data.get("meta", {}).get("currency", "USD"), "twelve_data", "time_series", "close", "fresh_close", "high")
        if values:
            row = values[0]
            dt = str(row.get("datetime", ""))[:10]
            return PriceResult(symbol, requested_close_date, dt, float(row["close"]), data.get("meta", {}).get("currency", "USD"), "twelve_data", "time_series_latest", "close", "fresh_fallback_source", "medium")
        return PriceResult(symbol, requested_close_date, None, None, None, "twelve_data", None, None, "unresolved", "low", error="No values returned")
    except Exception as exc:
        return PriceResult(symbol, requested_close_date, None, None, None, "twelve_data", None, None, "unresolved", "low", error=str(exc))


def fetch_eurusd(requested_date: str) -> FXResult:
    api_key = os.environ.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return FXResult("EUR/USD", requested_date, None, None, "twelve_data", "unresolved", error="Missing TWELVE_DATA_API_KEY")

    try:
        url = f"{BASE}/time_series?" + q({
            "symbol": "EUR/USD",
            "interval": "1day",
            "outputsize": 5,
            "format": "JSON",
            "apikey": api_key,
        })
        data = http_get_json(url)
        values = data.get("values") or []
        for row in values:
            dt = str(row.get("datetime", ""))[:10]
            if dt == requested_date:
                return FXResult("EUR/USD", requested_date, dt, float(row["close"]), "twelve_data", "fresh_close")
        if values:
            row = values[0]
            dt = str(row.get("datetime", ""))[:10]
            return FXResult("EUR/USD", requested_date, dt, float(row["close"]), "twelve_data", "fresh_fallback_source")
        return FXResult("EUR/USD", requested_date, None, None, "twelve_data", "unresolved", error="No values returned")
    except Exception as exc:
        return FXResult("EUR/USD", requested_date, None, None, "twelve_data", "unresolved", error=str(exc))
