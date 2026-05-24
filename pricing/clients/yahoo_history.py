from __future__ import annotations

from datetime import datetime, timezone

from .base import http_get_json, q
from ..models import PriceResult

BASE = "https://query1.finance.yahoo.com/v8/finance/chart"


def _ts_to_date(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()


def fetch_close(symbol: str, requested_close_date: str, canonical_symbol: str | None = None, provider_exchange: str | None = None) -> PriceResult:
    canonical = canonical_symbol or symbol
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
                symbol=canonical,
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
                provider_symbol=symbol,
                provider_exchange=provider_exchange,
            )

        result0 = result[0]
        timestamps = result0.get("timestamp") or []
        quotes = ((result0.get("indicators") or {}).get("quote") or [{}])[0]
        closes = quotes.get("close") or []
        currency = (result0.get("meta") or {}).get("currency", "USD")
        exchange = provider_exchange or (result0.get("meta") or {}).get("exchangeName") or (result0.get("meta") or {}).get("fullExchangeName")

        pairs = []
        for ts, close in zip(timestamps, closes):
            if close is None:
                continue
            pairs.append((_ts_to_date(ts), float(close), int(ts)))

        if not pairs:
            return PriceResult(
                symbol=canonical,
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
                provider_symbol=symbol,
                provider_exchange=exchange,
            )

        pairs.sort(key=lambda item: item[0])
        for returned_date, price, ts in pairs:
            if returned_date == requested_close_date:
                return PriceResult(
                    symbol=canonical,
                    requested_close_date=requested_close_date,
                    returned_close_date=returned_date,
                    price=price,
                    currency=currency,
                    source="yahoo_history",
                    source_detail="query1_chart_v8",
                    field_used="close",
                    status="fresh_exact_unverified",
                    confidence="medium",
                    provider_symbol=symbol,
                    provider_exchange=exchange,
                    raw_close=price,
                    selected_close=price,
                    selected_close_type="raw_close",
                    provider_timestamp=datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
                    provider_timezone="UTC_timestamp_mapped_to_date",
                    is_final_eod_bar=True,
                    metadata={"provider": "yahoo_history", "endpoint": "query1_chart_v8"},
                )

        prior_pairs = [(dt, price, ts) for dt, price, ts in pairs if dt <= requested_close_date]
        if prior_pairs:
            returned_date, price, ts = prior_pairs[-1]
        else:
            returned_date, price, ts = pairs[-1]

        return PriceResult(
            symbol=canonical,
            requested_close_date=requested_close_date,
            returned_close_date=returned_date,
            price=price,
            currency=currency,
            source="yahoo_history",
            source_detail="query1_chart_v8",
            field_used="close",
            status="prior_valid_close",
            confidence="medium",
            provider_symbol=symbol,
            provider_exchange=exchange,
            raw_close=price,
            selected_close=price,
            selected_close_type="raw_close",
            provider_timestamp=datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            provider_timezone="UTC_timestamp_mapped_to_date",
            is_final_eod_bar=True,
            metadata={"provider": "yahoo_history", "endpoint": "query1_chart_v8"},
        )
    except Exception as exc:
        return PriceResult(
            symbol=canonical,
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
            provider_symbol=symbol,
            provider_exchange=provider_exchange,
        )
