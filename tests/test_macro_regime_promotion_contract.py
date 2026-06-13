import json
from pathlib import Path

import pytest

from tools.validate_macro_regime_promotion_contract import validate_macro_regime_promotion_contract

FIXTURE_DIR = Path("fixtures/macro_promotion")
WP20_REVIEW_ARTIFACT = Path("output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json")


def _payload() -> dict:
    return json.loads((FIXTURE_DIR / "not_promoted_valid.json").read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "macro_promotion.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_not_promoted_fixture_passes():
    validate_macro_regime_promotion_contract(FIXTURE_DIR / "not_promoted_valid.json")


def test_wp20_deterministic_regime_promotion_review_artifact_passes():
    validate_macro_regime_promotion_contract(WP20_REVIEW_ARTIFACT)


def test_bad_promoted_without_approval_fixture_fails():
    with pytest.raises(RuntimeError):
        validate_macro_regime_promotion_contract(FIXTURE_DIR / "bad_promoted_without_approval.json")


def test_promoted_requires_all_approval_gates(tmp_path: Path):
    payload = _payload()
    payload["status"] = "promoted_to_report_narrative_authority"
    payload["client_facing_narrative_authority"] = True
    payload["production_report_narrative_authority"] = True
    payload["required_approvals"] = {
        "methodology_approved": True,
        "bilingual_parity_approved": True,
        "compliance_validator_passed": False,
        "old_vs_new_comparison_reviewed": True,
    }
    payload["promotion_decision"] = {
        "control_layer_decision": "promote_to_report_narrative_authority",
        "explicit_control_layer_promotion_decision": True,
        "decision_record_path": "control/DECISION_LOG.md",
        "reviewed_by_or_process": "pytest",
    }
    payload["blockers"] = []

    with pytest.raises(RuntimeError, match="compliance_validator_passed=true"):
        validate_macro_regime_promotion_contract(_write(tmp_path, payload))


def test_promoted_requires_explicit_control_layer_decision(tmp_path: Path):
    payload = _payload()
    payload["status"] = "promoted_to_report_narrative_authority"
    payload["client_facing_narrative_authority"] = True
    payload["production_report_narrative_authority"] = True
    payload["required_approvals"] = {
        "methodology_approved": True,
        "bilingual_parity_approved": True,
        "compliance_validator_passed": True,
        "old_vs_new_comparison_reviewed": True,
    }
    payload["promotion_decision"] = {
        "control_layer_decision": "promote_to_report_narrative_authority",
        "explicit_control_layer_promotion_decision": False,
        "decision_record_path": "control/DECISION_LOG.md",
        "reviewed_by_or_process": "pytest",
    }
    payload["blockers"] = []

    with pytest.raises(RuntimeError, match="explicit_control_layer_promotion_decision=true"):
        validate_macro_regime_promotion_contract(_write(tmp_path, payload))


def test_authority_flags_must_remain_false(tmp_path: Path):
    payload = _payload()
    payload["authority"]["lane_scoring_authority"] = True

    with pytest.raises(RuntimeError, match="authority.lane_scoring_authority must remain false"):
        validate_macro_regime_promotion_contract(_write(tmp_path, payload))
