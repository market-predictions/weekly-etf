from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_schema as validator


def _valid_artifact() -> dict:
    return copy.deepcopy(validator.valid_artifact())


def test_valid_minimal_review_artifact_passes() -> None:
    validator.validate_artifact(_valid_artifact())


def test_missing_authority_block_fails() -> None:
    payload = _valid_artifact()
    payload.pop("authority")

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)


def test_any_authority_field_set_true_fails() -> None:
    payload = _valid_artifact()
    payload["authority"]["fundability_authority"] = True

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)


def test_missing_source_artifact_reference_fails() -> None:
    payload = _valid_artifact()
    payload["source_artifacts"].pop("pricing_audit")

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)


def test_forbidden_promoted_status_fails() -> None:
    payload = _valid_artifact()
    payload["review_status"] = "promoted"

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)


def test_forbidden_fundable_status_fails() -> None:
    payload = _valid_artifact()
    payload["review_status"] = "fundable"

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)


def test_missing_bilingual_alias_source_fails() -> None:
    payload = _valid_artifact()
    payload["source_artifacts"].pop("bilingual_aliases")

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)


def test_schema_file_itself_validates() -> None:
    validator.validate_schema_file(Path("schemas/stage2_promotion_review.schema.json"))


def test_validator_reports_field_bad_value_and_reason(capsys: pytest.CaptureFixture[str]) -> None:
    payload = _valid_artifact()
    payload["review_status"] = "promoted"

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_artifact(payload)

    out = capsys.readouterr().out
    assert "field=review_status" in out
    assert "value='promoted'" in out
    assert "reason=forbidden promotional status" in out
