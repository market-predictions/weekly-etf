from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "macro_old_vs_new_review_v1"
ARTIFACT_TYPE = "macro_old_vs_new_review_package"
ALLOWED_REVIEW_STATUS = {"keep_shadow_only", "ready_for_narrative_promotion_review"}
REQUIRED_CRITERIA = {
    "clarity",
    "factual_support",
    "bilingual_parity",
    "absence_of_predictive_wording",
    "absence_of_internal_shadow_labels",
    "consistency_with_macro_methodology",
    "consistency_with_current_report_tone",
    "no_portfolio_action_leakage",
}
REQUIRED_FALSE_AUTHORITY = {
    "production_report_narrative_authority",
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "funding_authority",
    "portfolio_mutation",
    "production_report_mutation",
    "delivery_authority",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("macro old-vs-new review failed: artifact must be a JSON object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"macro old-vs-new review failed: {key} must be a non-empty string")


def validate_macro_old_vs_new_review_package(path: Path) -> None:
    payload = _load(path)
    required_top = {
        "schema_version",
        "artifact_type",
        "run_id",
        "created_at_utc",
        "report_date",
        "input_pilot_artifact_path",
        "pilot_validation_status",
        "wp2_validation_status",
        "wp3_promotion_status",
        "review_status",
        "review_summary",
        "current_macro_narrative_en",
        "current_macro_narrative_nl",
        "deterministic_macro_candidate_en",
        "deterministic_macro_candidate_nl",
        "review_criteria",
        "required_next_step_before_promotion",
        "authority",
        "blockers",
    }
    missing_top = _missing(required_top, payload)
    if missing_top:
        raise RuntimeError("macro old-vs-new review failed: missing top-level key(s): " + ", ".join(missing_top))

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"macro old-vs-new review failed: unsupported schema_version={payload['schema_version']}")
    if payload["artifact_type"] != ARTIFACT_TYPE:
        raise RuntimeError(f"macro old-vs-new review failed: unsupported artifact_type={payload['artifact_type']}")
    if payload["review_status"] not in ALLOWED_REVIEW_STATUS:
        raise RuntimeError(f"macro old-vs-new review failed: unsupported review_status={payload['review_status']}")
    if payload["pilot_validation_status"] != "passed":
        raise RuntimeError("macro old-vs-new review failed: pilot_validation_status must be passed")
    if payload["wp2_validation_status"] != "passed":
        raise RuntimeError("macro old-vs-new review failed: wp2_validation_status must be passed")
    if payload["wp3_promotion_status"] != "not_promoted":
        raise RuntimeError("macro old-vs-new review failed: wp3_promotion_status must remain not_promoted")

    for key in (
        "run_id",
        "created_at_utc",
        "report_date",
        "input_pilot_artifact_path",
        "review_summary",
        "current_macro_narrative_en",
        "current_macro_narrative_nl",
        "deterministic_macro_candidate_en",
        "deterministic_macro_candidate_nl",
        "required_next_step_before_promotion",
    ):
        _require_non_empty_string(payload, key)

    criteria = payload["review_criteria"]
    if not isinstance(criteria, dict):
        raise RuntimeError("macro old-vs-new review failed: review_criteria must be an object")
    missing_criteria = _missing(REQUIRED_CRITERIA, criteria)
    if missing_criteria:
        raise RuntimeError("macro old-vs-new review failed: missing review criteria: " + ", ".join(missing_criteria))
    all_passed = True
    for name in REQUIRED_CRITERIA:
        item = criteria[name]
        if not isinstance(item, dict):
            raise RuntimeError(f"macro old-vs-new review failed: review_criteria.{name} must be an object")
        for key in ("criterion", "passed", "current_production_observation", "deterministic_candidate_observation"):
            if key not in item:
                raise RuntimeError(f"macro old-vs-new review failed: review_criteria.{name} missing {key}")
        if item["criterion"] != name:
            raise RuntimeError(f"macro old-vs-new review failed: review_criteria.{name}.criterion mismatch")
        if not isinstance(item["passed"], bool):
            raise RuntimeError(f"macro old-vs-new review failed: review_criteria.{name}.passed must be boolean")
        if item["passed"] is False:
            all_passed = False
        for text_key in ("current_production_observation", "deterministic_candidate_observation"):
            if not isinstance(item[text_key], str) or not item[text_key].strip():
                raise RuntimeError(f"macro old-vs-new review failed: review_criteria.{name}.{text_key} must be a non-empty string")

    if payload["review_status"] == "ready_for_narrative_promotion_review" and not all_passed:
        raise RuntimeError("macro old-vs-new review failed: ready status requires all criteria to pass")

    authority = payload["authority"]
    if not isinstance(authority, dict):
        raise RuntimeError("macro old-vs-new review failed: authority must be an object")
    missing_auth = _missing(REQUIRED_FALSE_AUTHORITY, authority)
    if missing_auth:
        raise RuntimeError("macro old-vs-new review failed: authority missing key(s): " + ", ".join(missing_auth))
    for key in REQUIRED_FALSE_AUTHORITY:
        if authority[key] is not False:
            raise RuntimeError(f"macro old-vs-new review failed: authority.{key} must remain false")

    blockers = payload["blockers"]
    if not isinstance(blockers, list):
        raise RuntimeError("macro old-vs-new review failed: blockers must be a list")
    for required_blocker in (
        "review package is not promotion",
        "wp3 promotion artifact still required",
        "production report narrative authority remains false",
        "no production report mutation",
        "no delivery workflow change",
    ):
        if required_blocker not in blockers:
            raise RuntimeError(f"macro old-vs-new review failed: blockers must include {required_blocker}")

    print(
        f"MACRO_OLD_VS_NEW_REVIEW_OK | artifact={path} | review_status={payload['review_status']} | "
        "production_report_narrative_authority=false | portfolio_action_authority=false | "
        "lane_scoring_authority=false | fundability_authority=false | funding_authority=false | "
        "portfolio_mutation=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    validate_macro_old_vs_new_review_package(args.artifact)


if __name__ == "__main__":
    main()
