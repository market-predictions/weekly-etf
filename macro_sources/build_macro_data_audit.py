from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from macro_sources.cb_calendar import load_cb_calendar
from macro_sources.common import MacroObservation, MacroSourceError, load_fixture, parse_date, utc_now_iso
from macro_sources.ecb_client import fetch_ecb_series
from macro_sources.fred_client import fetch_fred_series
from macro_sources.treasury_client import fetch_treasury_series
from macro_sources.vol_client import fetch_volatility_series

REQUIRED_SOURCE_GROUPS = {"fred", "ecb", "treasury_fiscaldata", "volatility"}


def _report_token(reference_date: str) -> str:
    try:
        return parse_date(reference_date).strftime("%y%m%d")
    except MacroSourceError:
        return reference_date.replace("-", "")[-6:]


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise MacroSourceError(f"Macro data source config missing: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _source_group(row: dict[str, Any]) -> str:
    source = str(row.get("source") or "")
    if row.get("key") == "vix_close":
        return "volatility"
    if source == "fred":
        return "fred"
    if source == "ecb":
        return "ecb"
    if source == "treasury_fiscaldata":
        return "treasury_fiscaldata"
    if source == "cboe":
        return "volatility"
    return source


def _observation_groups(observations: list[dict[str, Any]]) -> set[str]:
    return {_source_group(row) for row in observations if _source_group(row)}


def _validate_required_groups(observations: list[dict[str, Any]]) -> None:
    missing = sorted(REQUIRED_SOURCE_GROUPS - _observation_groups(observations))
    if missing:
        raise MacroSourceError(f"Macro audit missing required source groups: {', '.join(missing)}")


def _fetch_live(config: dict[str, Any], *, reference_date: str) -> list[MacroObservation]:
    observations: list[MacroObservation] = []
    observations.extend(fetch_fred_series(config, reference_date=reference_date))
    observations.extend(fetch_ecb_series(config, reference_date=reference_date))
    observations.extend(fetch_treasury_series(config, reference_date=reference_date))
    observations.extend(fetch_volatility_series(config, reference_date=reference_date))
    if not observations:
        raise MacroSourceError("Macro audit fetch produced zero observations")
    return observations


def _normalize_fixture(fixture: dict[str, Any], *, run_id: str, reference_date: str) -> dict[str, Any]:
    payload = dict(fixture)
    payload["run_id"] = run_id
    payload["reference_date"] = reference_date
    payload["report_token"] = _report_token(reference_date)
    payload["generated_at_utc"] = utc_now_iso()
    payload["mode"] = "fixture"
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("status", "passed")
    _validate_required_groups(payload.get("observations", []) or [])
    return payload


def build_macro_data_audit(
    *,
    config_path: Path,
    cb_calendar_path: Path,
    reference_date: str,
    run_id: str,
    fixture_path: Path | None = None,
) -> dict[str, Any]:
    if fixture_path is not None:
        return _normalize_fixture(load_fixture(fixture_path), run_id=run_id, reference_date=reference_date)

    config = _load_config(config_path)
    observations = [obs.to_dict() for obs in _fetch_live(config, reference_date=reference_date)]
    _validate_required_groups(observations)
    max_staleness = max(int(obs.get("staleness_days") or 0) for obs in observations)
    groups = _observation_groups(observations)
    return {
        "schema_version": "1.0",
        "mode": "live",
        "status": "passed",
        "generated_at_utc": utc_now_iso(),
        "run_id": run_id,
        "reference_date": reference_date,
        "report_token": _report_token(reference_date),
        "source_config": str(config_path),
        "central_bank_calendar": load_cb_calendar(cb_calendar_path),
        "source_group_status": {group: "present" for group in sorted(groups)},
        "required_source_groups": sorted(REQUIRED_SOURCE_GROUPS),
        "observations": sorted(observations, key=lambda row: str(row.get("key"))),
        "summary": {
            "observation_count": len(observations),
            "max_staleness_days": max_staleness,
            "sources": sorted({str(obs.get("source")) for obs in observations}),
            "shadow_only": True,
            "client_facing_authority": False,
        },
        "authority": {
            "decision_framework": "macro audit foundation only; no allocation decision authority",
            "input_state_contract": "all values carry source, series_id, as_of_date, fetched_at_utc, and staleness_days",
            "output_contract": "internal JSON audit artifact only",
            "operational_runbook": "raise an error when required source groups are missing or stale",
        },
    }


def _write_outputs(payload: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_date = str(payload.get("reference_date") or "unknown")
    run_id = str(payload.get("run_id") or "unknown")
    out_path = output_dir / f"macro_data_audit_{reference_date}_{run_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "latest_macro_data_audit_path.txt").write_text(str(out_path) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a run-scoped ETF macro data audit artifact.")
    parser.add_argument("--config", default="config/macro_data_sources.yml")
    parser.add_argument("--cb-calendar", default="config/cb_calendar.yml")
    parser.add_argument("--reference-date", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default="output/macro")
    parser.add_argument("--fixture", default=None)
    args = parser.parse_args()

    reference_date = args.reference_date or datetime.now(timezone.utc).date().isoformat()
    run_id = args.run_id or _default_run_id()
    payload = build_macro_data_audit(
        config_path=Path(args.config),
        cb_calendar_path=Path(args.cb_calendar),
        reference_date=reference_date,
        run_id=run_id,
        fixture_path=Path(args.fixture) if args.fixture else None,
    )
    out_path = _write_outputs(payload, Path(args.output_dir))
    print(
        "ETF_MACRO_DATA_AUDIT_OK | "
        f"mode={payload.get('mode')} | reference_date={payload.get('reference_date')} | "
        f"run_id={payload.get('run_id')} | observations={len(payload.get('observations') or [])} | output={out_path}"
    )


if __name__ == "__main__":
    main()
