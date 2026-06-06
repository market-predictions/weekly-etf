import json
from pathlib import Path

import pytest

from runtime.build_macro_old_vs_new_review_package import build_review_package
from tools.validate_macro_old_vs_new_review_package import validate_macro_old_vs_new_review_package

PILOT = Path("output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json")


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "macro_review.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_review_package_from_wp7_pilot(tmp_path: Path):
    artifact = build_review_package(PILOT, tmp_path)
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    assert payload["artifact_type"] == "macro_old_vs_new_review_package"
    assert payload["review_status"] == "ready_for_narrative_promotion_review"
    assert payload["wp2_validation_status"] == "passed"
    assert payload["wp3_promotion_status"] == "not_promoted"
    assert payload["authority"]["production_report_narrative_authority"] is False
    assert payload["authority"]["portfolio_action_authority"] is False
    assert payload["authority"]["lane_scoring_authority"] is False
    assert payload["authority"]["fundability_authority"] is False
    assert payload["authority"]["funding_authority"] is False
    assert payload["authority"]["portfolio_mutation"] is False


def test_validator_accepts_generated_review_package(tmp_path: Path):
    artifact = build_review_package(PILOT, tmp_path)
    validate_macro_old_vs_new_review_package(artifact)


def test_ready_status_requires_all_criteria_pass(tmp_path: Path):
    artifact = build_review_package(PILOT, tmp_path)
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["review_criteria"]["clarity"]["passed"] = False
    with pytest.raises(RuntimeError, match="ready status requires all criteria to pass"):
        validate_macro_old_vs_new_review_package(_write(tmp_path, payload))


def test_authority_escalation_is_blocked(tmp_path: Path):
    artifact = build_review_package(PILOT, tmp_path)
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["authority"]["portfolio_action_authority"] = True
    with pytest.raises(RuntimeError, match="authority.portfolio_action_authority must remain false"):
        validate_macro_old_vs_new_review_package(_write(tmp_path, payload))


def test_keep_shadow_only_is_allowed_when_criteria_fail(tmp_path: Path):
    artifact = build_review_package(PILOT, tmp_path)
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["review_status"] = "keep_shadow_only"
    payload["review_criteria"]["clarity"]["passed"] = False
    validate_macro_old_vs_new_review_package(_write(tmp_path, payload))
