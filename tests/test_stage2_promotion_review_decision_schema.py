from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_decision_schema as validator


def _valid_artifact() -> dict:
    return copy.deepcopy(validator.valid_artifact())


def test_production_schema_validates() -> None:
    validator.validate_schema_file()


def test_valid_synthetic_artifact_passes() -> None:
    validator.validate_artifact(_valid_artifact(), require_expected_sources=True)


def test_missing_required_top_level_field_fails() -> None:
    payload = _valid_artifact()
    payload.pop("decision_scope")

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_forbidden_promoted_decision_status_fails() -> None:
    payload = _valid_artifact()
    payload["decision_status"] = "promoted"

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_forbidden_fundable_decision_status_fails() -> None:
    payload = _valid_artifact()
    payload["decision_status"] = "fundable"

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_false_authority_field_set_true_fails() -> None:
    payload = _valid_artifact()
    payload["authority"]["delivery_authority"] = True

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_missing_decision_artifact_only_fails() -> None:
    payload = _valid_artifact()
    payload["authority"].pop("decision_artifact_only")

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_missing_wp34_design_source_evidence_fails() -> None:
    payload = _valid_artifact()
    payload["source_evidence"].pop("decision_artifact_design")

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload, require_expected_sources=True)


def test_raw_driver_id_in_rationale_fails() -> None:
    payload = _valid_artifact()
    payload["decision_rationale"] = [
        {"code": "raw_driver", "severity": "blocker", "summary": "This rationale mentions driver_id."}
    ]

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_fundable_in_rationale_fails() -> None:
    payload = _valid_artifact()
    payload["decision_rationale"] = [
        {"code": "bad_claim", "severity": "blocker", "summary": "This rationale claims the lane is fundable."}
    ]

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_artifact(payload)


def test_schema_with_additional_properties_not_false_fails() -> None:
    schema = copy.deepcopy(validator._load_json(validator.DEFAULT_SCHEMA_PATH))
    schema["additionalProperties"] = True

    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        validator.validate_schema_definition(schema)


def test_cli_prints_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_decision_schema.py"])
    validator.main()

    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_DECISION_SCHEMA_OK" in out
