from __future__ import annotations

from datetime import datetime, timezone

from .base import http_get_json, q
from ..models import PriceResult

BASE = "https://query1.finance.yahoo.com/v8/finance/chart"


def _ts_to_date(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()


def fetch_close(symbol: str, requested_close_date: str) -> PriceResult:
    url = f"{BASE}/{symbol}?" + q({
        "range": "3mo",
        "interval": "1d",
        "includePrePost": "false",
        "events": "div,splits",
    })

    try:
        data = http_get_json(url)
        result = (data.get("chart") or {}).get("result") or []
        if not result:
            return PriceResult(
                symbol=symbol,
                requested_close_date=requested_close_date,
                returned_close_date=None,
                price=None,
                currency=None,
                source="yahoo_history",
                source_detail="query1_chart_v8",
                field_used=None,
                status="unresolved",
                confidence="low",
                error="Yahoo chart endpoint returned no result.",
            )

        result0 = result[0]
        timestamps = result0.get("timestamp") or []
        quotes = ((result0.get("indicators") or {}).get("quote") or [{}])[0]
        closes = quotes.get("close") or []
        currency = (result0.get("meta") or {}).get("currency", "USD")

        pairs = []
        for ts, close in zip(timestamps, closes):
            if close is None:
                continue
            pairs.append((_ts_to_date(ts), float(close)))

        if not pairs:
            return PriceResult(
                symbol=symbol,
                requested_close_date=requested_close_date,
                returned_close_date=None,
                price=None,
                currency=currency,
                source="yahoo_history",
                source_detail="query1_chart_v8",
                field_used=None,
                status="unresolved",
                confidence="low",
                error="Yahoo chart endpoint returned no valid close values.",
            )

        for returned_date, price in pairs:
            if returned_date == requested_close_date:
                return PriceResult(
                    symbol=symbol,
                    requested_close_date=requested_close_date,
                    returned_close_date=returned_date,
                    price=price,
                    currency=currency,
                    source="yahoo_history",
                    source_detail="query1_chart_v8",
                    field_used="close",
                    status="fresh_close",
                    confidence="medium",
                )

        returned_date, price = pairs[0]
        return PriceResult(
            symbol=symbol,
            requested_close_date=requested_close_date,
            returned_close_date=returned_date,
            price=price,
            currency=currency,
            source="yahoo_history",
            source_detail="query1_chart_v8",
            field_used="close",
            status="fresh_fallback_source",
            confidence="low",
        )
    except Exception as exc:
        return PriceResult(
            symbol=symbol,
            requested_close_date=requested_close_date,
            returned_close_date=None,
            price=None,
            currency=None,
            source="yahoo_history",
            source_detail="query1_chart_v8",
            field_used=None,
            status="unresolved",
            confidence="low",
            error=str(exc),
        )
