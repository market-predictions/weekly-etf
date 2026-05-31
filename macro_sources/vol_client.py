from __future__ import annotations

from typing import Any

from macro_sources.common import MacroObservation, MacroSourceError, build_url, ensure_fresh, fetch_json, fetch_text, parse_float, read_csv_rows, utc_now_iso


def _fetch_cboe(config: dict[str, Any], *, reference_date: str) -> MacroObservation:
    vol_cfg = config.get("volatility") or {}
    url = str(vol_cfg.get("cboe_chart_url") or "").strip()
    if not url:
        raise MacroSourceError("CBOE VIX chart URL is missing from config")
    defaults = config.get("defaults") or {}
    timeout = int(defaults.get("request_timeout_seconds", 25))
    user_agent = str(defaults.get("user_agent") or "weekly-etf-macro-audit/1.0")
    payload = fetch_json(url, timeout=timeout, user_agent=user_agent)
    data = payload.get("data") or []
    if not isinstance(data, list) or not data:
        raise MacroSourceError("CBOE VIX chart endpoint returned no data")
    latest = dict(data[-1])
    # CBOE delayed quote chart rows have changed shape historically. Accept the
    # common date/value spellings and fail loudly if none are present.
    as_of_date = str(latest.get("date") or latest.get("dt") or latest.get("time") or latest.get("x") or "")[:10]
    raw_value = latest.get("close") or latest.get("value") or latest.get("y") or latest.get("last")
    value = parse_float(raw_value)
    series = (vol_cfg.get("series") or [{}])[0]
    max_staleness = int(series.get("max_staleness_days", 7))
    age = ensure_fresh(label="CBOE VIX", as_of_date=as_of_date, reference_date=reference_date, max_staleness_days=max_staleness)
    return MacroObservation(
        key=str(series.get("key") or "vix_close"),
        value=value,
        units=str(series.get("units") or "index"),
        source="cboe",
        series_id=str(series.get("series_id") or "CBOE/VIX"),
        label=str(series.get("label") or "CBOE Volatility Index close"),
        category=str(series.get("category") or "volatility"),
        as_of_date=as_of_date,
        fetched_at_utc=utc_now_iso(),
        staleness_days=age,
        max_staleness_days=max_staleness,
        source_url=url,
        provider_metadata={"endpoint": "delayed_quotes_chart"},
    )


def _fetch_fred_vix(config: dict[str, Any], *, reference_date: str, error_note: str) -> MacroObservation:
    vol_cfg = config.get("volatility") or {}
    fallback = vol_cfg.get("fallback_fred") or {}
    series_id = str(fallback.get("series_id") or "VIXCLS")
    fred_cfg = config.get("fred") or {}
    base_url = str(fred_cfg.get("base_url") or "https://fred.stlouisfed.org/graph/fredgraph.csv")
    defaults = config.get("defaults") or {}
    timeout = int(defaults.get("request_timeout_seconds", 25))
    user_agent = str(defaults.get("user_agent") or "weekly-etf-macro-audit/1.0")
    url = build_url(base_url, {"id": series_id})
    rows = read_csv_rows(fetch_text(url, timeout=timeout, user_agent=user_agent))
    latest = None
    for row in reversed(rows):
        try:
            parse_float(row.get(series_id))
        except MacroSourceError:
            continue
        latest = row
        break
    if latest is None:
        raise MacroSourceError(f"FRED VIX fallback {series_id}: no valid observations returned after CBOE failure: {error_note}")
    as_of_date = str(latest.get("observation_date") or latest.get("DATE") or latest.get("date"))
    value = parse_float(latest.get(series_id))
    series = (vol_cfg.get("series") or [{}])[0]
    max_staleness = int(series.get("max_staleness_days", 7))
    age = ensure_fresh(label=f"FRED {series_id}", as_of_date=as_of_date, reference_date=reference_date, max_staleness_days=max_staleness)
    return MacroObservation(
        key=str(series.get("key") or "vix_close"),
        value=value,
        units=str(series.get("units") or "index"),
        source="fred",
        series_id=series_id,
        label=str(fallback.get("label") or series.get("label") or "CBOE Volatility Index close"),
        category=str(series.get("category") or "volatility"),
        as_of_date=as_of_date,
        fetched_at_utc=utc_now_iso(),
        staleness_days=age,
        max_staleness_days=max_staleness,
        source_url=url,
        provider_metadata={"fallback_reason": error_note, "primary_source": "cboe"},
    )


def fetch_volatility_series(config: dict[str, Any], *, reference_date: str) -> list[MacroObservation]:
    vol_cfg = config.get("volatility") or {}
    if not vol_cfg.get("enabled", True):
        return []
    try:
        return [_fetch_cboe(config, reference_date=reference_date)]
    except MacroSourceError as exc:
        return [_fetch_fred_vix(config, reference_date=reference_date, error_note=str(exc))]
