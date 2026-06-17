from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import build_stage2_promotion_review_decision_sample as builder
from tools import validate_stage2_promotion_review_decision_sample_gate as gate
from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_schema as schema_validator


def _sample() -> dict:
    return copy.deepcopy(builder.build_sample())


def test_sample_builder_returns_deterministic_artifact() -> None:
    assert builder.build_sample() == builder.build_sample()


def test_sample_artifact_validates_against_decision_schema() -> None:
    schema_validator.validate_artifact(_sample(), require_expected_sources=True)


def test_sample_artifact_passes_hardening_checks() -> None:
    hardening._validate_hardened_artifact(_sample())


def test_sample_artifact_has_decision_status_not_promoted() -> None:
    assert _sample()["decision_status"] == "not_promoted"


def test_sample_artifact_has_exact_authority_block() -> None:
    assert _sample()["authority"] == schema_validator.REQUIRED_AUTHORITY


def test_sample_artifact_has_exact_source_evidence_references() -> None:
    assert _sample()["source_evidence"] == schema_validator.EXPECTED_SOURCE_EVIDENCE


def test_sample_artifact_has_deterministic_generated_at_utc() -> None:
    assert _sample()["generated_at_utc"] == "2026-06-17T00:00:00Z"


def test_sample_builder_does_not_write_by_default() -> None:
    gate.validate_no_default_write()


def test_sample_builder_rejects_output_write_path() -> None:
    with pytest.raises(ValueError):
        builder.validate_write_path(Path("output/sample.json"))


def test_sample_builder_rejects_absolute_write_path() -> None:
    with pytest.raises(ValueError):
        builder.validate_write_path(Path("/tmp/sample.json"))


def test_sample_builder_rejects_traversal_write_path() -> None:
    with pytest.raises(ValueError):
        builder.validate_write_path(Path("../sample.json"))


def test_sample_gate_rejects_sample_with_authority_true() -> None:
    sample = _sample()
    sample["authority"]["delivery_authority"] = True
    with pytest.raises(RuntimeError, match="sample gate failed"):
        gate.validate_sample(sample)


def test_sample_gate_rejects_sample_with_extra_top_level_field() -> None:
    sample = _sample()
    sample["extra"] = True
    with pytest.raises(RuntimeError, match="sample gate failed"):
        gate.validate_sample(sample)


def test_sample_gate_rejects_sample_with_raw_driver_id_text() -> None:
    sample = _sample()
    sample["decision_rationale"][0]["summary"] = "This text contains driver_id."
    with pytest.raises(RuntimeError, match="sample gate failed"):
        gate.validate_sample(sample)


def test_sample_gate_rejects_sample_with_promotional_text() -> None:
    sample = _sample()
    sample["decision_rationale"][0]["summary"] = "This text says recommended."
    with pytest.raises(RuntimeError, match="sample gate failed"):
        gate.validate_sample(sample)


def test_sample_gate_cli_prints_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_decision_sample_gate.py"])
    gate.main()
    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_DECISION_SAMPLE_GATE_OK" in out


def test_allowed_generated_sample_write_with_tmp_override(tmp_path: Path) -> None:
    target = tmp_path / "sample.json"
    builder.write_sample(target, allow_tmp=True)
    assert target.exists()
