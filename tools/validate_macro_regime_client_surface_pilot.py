from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.validate_macro_narrative_client_surface import validate as validate_wp2_client_surface

SCHEMA_VERSION = "macro_narrative_client_surface_v1"
ARTIFACT_TYPE = "macro_narrative_client_surface"
PILOT_ARTIFACT_TYPE = "deterministic_macro_regime_client_surface_pilot"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "artifact_type",
    "pilot_artifact_type",
    "run_id",
    "created_at_utc",
    "report_date",
    "current_macro_narrative_en",
    "current_macro_narrative_nl",
    "deterministic_macro_candidate_en",
    "deterministic_macro_candidate_nl",
    "wp2_validation_status",
    "wp3_promotion_status",
    "client_surface_pilot",
    "production_report_narrative_authority",
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "funding_authority",
    "portfolio_mutation",
    "meaning_contract",
    "client_surface",
    "authority",
    "inputs",
    "blockers",
}

REQUIRED_FALSE_FLAGS = {
    "client_facing_narrative_authority",
    "production_report_narrative_authority",
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "funding_authority",
    "portfolio_mutation",
    "production_report_mutation",
}

REQUIRED_STRING_FIELDS = {
    "run_id",
    "created_at_utc",
    "report_date",
    "current_macro_narrative_en",
    "current_macro_narrative_nl",
    "deterministic_macro_candidate_en",
    "deterministic_macro_candidate_nl",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("macro client-surface pilot failed: artifact must be a JSON object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"macro client-surface pilot failed: {key} must be a non-empty string")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"macro client-surface pilot failed: {key} must remain false")


def _validate_authority(payload: dict[str, Any]) -> None:
    authority = payload.get("authority")
    if not isinstance(authority, dict):
        raise RuntimeError("macro client-surface pilot failed: authority must be an object")
    missing = _missing(REQUIRED_FALSE_FLAGS, authority)
    if missing:
        raise RuntimeError("macro client-surface pilot failed: authority missing key(s): " + ", ".join(missing))
    for key in REQUIRED_FALSE_FLAGS:
        if authority[key] is not False:
            raise RuntimeError(f"macro client-surface pilot failed: authority.{key} must remain false")


def _validate_inputs(payload: dict[str, Any]) -> None:
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        raise RuntimeError("macro client-surface pilot failed: inputs must be an object")
    path = inputs.get("wp1_shadow_narrative_artifact_path")
    if not isinstance(path, str) or not path.strip():
        raise RuntimeError("macro client-surface pilot failed: inputs.wp1_shadow_narrative_artifact_path must be set")
    if inputs.get("wp2_validator") != "tools/validate_macro_narrative_client_surface.py":
        raise RuntimeError("macro client-surface pilot failed: inputs.wp2_validator must reference WP2 validator")
    if inputs.get("wp3_promotion_contract") != "control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md":
        raise RuntimeError("macro client-surface pilot failed: inputs.wp3_promotion_contract must reference WP3 contract")


def validate_macro_regime_client_surface_pilot(path: Path) -> None:
    payload = _load(path)
    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError("macro client-surface pilot failed: missing top-level key(s): " + ", ".join(missing_top))

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"macro client-surface pilot failed: unsupported schema_version={payload['schema_version']}")
    if payload["artifact_type"] != ARTIFACT_TYPE:
        raise RuntimeError(f"macro client-surface pilot failed: unsupported artifact_type={payload['artifact_type']}")
    if payload["pilot_artifact_type"] != PILOT_ARTIFACT_TYPE:
        raise RuntimeError(f"macro client-surface pilot failed: unsupported pilot_artifact_type={payload['pilot_artifact_type']}")

    for key in REQUIRED_STRING_FIELDS:
        _require_non_empty_string(payload, key)

    if payload["wp2_validation_status"] != "passed":
        raise RuntimeError("macro client-surface pilot failed: wp2_validation_status must be passed")
    if payload["wp3_promotion_status"] != "not_promoted":
        raise RuntimeError("macro client-surface pilot failed: wp3_promotion_status must remain not_promoted")
    if payload["client_surface_pilot"] is not True:
        raise RuntimeError("macro client-surface pilot failed: client_surface_pilot must be true")

    for key in REQUIRED_FALSE_FLAGS:
        _require_false(payload, key)
    _validate_authority(payload)
    _validate_inputs(payload)

    blockers = payload["blockers"]
    if not isinstance(blockers, list):
        raise RuntimeError("macro client-surface pilot failed: blockers must be a list")
    for blocker in (
        "macro regime remains shadow-only",
        "wp3_promotion_status=not_promoted",
        "no production report mutation",
        "no delivery workflow change",
    ):
        if blocker not in blockers:
            raise RuntimeError(f"macro client-surface pilot failed: blockers must include {blocker}")

    validate_wp2_client_surface(path)

    print(
        f"MACRO_REGIME_CLIENT_SURFACE_PILOT_OK | artifact={path} | "
        "wp2_validation_status=passed | wp3_promotion_status=not_promoted | "
        "production_report_narrative_authority=false | portfolio_action_authority=false | "
        "lane_scoring_authority=false | fundability_authority=false | funding_authority=false | "
        "portfolio_mutation=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    validate_macro_regime_client_surface_pilot(args.artifact)


if __name__ == "__main__":
    main()
