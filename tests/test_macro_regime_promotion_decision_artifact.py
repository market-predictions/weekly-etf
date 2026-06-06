import json
from pathlib import Path

import pytest

from tools.validate_macro_regime_promotion_contract import validate_macro_regime_promotion_contract

ARTIFACT_PATH = Path("output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json")


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "macro_regime_promotion_decision.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_wp9_promotion_decision_artifact_validates():
    validate_macro_regime_promotion_contract(ARTIFACT_PATH)


def test_wp9_artifact_records_safe_not_promoted_status():
    payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert payload["status"] == "not_promoted"
    assert payload["client_facing_narrative_authority"] is False
    assert payload["production_report_narrative_authority"] is False
    assert payload["promotion_decision"]["control_layer_decision"] == "not_promoted"
    assert payload["promotion_decision"]["explicit_control_layer_promotion_decision"] is False
    assert "macro regime remains shadow-only" in payload["blockers"]


def test_wp9_artifact_preserves_permanent_authority_boundaries():
    payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    for key in (
        "portfolio_action_authority",
        "lane_scoring_authority",
        "fundability_authority",
        "funding_authority",
        "portfolio_mutation",
    ):
        assert payload["authority"][key] is False


def test_unsafe_promotion_copy_is_blocked(tmp_path: Path):
    payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    payload["status"] = "promoted_to_report_narrative_authority"
    payload["client_facing_narrative_authority"] = True
    payload["production_report_narrative_authority"] = True
    payload["required_approvals"]["methodology_approved"] = False
    payload["promotion_decision"]["control_layer_decision"] = "promote_to_report_narrative_authority"
    payload["promotion_decision"]["explicit_control_layer_promotion_decision"] = True
    payload["blockers"] = []

    with pytest.raises(RuntimeError, match="methodology_approved=true"):
        validate_macro_regime_promotion_contract(_write(tmp_path, payload))
