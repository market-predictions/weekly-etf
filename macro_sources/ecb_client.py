from __future__ import annotations

from typing import Any

from macro_sources.common import MacroObservation, MacroSourceError, build_url, ensure_fresh, fetch_text, parse_float, read_csv_rows, utc_now_iso


def fetch_ecb_series(config: dict[str, Any], *, reference_date: str) -> list[MacroObservation]:
    ecb_cfg = config.get("ecb") or {}
    if not ecb_cfg.get("enabled", True):
        return []
    base_url = str(ecb_cfg.get("base_url") or "https://data-api.ecb.europa.eu/service/data").rstrip("/")
    defaults = config.get("defaults") or {}
    timeout = int(defaults.get("request_timeout_seconds", 25))
    user_agent = str(defaults.get("user_agent") or "weekly-etf-macro-audit/1.0")

    observations: list[MacroObservation] = []
    for series in ecb_cfg.get("series", []) or []:
        flow = str(series.get("flow") or "").strip()
        key_path = str(series.get("key_path") or "").strip()
        key = str(series.get("key") or key_path).strip()
        if not flow or not key_path or not key:
            raise MacroSourceError(f"Invalid ECB series configuration: {series!r}")
        url = build_url(f"{base_url}/{flow}/{key_path}", {"lastNObservations": 10, "format": "csvdata"})
        rows = read_csv_rows(fetch_text(url, timeout=timeout, user_agent=user_agent))
        latest_row = None
        for row in reversed(rows):
            try:
                parse_float(row.get("OBS_VALUE"))
            except MacroSourceError:
                continue
            if row.get("TIME_PERIOD"):
                latest_row = row
                break
        if latest_row is None:
            raise MacroSourceError(f"ECB {flow}/{key_path}: no valid observations returned")
        as_of_date = str(latest_row.get("TIME_PERIOD"))
        value = parse_float(latest_row.get("OBS_VALUE"))
        max_staleness = int(series.get("max_staleness_days", 7))
        age = ensure_fresh(label=f"ECB {flow}/{key_path}", as_of_date=as_of_date, reference_date=reference_date, max_staleness_days=max_staleness)
        observations.append(
            MacroObservation(
                key=key,
                value=value,
                units=str(series.get("units") or "value"),
                source="ecb",
                series_id=str(series.get("series_id") or f"{flow}/{key_path}"),
                label=str(series.get("label") or f"{flow}/{key_path}"),
                category=str(series.get("category") or "macro"),
                as_of_date=as_of_date,
                fetched_at_utc=utc_now_iso(),
                staleness_days=age,
                max_staleness_days=max_staleness,
                source_url=url,
                provider_metadata={"flow": flow, "key_path": key_path, "frequency": series.get("frequency")},
            )
        )
    return observations
