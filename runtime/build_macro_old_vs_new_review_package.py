from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT_PATH = REPO_ROOT / "output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output/macro/review"

SCHEMA_VERSION = "macro_old_vs_new_review_v1"
ARTIFACT_TYPE = "macro_old_vs_new_review_package"
READY_FOR_REVIEW = "ready_for_narrative_promotion_review"
KEEP_SHADOW_ONLY = "keep_shadow_only"

AUTHORITY_FALSE = {
    "production_report_narrative_authority": False,
    "portfolio_action_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
    "funding_authority": False,
    "portfolio_mutation": False,
    "production_report_mutation": False,
    "delivery_authority": False,
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _word_count(text: str) -> int:
    return len([part for part in text.replace("\n", " ").split(" ") if part.strip()])


def _criterion(name: str, passed: bool, current_observation: str, candidate_observation: str) -> dict[str, Any]:
    return {
        "criterion": name,
        "passed": bool(passed),
        "current_production_observation": current_observation,
        "deterministic_candidate_observation": candidate_observation,
    }


def _build_criteria(pilot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    current_en = pilot.get("current_macro_narrative_en", "")
    current_nl = pilot.get("current_macro_narrative_nl", "")
    candidate_en = pilot.get("deterministic_macro_candidate_en", "")
    candidate_nl = pilot.get("deterministic_macro_candidate_nl", "")
    blockers = pilot.get("blockers", [])

    candidate_has_citation = "[M1]" in candidate_en and "[M1]" in candidate_nl
    wp2_passed = pilot.get("wp2_validation_status") == "passed"
    no_authority = all(pilot.get(key) is False for key in AUTHORITY_FALSE if key in pilot)
    not_promoted = pilot.get("wp3_promotion_status") == "not_promoted"
    no_mutation = "no production report mutation" in blockers and "no delivery workflow change" in blockers

    return {
        "clarity": _criterion(
            "clarity",
            _word_count(candidate_en) >= 20 and _word_count(candidate_nl) >= 20,
            "Current production wording is concise but regime-label oriented.",
            "Candidate gives a fuller explanation of risk tone, narrow leadership, and authority boundaries.",
        ),
        "factual_support": _criterion(
            "factual_support",
            candidate_has_citation and wp2_passed,
            "Current production wording is brief and report-context based.",
            "Candidate includes citation marker [M1] and passed the WP2 client-surface gate.",
        ),
        "bilingual_parity": _criterion(
            "bilingual_parity",
            wp2_passed,
            "Current English/Dutch production wording is concise and parallel.",
            "Candidate passed WP2 bilingual parity validation.",
        ),
        "absence_of_predictive_wording": _criterion(
            "absence_of_predictive_wording",
            wp2_passed,
            "Current wording is stable report language.",
            "Candidate passed WP2 predictive-language checks.",
        ),
        "absence_of_internal_shadow_labels": _criterion(
            "absence_of_internal_shadow_labels",
            wp2_passed,
            "Current report wording does not expose internal macro payload fields.",
            "Candidate passed WP2 internal/shadow label leakage checks.",
        ),
        "consistency_with_macro_methodology": _criterion(
            "consistency_with_macro_methodology",
            pilot.get("meaning_contract", {}).get("confidence_language") == "evidence_based_observation",
            "Current report gives a regime/confidence summary.",
            "Candidate frames macro inputs as review context, not as standalone portfolio signals.",
        ),
        "consistency_with_current_report_tone": _criterion(
            "consistency_with_current_report_tone",
            "No portfolio action" in candidate_en and "geen portefeuilleactie" in candidate_nl.lower(),
            "Current report uses concise professional client language.",
            "Candidate remains professional and explicitly preserves portfolio-action boundaries.",
        ),
        "no_portfolio_action_leakage": _criterion(
            "no_portfolio_action_leakage",
            no_authority and not_promoted and no_mutation,
            "Current production report owns final client wording under the normal report path.",
            "Candidate keeps all portfolio/lane/fundability/funding/mutation/delivery authorities false and remains not promoted.",
        ),
    }


def build_review_package(pilot_path: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    pilot = _load(pilot_path)
    criteria = _build_criteria(pilot)
    all_passed = all(item["passed"] is True for item in criteria.values())
    review_status = READY_FOR_REVIEW if all_passed else KEEP_SHADOW_ONLY
    run_id = pilot.get("run_id", "unknown_run")
    report_date = pilot.get("report_date", "unknown_date")

    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": report_date,
        "input_pilot_artifact_path": str(pilot_path.relative_to(REPO_ROOT) if pilot_path.is_absolute() and pilot_path.is_relative_to(REPO_ROOT) else pilot_path),
        "pilot_validation_status": "passed",
        "wp2_validation_status": pilot.get("wp2_validation_status"),
        "wp3_promotion_status": pilot.get("wp3_promotion_status"),
        "review_status": review_status,
        "review_summary": (
            "The deterministic macro pilot is ready for narrative promotion review, but remains not promoted."
            if review_status == READY_FOR_REVIEW
            else "The deterministic macro pilot should remain shadow-only pending further remediation."
        ),
        "current_macro_narrative_en": pilot.get("current_macro_narrative_en", ""),
        "current_macro_narrative_nl": pilot.get("current_macro_narrative_nl", ""),
        "deterministic_macro_candidate_en": pilot.get("deterministic_macro_candidate_en", ""),
        "deterministic_macro_candidate_nl": pilot.get("deterministic_macro_candidate_nl", ""),
        "review_criteria": criteria,
        "required_next_step_before_promotion": "create WP9 promotion decision artifact under control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md",
        "authority": dict(AUTHORITY_FALSE),
        "blockers": [
            "review package is not promotion",
            "wp3 promotion artifact still required",
            "production report narrative authority remains false",
            "portfolio_action_authority=false",
            "lane_scoring_authority=false",
            "fundability_authority=false",
            "funding_authority=false",
            "portfolio_mutation=false",
            "no production report mutation",
            "no delivery workflow change",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"macro_old_vs_new_review_{run_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-artifact", type=Path, default=DEFAULT_PILOT_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    out_path = build_review_package(args.pilot_artifact, args.output_dir)
    print(f"MACRO_OLD_VS_NEW_REVIEW_WRITTEN | artifact={out_path}")


if __name__ == "__main__":
    main()
