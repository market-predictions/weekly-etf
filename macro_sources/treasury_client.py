from __future__ import annotations

from typing import Any

from macro_sources.common import MacroObservation, MacroSourceError, build_url, ensure_fresh, fetch_json, parse_float, utc_now_iso


def fetch_treasury_series(config: dict[str, Any], *, reference_date: str) -> list[MacroObservation]:
    treasury_cfg = config.get("treasury") or {}
    if not treasury_cfg.get("enabled", True):
        return []
    endpoint = str(treasury_cfg.get("endpoint") or "").strip()
    if not endpoint:
        raise MacroSourceError("Treasury endpoint is missing from config")
    defaults = config.get("defaults") or {}
    timeout = int(defaults.get("request_timeout_seconds", 25))
    user_agent = str(defaults.get("user_agent") or "weekly-etf-macro-audit/1.0")
    record_date_field = str(treasury_cfg.get("record_date_field") or "record_date")
    fields = treasury_cfg.get("fields", []) or []
    field_names = ",".join([record_date_field] + [str(field.get("field")) for field in fields if field.get("field")])
    url = build_url(endpoint, {"sort": f"-{record_date_field}", "page[size]": 1, "fields": field_names, "format": "json"})
    payload = fetch_json(url, timeout=timeout, user_agent=user_agent)
    data = payload.get("data") or []
    if not data:
        raise MacroSourceError("Treasury daily rates endpoint returned no data")
    latest = dict(data[0])
    as_of_date = str(latest.get(record_date_field) or "")
    if not as_of_date:
        raise MacroSourceError("Treasury daily rates row is missing record_date")

    observations: list[MacroObservation] = []
    for field in fields:
        source_field = str(field.get("field") or "").strip()
        key = str(field.get("key") or source_field).strip()
        if not source_field or not key:
            raise MacroSourceError(f"Invalid Treasury field configuration: {field!r}")
        value = parse_float(latest.get(source_field))
        max_staleness = int(field.get("max_staleness_days", 7))
        age = ensure_fresh(label=f"Treasury {source_field}", as_of_date=as_of_date, reference_date=reference_date, max_staleness_days=max_staleness)
        observations.append(
            MacroObservation(
                key=key,
                value=value,
                units=str(field.get("units") or "percent"),
                source="treasury_fiscaldata",
                series_id=str(field.get("series_id") or f"fiscaldata.daily_treasury_rates.{source_field}"),
                label=str(field.get("label") or source_field),
                category=str(field.get("category") or "rates"),
                as_of_date=as_of_date,
                fetched_at_utc=utc_now_iso(),
                staleness_days=age,
                max_staleness_days=max_staleness,
                source_url=url,
                provider_metadata={"record_date_field": record_date_field, "field": source_field},
            )
        )
    return observations
