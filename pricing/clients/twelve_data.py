from __future__ import annotations

import os

from .base import http_get_json, q
from ..models import PriceResult, FXResult

BASE = "https://api.twelvedata.com"


def fetch_close(symbol: str, requested_close_date: str, canonical_symbol: str | None = None, provider_exchange: str | None = None) -> PriceResult:
    canonical = canonical_symbol or symbol
    api_key = os.environ.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return PriceResult(canonical, requested_close_date, None, None, None, "twelve_data", None, None, "unresolved", "low", error="Missing TWELVE_DATA_API_KEY", provider_symbol=symbol, provider_exchange=provider_exchange)

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
        meta = data.get("meta", {}) or {}
        currency = meta.get("currency", "USD")
        exchange = provider_exchange or meta.get("exchange") or meta.get("mic_code")
        for row in values:
            dt = str(row.get("datetime", ""))[:10]
            if dt == requested_close_date:
                price = float(row["close"])
                return PriceResult(canonical, requested_close_date, dt, price, currency, "twelve_data", "time_series", "close", "fresh_exact_unverified", "high", provider_symbol=symbol, provider_exchange=exchange, raw_close=price, selected_close=price, selected_close_type="raw_close", provider_timezone="provider_daily_bar", is_final_eod_bar=True, metadata={"provider": "twelve_data", "endpoint": "time_series"})
        if values:
            row = values[0]
            dt = str(row.get("datetime", ""))[:10]
            price = float(row["close"])
            return PriceResult(canonical, requested_close_date, dt, price, currency, "twelve_data", "time_series_latest", "close", "prior_valid_close", "medium", provider_symbol=symbol, provider_exchange=exchange, raw_close=price, selected_close=price, selected_close_type="raw_close", provider_timezone="provider_daily_bar", is_final_eod_bar=True, metadata={"provider": "twelve_data", "endpoint": "time_series"})
        return PriceResult(canonical, requested_close_date, None, None, None, "twelve_data", None, None, "unresolved", "low", error="No values returned", provider_symbol=symbol, provider_exchange=exchange)
    except Exception as exc:
        return PriceResult(canonical, requested_close_date, None, None, None, "twelve_data", None, None, "unresolved", "low", error=str(exc), provider_symbol=symbol, provider_exchange=provider_exchange)


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
                return FXResult("EUR/USD", requested_date, dt, float(row["close"]), "twelve_data", "fresh_exact_unverified")
        if values:
            row = values[0]
            dt = str(row.get("datetime", ""))[:10]
            return FXResult("EUR/USD", requested_date, dt, float(row["close"]), "twelve_data", "prior_valid_close")
        return FXResult("EUR/USD", requested_date, None, None, "twelve_data", "unresolved", error="No values returned")
    except Exception as exc:
        return FXResult("EUR/USD", requested_date, None, None, "twelve_data", "unresolved", error=str(exc))
