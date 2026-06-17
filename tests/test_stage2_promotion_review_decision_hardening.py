from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_fixtures as fixture_validator
from tools import validate_stage2_promotion_review_decision_schema as schema_validator


def _artifact() -> dict:
    return copy.deepcopy(schema_validator.valid_artifact())


def test_hardening_validator_passes() -> None:
    hardening.run_hardening_checks()


def test_schema_validator_rejects_nested_authority_extra_property() -> None:
    payload = _artifact()
    payload["authority"]["extra"] = False
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_nested_source_evidence_extra_property() -> None:
    payload = _artifact()
    payload["source_evidence"]["extra"] = "control/extra.md"
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_review_note_extra_property() -> None:
    payload = _artifact()
    payload["decision_rationale"][0]["extra"] = "x"
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_non_object_review_note() -> None:
    payload = _artifact()
    payload["decision_rationale"] = ["not-an-object"]
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_invalid_severity() -> None:
    payload = _artifact()
    payload["decision_rationale"][0]["severity"] = "critical"
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_authority_boolean_as_string() -> None:
    payload = _artifact()
    payload["authority"]["delivery_authority"] = "false"
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_decision_status_whitespace_case_mutation() -> None:
    payload = _artifact()
    payload["decision_status"] = " Not_Promoted "
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_source_evidence_path_traversal() -> None:
    payload = _artifact()
    payload["source_evidence"]["review_schema"] = "../schemas/stage2_promotion_review.schema.json"
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_schema_validator_rejects_bad_generated_at_utc() -> None:
    payload = _artifact()
    payload["generated_at_utc"] = "2026-06-17 00:00:00"
    with pytest.raises(RuntimeError, match="decision schema validation failed"):
        hardening._validate_hardened_artifact(payload)


def test_fixture_validator_rejects_extra_manifest_entry_key() -> None:
    manifest = {
        "schema_version": "1.0",
        "fixture_set": "stage2_promotion_review_decision",
        "authority": dict(fixture_validator.REQUIRED_MANIFEST_AUTHORITY),
        "fixtures": [
            {
                "path": "fixtures/stage2_promotion_review_decision/pass_not_promoted.json",
                "expected": "pass",
                "expected_decision_status": "not_promoted",
                "extra": "x",
            }
        ],
    }
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        hardening._validate_hardened_manifest(manifest)


def test_cli_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_decision_hardening.py"])
    hardening.main()
    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_DECISION_HARDENING_OK" in out
