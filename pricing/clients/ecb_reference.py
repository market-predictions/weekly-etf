from __future__ import annotations

from datetime import datetime, timezone
from xml.etree import ElementTree as ET

from .base import http_get_text
from ..models import FXResult

ECB_DAILY_XML = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


def fetch_eurusd(requested_date: str) -> FXResult:
    """Fetch the ECB EUR/USD reference rate as a no-key FX fallback.

    ECB publishes USD per 1 EUR. That matches the report's EUR/USD convention.
    The daily endpoint may return the latest available ECB business-day fixing,
    so it is treated as fresh_fallback_source unless the date matches exactly.
    """
    try:
        text = http_get_text(ECB_DAILY_XML)
        root = ET.fromstring(text)
        cube_time = None
        usd_rate = None
        for elem in root.iter():
            attrs = elem.attrib
            if "time" in attrs:
                cube_time = attrs.get("time")
            if attrs.get("currency") == "USD" and "rate" in attrs:
                usd_rate = float(attrs["rate"])
                break

        if usd_rate is None:
            return FXResult("EUR/USD", requested_date, None, None, "ecb_reference", "unresolved", error="ECB daily XML did not contain USD rate")

        returned_date = cube_time or datetime.now(timezone.utc).date().isoformat()
        status = "fresh_close" if returned_date == requested_date else "fresh_fallback_source"
        return FXResult("EUR/USD", requested_date, returned_date, usd_rate, "ecb_reference", status)
    except Exception as exc:
        return FXResult("EUR/USD", requested_date, None, None, "ecb_reference", "unresolved", error=str(exc))
