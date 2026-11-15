"""Free end-of-day price sources for Weekly ETF EU v2.

Each fetcher returns a SourceResult with daily closes keyed by ISO date plus the
identity metadata the source reports. Fetchers never raise for data problems;
they record the problem in `error` so callers can decide.
"""
from __future__ import annotations

import csv
import io
import os
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import requests

UA = {"User-Agent": "Mozilla/5.0 (weekly-etf v2)"}
TIMEOUT = 30

# Exchange code mapping per source.
SUFFIX = {
    "Xetra": {"yahoo": ".DE", "alpha_vantage": ".DEX", "eodhd": ".XETRA", "stooq": ".de", "twelve_data": "XETR"},
    "US": {"yahoo": "", "alpha_vantage": "", "eodhd": ".US", "stooq": ".us", "twelve_data": ""},
    "Euronext Amsterdam": {"yahoo": ".AS", "alpha_vantage": ".AMS", "eodhd": ".AS", "stooq": ".nl", "twelve_data": "Euronext"},
}


@dataclass
class SourceResult:
    source: str
    symbol: str
    closes: dict[str, float] = field(default_factory=dict)
    currency: str | None = None
    exchange: str | None = None
    name: str | None = None
    error: str | None = None

    @property
    def last_date(self) -> str | None:
        return max(self.closes) if self.closes else None


def symbol_for(source: str, ticker: str, exchange: str) -> str:
    code = SUFFIX.get(exchange, {}).get(source)
    if code is None:
        return ""
    if source == "twelve_data":
        return ticker
    if source == "stooq":
        return ticker.lower() + code
    return ticker + code


def _get(url: str, **params) -> requests.Response:
    return requests.get(url, params=params, headers=UA, timeout=TIMEOUT)


def yahoo(ticker: str, exchange: str, start: date, end: date) -> SourceResult:
    return yahoo_symbol(symbol_for("yahoo", ticker, exchange), start, end)


def yahoo_symbol(sym: str, start: date, end: date) -> SourceResult:
    """Daily closes for a raw Yahoo symbol (e.g. SPY, SXR8.DE, EURUSD=X)."""
    res = SourceResult("yahoo", sym)
    p1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
    p2 = int(datetime(end.year, end.month, end.day, 23, 59, tzinfo=timezone.utc).timestamp())
    last_exc = None
    for host in ("query1", "query2"):
        try:
            r = _get(f"https://{host}.finance.yahoo.com/v8/finance/chart/{sym}", period1=p1, period2=p2, interval="1d")
            if r.status_code != 200:
                last_exc = f"http_{r.status_code}"
                continue
            chart = (r.json().get("chart") or {}).get("result") or []
            if not chart:
                last_exc = "no_result"
                continue
            c = chart[0]
            meta = c.get("meta") or {}
            res.currency = meta.get("currency")
            res.exchange = meta.get("exchangeName")
            res.name = meta.get("longName") or meta.get("shortName")
            ts = c.get("timestamp") or []
            closes = ((c.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
            tz_offset = int(meta.get("gmtoffset") or 0)
            for t, v in zip(ts, closes):
                if v is None:
                    continue
                d = datetime.fromtimestamp(t + tz_offset, tz=timezone.utc).date().isoformat()
                res.closes[d] = float(v)
            return res
        except Exception as exc:  # network / parse
            last_exc = type(exc).__name__
    res.error = last_exc
    return res


def yahoo_isin_symbols(isin: str) -> list[dict]:
    """Yahoo search by ISIN -> list of {symbol, exchange} it maps to."""
    try:
        r = _get("https://query2.finance.yahoo.com/v1/finance/search", q=isin, quotesCount=20, newsCount=0)
        if r.status_code != 200:
            return []
        return [{"symbol": q.get("symbol"), "exchange": q.get("exchange"), "name": q.get("longname") or q.get("shortname")}
                for q in r.json().get("quotes") or []]
    except Exception:
        return []


def alpha_vantage(ticker: str, exchange: str) -> SourceResult:
    sym = symbol_for("alpha_vantage", ticker, exchange)
    res = SourceResult("alpha_vantage", sym)
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not key:
        res.error = "no_key"
        return res
    try:
        r = _get("https://www.alphavantage.co/query", function="TIME_SERIES_DAILY", symbol=sym, outputsize="compact", apikey=key)
        data = r.json()
        series = data.get("Time Series (Daily)")
        if not series:
            msg = " ".join(str(v) for v in data.values())[:80].lower()
            res.error = "rate_limited" if ("rate" in msg or "frequency" in msg or "limit" in msg) else "no_data"
            return res
        res.closes = {d: float(v["4. close"]) for d, v in series.items()}
        res.currency = "EUR"  # AV does not report currency in this endpoint
    except Exception as exc:
        res.error = type(exc).__name__
    return res


def eodhd(ticker: str, exchange: str, start: date) -> SourceResult:
    sym = symbol_for("eodhd", ticker, exchange)
    res = SourceResult("eodhd", sym)
    key = os.environ.get("EODHD_API_TOKEN")
    if not key:
        res.error = "no_key"
        return res
    try:
        r = _get(f"https://eodhd.com/api/eod/{sym}", api_token=key, fmt="json", **{"from": start.isoformat()})
        if r.status_code != 200:
            res.error = f"http_{r.status_code}"
            return res
        rows = r.json()
        if not isinstance(rows, list) or not rows:
            res.error = "no_data"
            return res
        res.closes = {row["date"]: float(row["close"]) for row in rows if row.get("close") is not None}
    except Exception as exc:
        res.error = type(exc).__name__
    return res


def twelve_data(ticker: str, exchange: str, start: date) -> SourceResult:
    ex = SUFFIX.get(exchange, {}).get("twelve_data")
    res = SourceResult("twelve_data", f"{ticker}:{ex}")
    key = os.environ.get("TWELVE_DATA_API_KEY") or os.environ.get("TWELVEDATA_API_KEY")
    if not key:
        res.error = "no_key"
        return res
    try:
        r = _get("https://api.twelvedata.com/time_series", symbol=ticker, exchange=ex, interval="1day",
                 start_date=start.isoformat(), apikey=key)
        data = r.json()
        if data.get("status") != "ok":
            res.error = ("rate_limited" if data.get("code") == 429 else f"err_{data.get('code')}")
            return res
        meta = data.get("meta") or {}
        res.currency = meta.get("currency")
        res.exchange = meta.get("exchange")
        res.closes = {v["datetime"][:10]: float(v["close"]) for v in data.get("values") or []}
    except Exception as exc:
        res.error = type(exc).__name__
    return res


def stooq(ticker: str, exchange: str, start: date) -> SourceResult:
    sym = symbol_for("stooq", ticker, exchange)
    res = SourceResult("stooq", sym)
    params = {"s": sym, "i": "d", "d1": start.strftime("%Y%m%d")}
    if os.environ.get("STOOQ_API_KEY"):
        params["apikey"] = os.environ["STOOQ_API_KEY"]
    try:
        r = _get("https://stooq.com/q/d/l/", **params)
        text = r.text.strip()
        if r.status_code != 200 or not text.lower().startswith("date"):
            res.error = f"http_{r.status_code}" if r.status_code != 200 else "no_data"
            return res
        for row in csv.DictReader(io.StringIO(text)):
            if row.get("Close") not in (None, "", "N/D"):
                res.closes[row["Date"]] = float(row["Close"])
        if not res.closes:
            res.error = "no_data"
    except Exception as exc:
        res.error = type(exc).__name__
    return res


def pause(seconds: float) -> None:
    time.sleep(seconds)
