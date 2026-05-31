from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

REQUIRED_GROUPS = {"fred", "ecb", "treasury_fiscaldata", "volatility"}
TOP_LEVEL = ["schema_version", "mode", "status", "generated_at_utc", "run_id", "reference_date", "observations", "summary", "authority"]
OBS_FIELDS = ["key", "value", "source", "series_id", "as_of_date", "fetched_at_utc", "staleness_days", "max_staleness_days", "status"]


def load(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError("Macro data audit file missing: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def latest_path() -> Path:
    pointer = Path("output/macro/latest_macro_data_audit_path.txt")
    if not pointer.exists():
        raise RuntimeError("latest_macro_data_audit_path.txt is missing")
    raw = pointer.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError("latest_macro_data_audit_path.txt is empty")
    return Path(raw)


def is_date(value: object) -> bool:
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def source_group(row: dict) -> str:
    source = str(row.get("source") or "")
    if row.get("key") == "vix_close" or source == "cboe":
        return "volatility"
    return source


def validate(path: Path) -> dict:
    payload = load(path)
    for key in TOP_LEVEL:
        if key not in payload:
            raise RuntimeError("Macro data audit missing top-level field: " + key)
    if payload.get("status") != "passed":
        raise RuntimeError("Macro data audit status is not passed")
    if payload.get("mode") not in {"live", "fixture"}:
        raise RuntimeError("Macro data audit mode is invalid")
    if not is_date(payload.get("reference_date")):
        raise RuntimeError("Macro data audit reference_date is invalid")
    rows = payload.get("observations") or []
    if not rows:
        raise RuntimeError("Macro data audit has no observations")
    seen = set()
    groups = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise RuntimeError("Macro observation is not an object")
        for field in OBS_FIELDS:
            if field not in row:
                raise RuntimeError("Macro observation missing field: " + field)
        key = str(row.get("key") or "")
        if not key:
            raise RuntimeError("Macro observation has empty key")
        if key in seen:
            raise RuntimeError("Duplicate macro observation key: " + key)
        seen.add(key)
        if not isinstance(row.get("value"), (int, float)):
            raise RuntimeError("Macro observation value is not numeric: " + key)
        if not is_date(row.get("as_of_date")):
            raise RuntimeError("Macro observation date is invalid: " + key)
        staleness = int(row.get("staleness_days"))
        max_staleness = int(row.get("max_staleness_days"))
        if staleness < 0 or staleness > max_staleness:
            raise RuntimeError("Macro observation stale: " + key)
        if row.get("status") != "fresh":
            raise RuntimeError("Macro observation status is not fresh: " + key)
        groups.add(source_group(row))
    missing = sorted(REQUIRED_GROUPS - groups)
    if missing:
        raise RuntimeError("Macro data audit missing source groups: " + ", ".join(missing))
    summary = payload.get("summary") or {}
    if summary.get("shadow_only") is not True or summary.get("client_facing_authority") is not False:
        raise RuntimeError("Macro audit authority flags are invalid")
    if int(summary.get("observation_count") or -1) != len(rows):
        raise RuntimeError("Macro audit observation_count mismatch")
    return {"mode": payload.get("mode"), "reference_date": payload.get("reference_date"), "observations": len(rows), "groups": sorted(groups)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", default=None)
    args = parser.parse_args()
    result = validate(Path(args.audit) if args.audit else latest_path())
    print("ETF_MACRO_DATA_AUDIT_VALID_OK | mode={} | reference_date={} | observations={} | groups={}".format(result["mode"], result["reference_date"], result["observations"], ",".join(result["groups"])))


if __name__ == "__main__":
    main()
