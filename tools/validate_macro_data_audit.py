from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

REQUIRED_GROUPS = {"fred", "ecb", "treasury_fiscaldata", "volatility"}
TOP_LEVEL = [
    "schema_version",
    "mode",
    "status",
    "generated_at_utc",
    "run_id",
    "reference_date",
    "report_token",
    "required_source_groups",
    "source_group_status",
    "observations",
    "summary",
    "authority",
]
OBS_FIELDS = [
    "key",
    "value",
    "units",
    "source",
    "series_id",
    "label",
    "category",
    "as_of_date",
    "fetched_at_utc",
    "staleness_days",
    "max_staleness_days",
    "status",
]
AUTHORITY_FIELDS = ["decision_framework", "input_state_contract", "output_contract", "operational_runbook"]
POSITIVE_AUTHORITY_PATTERNS = [
    "can drive allocation",
    "may drive allocation",
    "drives allocation",
    "allocation authority granted",
    "portfolio action authority granted",
    "lane scoring authority granted",
    "fundability authority granted",
    "sets regime",
    "sets confidence",
    "sets lane scoring",
    "sets fundability",
    "sets portfolio action",
]


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
    path = Path(raw)
    if path.exists():
        return path
    candidate = pointer.parent / path.name
    if candidate.exists():
        return candidate
    raise RuntimeError("latest_macro_data_audit_path.txt points to a missing file: " + raw)


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


def _require_authority(payload: dict) -> None:
    authority = payload.get("authority") or {}
    for field in AUTHORITY_FIELDS:
        if not str(authority.get(field) or "").strip():
            raise RuntimeError("Macro data audit authority field missing: " + field)
    text = " ".join(str(authority.get(field) or "") for field in AUTHORITY_FIELDS).lower()
    if "no allocation" not in text and "no allocation decision authority" not in text:
        raise RuntimeError("Macro data audit authority does not explicitly deny allocation authority")
    matched = [pattern for pattern in POSITIVE_AUTHORITY_PATTERNS if pattern in text]
    if matched:
        raise RuntimeError("Macro data audit authority wording may imply production authority: " + ", ".join(matched))


def _require_source_groups(payload: dict, groups: set[str]) -> None:
    declared = set(str(group) for group in (payload.get("required_source_groups") or []))
    if declared != REQUIRED_GROUPS:
        raise RuntimeError("Macro data audit required_source_groups mismatch: " + ",".join(sorted(declared)))
    status = payload.get("source_group_status") or {}
    missing = sorted(REQUIRED_GROUPS - groups)
    if missing:
        raise RuntimeError("Macro data audit missing source groups: " + ", ".join(missing))
    for group in REQUIRED_GROUPS:
        if status.get(group) != "present":
            raise RuntimeError(f"Macro data audit source_group_status[{group!r}] is not present")


def _summary_max_staleness_matches(summary: dict, rows: list[dict]) -> bool:
    actual = int(summary.get("max_staleness_days") or -1)
    max_observed_staleness = max(int(row.get("staleness_days")) for row in rows)
    max_allowed_staleness = max(int(row.get("max_staleness_days")) for row in rows)
    # Compatibility rule: WP18 fixtures use this summary as maximum observed
    # staleness; older macro-regime shadow fixtures use it as a source-contract
    # ceiling. Both are valid if the summary does not under-report observed
    # staleness and does not exceed the widest source-contract ceiling.
    return max_observed_staleness <= actual <= max_allowed_staleness


def validate(path: Path) -> dict:
    payload = load(path)
    for key in TOP_LEVEL:
        if key not in payload:
            raise RuntimeError("Macro data audit missing top-level field: " + key)
    if payload.get("schema_version") != "1.0":
        raise RuntimeError("Macro data audit schema_version is not 1.0")
    if payload.get("status") != "passed":
        raise RuntimeError("Macro data audit status is not passed")
    if payload.get("mode") not in {"live", "fixture"}:
        raise RuntimeError("Macro data audit mode is invalid")
    if not is_date(payload.get("reference_date")):
        raise RuntimeError("Macro data audit reference_date is invalid")
    if not str(payload.get("run_id") or "").strip():
        raise RuntimeError("Macro data audit run_id is missing")
    if not str(payload.get("report_token") or "").strip():
        raise RuntimeError("Macro data audit report_token is missing")
    _require_authority(payload)

    rows = payload.get("observations") or []
    if not rows:
        raise RuntimeError("Macro data audit has no observations")
    seen = set()
    groups = set()
    for row in rows:
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
        if not str(row.get("source") or "").strip():
            raise RuntimeError("Macro observation source is empty: " + key)
        if not str(row.get("series_id") or "").strip():
            raise RuntimeError("Macro observation series_id is empty: " + key)
        if not str(row.get("label") or "").strip():
            raise RuntimeError("Macro observation label is empty: " + key)
        if not is_date(row.get("as_of_date")):
            raise RuntimeError("Macro observation date is invalid: " + key)
        if "t" not in str(row.get("fetched_at_utc") or "").lower():
            raise RuntimeError("Macro observation fetched_at_utc is invalid: " + key)
        staleness = int(row.get("staleness_days"))
        max_staleness = int(row.get("max_staleness_days"))
        if staleness < 0 or staleness > max_staleness:
            raise RuntimeError("Macro observation stale: " + key)
        if row.get("status") != "fresh":
            raise RuntimeError("Macro observation status is not fresh: " + key)
        if payload.get("mode") == "live" and not str(row.get("source_url") or "").strip():
            raise RuntimeError("Live macro observation missing source_url: " + key)
        groups.add(source_group(row))
    _require_source_groups(payload, groups)

    summary = payload.get("summary") or {}
    if summary.get("shadow_only") is not True or summary.get("client_facing_authority") is not False:
        raise RuntimeError("Macro audit authority flags are invalid")
    if int(summary.get("observation_count") or -1) != len(rows):
        raise RuntimeError("Macro audit observation_count mismatch")
    if not _summary_max_staleness_matches(summary, rows):
        raise RuntimeError("Macro audit max_staleness_days mismatch")
    return {"mode": payload.get("mode"), "reference_date": payload.get("reference_date"), "observations": len(rows), "groups": sorted(groups)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", default=None)
    args = parser.parse_args()
    result = validate(Path(args.audit) if args.audit else latest_path())
    print(
        "ETF_MACRO_DATA_AUDIT_VALID_OK | "
        "mode={} | reference_date={} | observations={} | groups={}".format(
            result["mode"], result["reference_date"], result["observations"], ",".join(result["groups"])
        )
    )


if __name__ == "__main__":
    main()
