from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


class MacroSourceError(RuntimeError):
    """Raised when a macro source cannot produce a valid, non-stale observation."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_date(value: Any) -> date:
    raw = str(value or "").strip()
    if not raw:
        raise MacroSourceError("Missing date value")
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw[:10] if fmt == "%Y-%m-%d" else raw, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise MacroSourceError(f"Could not parse date value: {raw!r}") from exc


def parse_float(value: Any) -> float:
    raw = str(value or "").replace(",", "").strip()
    if raw in {"", ".", "null", "None", "nan"}:
        raise MacroSourceError(f"Missing numeric value: {value!r}")
    try:
        return float(raw)
    except ValueError as exc:
        raise MacroSourceError(f"Could not parse numeric value: {value!r}") from exc


def staleness_days(as_of_date: str | date, reference_date: str | date) -> int:
    as_of = parse_date(as_of_date) if not isinstance(as_of_date, date) else as_of_date
    ref = parse_date(reference_date) if not isinstance(reference_date, date) else reference_date
    return (ref - as_of).days


def ensure_fresh(*, label: str, as_of_date: str, reference_date: str, max_staleness_days: int) -> int:
    age = staleness_days(as_of_date, reference_date)
    if age < 0:
        raise MacroSourceError(f"{label}: observation date {as_of_date} is after reference date {reference_date}")
    if age > max_staleness_days:
        raise MacroSourceError(
            f"{label}: stale observation as_of={as_of_date}, reference={reference_date}, "
            f"staleness_days={age}, max={max_staleness_days}"
        )
    return age


def _retry_pause(attempt: int, retry_sleep_seconds: float) -> None:
    if retry_sleep_seconds <= 0:
        return
    time.sleep(retry_sleep_seconds * attempt)


def fetch_text(
    url: str,
    *,
    timeout: int = 45,
    user_agent: str = "weekly-etf-macro-audit/1.0",
    max_attempts: int = 3,
    retry_sleep_seconds: float = 2.0,
) -> str:
    """Fetch text from an official/public macro source with bounded retries.

    Transient GitHub-runner/network read timeouts should not make the macro
    audit fragile. But after bounded retries, the function still fails loudly as
    MacroSourceError so stale/unavailable data never gets silently guessed.
    """
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    attempts = max(1, int(max_attempts))
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - configured official public data sources only
                raw = response.read()
                return raw.decode("utf-8")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt >= attempts:
                raise MacroSourceError(f"HTTP {exc.code} while fetching {url} after {attempt}/{attempts} attempts") from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt >= attempts:
                raise MacroSourceError(f"Network error while fetching {url} after {attempt}/{attempts} attempts: {exc.reason}") from exc
        except TimeoutError as exc:
            last_error = exc
            if attempt >= attempts:
                raise MacroSourceError(f"Read timeout while fetching {url} after {attempt}/{attempts} attempts") from exc
        except OSError as exc:
            last_error = exc
            if attempt >= attempts:
                raise MacroSourceError(f"OS/network error while fetching {url} after {attempt}/{attempts} attempts: {exc}") from exc
        _retry_pause(attempt, retry_sleep_seconds)
    raise MacroSourceError(f"Network fetch failed for {url}: {last_error}")


def fetch_json(url: str, *, timeout: int = 45, user_agent: str = "weekly-etf-macro-audit/1.0") -> dict[str, Any]:
    text = fetch_text(url, timeout=timeout, user_agent=user_agent)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise MacroSourceError(f"Invalid JSON from {url}: {exc}") from exc


def read_csv_rows(text: str) -> list[dict[str, str]]:
    return [dict(row) for row in csv.DictReader(StringIO(text))]


def build_url(base_url: str, params: dict[str, Any]) -> str:
    return base_url + "?" + urllib.parse.urlencode(params)


@dataclass(slots=True)
class MacroObservation:
    key: str
    value: float
    units: str
    source: str
    series_id: str
    label: str
    category: str
    as_of_date: str
    fetched_at_utc: str
    staleness_days: int
    max_staleness_days: int
    status: str = "fresh"
    source_url: str | None = None
    provider_metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["provider_metadata"] = payload.get("provider_metadata") or {}
        return payload


def load_fixture(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise MacroSourceError(f"Macro fixture does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
