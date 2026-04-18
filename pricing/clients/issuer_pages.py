from __future__ import annotations

import html
import re
from datetime import datetime

from .base import http_get_text
from ..models import PriceResult


HANDLER_URLS = {
    "ssga_spy": "https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy",
    "ssga_gld": "https://www.ssga.com/us/en/individual/etfs/spdr-gold-shares-gld",
    "vaneck_smh": "https://www.vaneck.com/us/en/investments/semiconductor-etf-smh/overview/",
    "globalx_pave": "https://www.globalxetfs.com/funds/pave/",
    "sprott_urnm": "https://sprottetfs.com/urnm-sprott-uranium-miners-etf/",
    "invesco_ppa": "https://www.invesco.com/us/financial-products/etfs/product-detail?audienceType=Investor&ticker=PPA",
}

DATE_FORMATS = [
    "%b %d %Y",
    "%B %d, %Y",
    "%m/%d/%Y",
]


def _normalize_text(raw_html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_date(date_text: str) -> str | None:
    cleaned = date_text.strip().replace(" ,", ",")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _extract_date(text: str) -> str | None:
    patterns = [
        r"As of ([A-Za-z]{3} \d{1,2} \d{4})",
        r"As of ([A-Za-z]+ \d{1,2}, \d{4})",
        r"Prices as of (\d{2}/\d{2}/\d{4})",
        r"as of (\d{2}/\d{2}/\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            parsed = _parse_date(match.group(1))
            if parsed:
                return parsed
    return None


def _extract_price(text: str, symbol: str, handler_name: str) -> float | None:
    if handler_name in {"ssga_spy", "ssga_gld"}:
        match = re.search(r"Closing Price[^$]{0,120}\$([0-9,]+\.\d+)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    if handler_name == "globalx_pave":
        match = re.search(r"Market Price[^$]{0,120}\$([0-9,]+\.\d+)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    if handler_name == "sprott_urnm":
        match = re.search(r"Market Price[^$]{0,120}\$([0-9,]+\.\d+)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    if handler_name == "invesco_ppa":
        match = re.search(r"Closing Price[^$]{0,120}\$([0-9,]+\.\d+)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    if handler_name == "vaneck_smh":
        match = re.search(rf"{re.escape(symbol)}\s+\$([0-9,]+\.\d+)\s+\$([0-9,]+\.\d+)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(2).replace(",", ""))
        match = re.search(r"Market\s*Price[^$]{0,120}\$([0-9,]+\.\d+)", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    return None


def fetch_close(symbol: str, requested_close_date: str, handler_name: str | None) -> PriceResult:
    if not handler_name or handler_name not in HANDLER_URLS:
        return PriceResult(
            symbol=symbol,
            requested_close_date=requested_close_date,
            returned_close_date=None,
            price=None,
            currency=None,
            source="issuer_override",
            source_detail=handler_name,
            field_used=None,
            status="unresolved",
            confidence="low",
            error="No issuer handler configured for symbol.",
        )

    url = HANDLER_URLS[handler_name]
    try:
        text = _normalize_text(http_get_text(url))
        returned_date = _extract_date(text)
        price = _extract_price(text, symbol, handler_name)
        if price is None or returned_date is None:
            return PriceResult(
                symbol=symbol,
                requested_close_date=requested_close_date,
                returned_close_date=returned_date,
                price=None,
                currency="USD",
                source="issuer_override",
                source_detail=handler_name,
                field_used=None,
                status="unresolved",
                confidence="low",
                error="Issuer page did not yield a dated close/market price.",
            )

        status = "fresh_close" if returned_date == requested_close_date else "fresh_fallback_source"
        confidence = "high" if handler_name in {"ssga_spy", "ssga_gld", "globalx_pave", "sprott_urnm", "invesco_ppa"} else "medium"
        return PriceResult(
            symbol=symbol,
            requested_close_date=requested_close_date,
            returned_close_date=returned_date,
            price=price,
            currency="USD",
            source="issuer_override",
            source_detail=handler_name,
            field_used="closing_price" if handler_name in {"ssga_spy", "ssga_gld", "invesco_ppa"} else "market_price",
            status=status,
            confidence=confidence,
        )
    except Exception as exc:
        return PriceResult(
            symbol=symbol,
            requested_close_date=requested_close_date,
            returned_close_date=None,
            price=None,
            currency=None,
            source="issuer_override",
            source_detail=handler_name,
            field_used=None,
            status="unresolved",
            confidence="low",
            error=str(exc),
        )
