from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "macro_regime_promotion_decision_v1"
ARTIFACT_TYPE = "deterministic_macro_regime_promotion_decision"
ALLOWED_STATUS = {"not_promoted", "promoted_to_report_narrative_authority"}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "artifact_type",
    "run_id",
    "created_at_utc",
    "report_date",
    "status",
    "client_facing_narrative_authority",
    "production_report_narrative_authority",
    "required_approvals",
    "promotion_decision",
    "authority",
    "blockers",
}

REQUIRED_APPROVALS = {
    "methodology_approved",
    "bilingual_parity_approved",
    "compliance_validator_passed",
    "old_vs_new_comparison_reviewed",
}

REQUIRED_PROMOTION_DECISION = {
    "control_layer_decision",
    "explicit_control_layer_promotion_decision",
    "decision_record_path",
    "reviewed_by_or_process",
}

REQUIRED_AUTHORITY_FALSE = {
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "funding_authority",
    "portfolio_mutation",
}

PROMOTION_DECISION_VALUE = "promote_to_report_narrative_authority"
NOT_PROMOTED_DECISION_VALUE = "not_promoted"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"macro promotion contract failed: {key} must be a non-empty string")


def _require_bool(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), bool):
        raise RuntimeError(f"macro promotion contract failed: {key} must be a boolean")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"macro promotion contract failed: {key} must remain false")


def _validate_approvals(payload: dict[str, Any]) -> dict[str, bool]:
    approvals = payload["required_approvals"]
    if not isinstance(approvals, dict):
        raise RuntimeError("macro promotion contract failed: required_approvals must be an object")
    missing = _missing(REQUIRED_APPROVALS, approvals)
    if missing:
        raise RuntimeError("macro promotion contract failed: required_approvals missing key(s): " + ", ".join(missing))
    for key in REQUIRED_APPROVALS:
        if not isinstance(approvals[key], bool):
            raise RuntimeError(f"macro promotion contract failed: required_approvals.{key} must be a boolean")
    return approvals


def _validate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    decision = payload["promotion_decision"]
    if not isinstance(decision, dict):
        raise RuntimeError("macro promotion contract failed: promotion_decision must be an object")
    missing = _missing(REQUIRED_PROMOTION_DECISION, decision)
    if missing:
        raise RuntimeError("macro promotion contract failed: promotion_decision missing key(s): " + ", ".join(missing))
    if not isinstance(decision["explicit_control_layer_promotion_decision"], bool):
        raise RuntimeError("macro promotion contract failed: explicit_control_layer_promotion_decision must be a boolean")
    for key in ("control_layer_decision", "decision_record_path", "reviewed_by_or_process"):
        if not isinstance(decision[key], str) or not decision[key].strip():
            raise RuntimeError(f"macro promotion contract failed: promotion_decision.{key} must be a non-empty string")
    return decision


def _validate_authority(payload: dict[str, Any]) -> None:
    authority = payload["authority"]
    if not isinstance(authority, dict):
        raise RuntimeError("macro promotion contract failed: authority must be an object")
    missing = _missing(REQUIRED_AUTHORITY_FALSE, authority)
    if missing:
        raise RuntimeError("macro promotion contract failed: authority missing key(s): " + ", ".join(missing))
    for key in REQUIRED_AUTHORITY_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"macro promotion contract failed: authority.{key} must remain false")


def validate_macro_regime_promotion_contract(path: Path) -> None:
    payload = _load(path)
    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError("macro promotion contract failed: missing top-level key(s): " + ", ".join(missing_top))
    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"macro promotion contract failed: unsupported schema_version={payload['schema_version']}")
    if payload["artifact_type"] != ARTIFACT_TYPE:
        raise RuntimeError(f"macro promotion contract failed: unsupported artifact_type={payload['artifact_type']}")
    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError(f"macro promotion contract failed: unsupported status={payload['status']}")
    for key in ("run_id", "created_at_utc", "report_date"):
        _require_non_empty_string(payload, key)
    for key in ("client_facing_narrative_authority", "production_report_narrative_authority"):
        _require_bool(payload, key)

    approvals = _validate_approvals(payload)
    decision = _validate_decision(payload)
    _validate_authority(payload)

    blockers = payload["blockers"]
    if not isinstance(blockers, list):
        raise RuntimeError("macro promotion contract failed: blockers must be a list")

    status = payload["status"]
    if status == "not_promoted":
        _require_false(payload, "client_facing_narrative_authority")
        _require_false(payload, "production_report_narrative_authority")
        if decision["control_layer_decision"] != NOT_PROMOTED_DECISION_VALUE:
            raise RuntimeError("macro promotion contract failed: not_promoted artifacts require control_layer_decision=not_promoted")
        if decision["explicit_control_layer_promotion_decision"] is not False:
            raise RuntimeError("macro promotion contract failed: not_promoted artifacts must not contain an explicit promotion decision")
        if "macro regime remains shadow-only" not in blockers:
            raise RuntimeError("macro promotion contract failed: blockers must include macro regime remains shadow-only")

    if status == "promoted_to_report_narrative_authority":
        if payload["client_facing_narrative_authority"] is not True:
            raise RuntimeError("macro promotion contract failed: promoted artifacts require client_facing_narrative_authority=true")
        if payload["production_report_narrative_authority"] is not True:
            raise RuntimeError("macro promotion contract failed: promoted artifacts require production_report_narrative_authority=true")
        for key in REQUIRED_APPROVALS:
            if approvals[key] is not True:
                raise RuntimeError(f"macro promotion contract failed: promoted artifact requires required_approvals.{key}=true")
        if decision["control_layer_decision"] != PROMOTION_DECISION_VALUE:
            raise RuntimeError("macro promotion contract failed: promoted artifact requires control_layer_decision=promote_to_report_narrative_authority")
        if decision["explicit_control_layer_promotion_decision"] is not True:
            raise RuntimeError("macro promotion contract failed: promoted artifact requires explicit_control_layer_promotion_decision=true")
        if blockers:
            raise RuntimeError("macro promotion contract failed: promoted artifacts must not contain blockers")

    print(f"MACRO_REGIME_PROMOTION_CONTRACT_OK | artifact={path} | status={status} | portfolio_action_authority=false | lane_scoring_authority=false")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_macro_regime_promotion_contract(Path(args.artifact))


if __name__ == "__main__":
    main()
