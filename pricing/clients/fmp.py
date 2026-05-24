from __future__ import annotations

import os

from .base import http_get_json
from ..models import PriceResult


def fetch_close(symbol: str, requested_close_date: str, canonical_symbol: str | None = None, provider_exchange: str | None = None) -> PriceResult:
    canonical = canonical_symbol or symbol
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        return PriceResult(canonical, requested_close_date, None, None, None, "fmp", None, None, "unresolved", "low", error="Missing FMP_API_KEY", provider_symbol=symbol, provider_exchange=provider_exchange)

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
                    raw_price = row.get("close")
                    adj_price = row.get("adjClose")
                    price = raw_price if raw_price is not None else adj_price
                    if price is not None:
                        price_f = float(price)
                        return PriceResult(canonical, requested_close_date, dt, price_f, "USD", "fmp", url, "close" if raw_price is not None else "adjClose", "fresh_exact_unverified", "high", provider_symbol=symbol, provider_exchange=provider_exchange, raw_close=None if raw_price is None else float(raw_price), adjusted_close=None if adj_price is None else float(adj_price), selected_close=price_f, selected_close_type="raw_close" if raw_price is not None else "adjusted_close", provider_timezone="provider_daily_bar", is_final_eod_bar=True, metadata={"provider": "fmp", "endpoint": url})
            if rows:
                row = rows[0]
                dt = str(row.get("date", ""))[:10]
                raw_price = row.get("close")
                adj_price = row.get("adjClose")
                price = raw_price if raw_price is not None else adj_price
                if price is not None:
                    price_f = float(price)
                    return PriceResult(canonical, requested_close_date, dt, price_f, "USD", "fmp", url, "close" if raw_price is not None else "adjClose", "prior_valid_close", "medium", provider_symbol=symbol, provider_exchange=provider_exchange, raw_close=None if raw_price is None else float(raw_price), adjusted_close=None if adj_price is None else float(adj_price), selected_close=price_f, selected_close_type="raw_close" if raw_price is not None else "adjusted_close", provider_timezone="provider_daily_bar", is_final_eod_bar=True, metadata={"provider": "fmp", "endpoint": url})
        except Exception:
            continue
    return PriceResult(canonical, requested_close_date, None, None, None, "fmp", None, None, "unresolved", "low", error="No matching EOD result", provider_symbol=symbol, provider_exchange=provider_exchange)
