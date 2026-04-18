from __future__ import annotations

import os

from .base import http_get_json
from ..models import PriceResult


def fetch_close(symbol: str, requested_close_date: str) -> PriceResult:
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        return PriceResult(symbol, requested_close_date, None, None, None, "fmp", None, None, "unresolved", "low", error="Missing FMP_API_KEY")

    urls = [
        f"https://financialmodelingprep.com/stable/historical-price-eod/full?symbol={symbol}&apikey={api_key}",
        f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={api_key}",
    ]
    for url in urls:
        try:
            data = http_get_json(url)
            rows = []
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                rows = data.get("historical") or data.get("data") or []
            for row in rows:
                dt = str(row.get("date", ""))[:10]
                if dt == requested_close_date:
                    price = row.get("close") or row.get("adjClose")
                    if price is not None:
                        return PriceResult(symbol, requested_close_date, dt, float(price), "USD", "fmp", url, "close", "fresh_close", "high")
            if rows:
                row = rows[0]
                dt = str(row.get("date", ""))[:10]
                price = row.get("close") or row.get("adjClose")
                if price is not None:
                    return PriceResult(symbol, requested_close_date, dt, float(price), "USD", "fmp", url, "close", "fresh_fallback_source", "medium")
        except Exception:
            continue
    return PriceResult(symbol, requested_close_date, None, None, None, "fmp", None, None, "unresolved", "low", error="No matching EOD result")
