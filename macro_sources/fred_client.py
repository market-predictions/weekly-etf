from __future__ import annotations

from typing import Any

from macro_sources.common import MacroObservation, MacroSourceError, build_url, ensure_fresh, fetch_text, parse_float, read_csv_rows, utc_now_iso


def fetch_fred_series(config: dict[str, Any], *, reference_date: str) -> list[MacroObservation]:
    fred_cfg = config.get("fred") or {}
    if not fred_cfg.get("enabled", True):
        return []
    base_url = str(fred_cfg.get("base_url") or "https://fred.stlouisfed.org/graph/fredgraph.csv")
    defaults = config.get("defaults") or {}
    timeout = int(defaults.get("request_timeout_seconds", 25))
    user_agent = str(defaults.get("user_agent") or "weekly-etf-macro-audit/1.0")

    observations: list[MacroObservation] = []
    for series in fred_cfg.get("series", []) or []:
        series_id = str(series.get("series_id") or "").strip()
        key = str(series.get("key") or series_id).strip()
        if not series_id or not key:
            raise MacroSourceError(f"Invalid FRED series configuration: {series!r}")
        url = build_url(base_url, {"id": series_id})
        rows = read_csv_rows(fetch_text(url, timeout=timeout, user_agent=user_agent))
        value_col = series_id
        latest_row = None
        for row in reversed(rows):
            raw_value = row.get(value_col) or row.get(series_id.upper()) or row.get(series_id.lower())
            try:
                parse_float(raw_value)
            except MacroSourceError:
                continue
            if row.get("observation_date") or row.get("DATE") or row.get("date"):
                latest_row = row
                break
        if latest_row is None:
            raise MacroSourceError(f"FRED {series_id}: no valid observations returned")
        as_of_date = str(latest_row.get("observation_date") or latest_row.get("DATE") or latest_row.get("date"))
        value = parse_float(latest_row.get(value_col) or latest_row.get(series_id.upper()) or latest_row.get(series_id.lower()))
        max_staleness = int(series.get("max_staleness_days", 7))
        age = ensure_fresh(label=f"FRED {series_id}", as_of_date=as_of_date, reference_date=reference_date, max_staleness_days=max_staleness)
        observations.append(
            MacroObservation(
                key=key,
                value=value,
                units=str(series.get("units") or "value"),
                source="fred",
                series_id=series_id,
                label=str(series.get("label") or series_id),
                category=str(series.get("category") or "macro"),
                as_of_date=as_of_date,
                fetched_at_utc=utc_now_iso(),
                staleness_days=age,
                max_staleness_days=max_staleness,
                source_url=url,
                provider_metadata={"frequency": series.get("frequency")},
            )
        )
    return observations
