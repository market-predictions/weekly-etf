from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_explicit_decision_design_review as validator

DOC = Path("control/STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_ARTIFACT_DESIGN_REVIEW.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_design_review_document_exists() -> None:
    assert DOC.exists()


def test_design_review_states_required_boundary_phrases() -> None:
    text = _text()
    for phrase in validator.REQUIRED_PHRASES:
        assert phrase in text


def test_design_review_separates_four_layers() -> None:
    text = _text()
    for section in validator.REQUIRED_SECTIONS:
        assert section in text


def test_design_review_references_all_required_evidence() -> None:
    text = _text()
    for evidence in validator.REQUIRED_EVIDENCE:
        assert evidence in text


def test_design_review_has_required_outcomes() -> None:
    text = _text()
    for outcome in validator.REQUIRED_OUTCOMES:
        assert outcome in text


def test_design_review_requires_future_explicit_control_layer_decision() -> None:
    assert "future explicit control-layer decision" in _text()


def test_design_review_requires_separate_future_implementation_package() -> None:
    assert "separate future implementation package" in _text()


def test_validator_rejects_planted_forbidden_status() -> None:
    bad_status = "pro" + "moted"
    text = _text().replace("review_status: design_review_complete_not_promoted", f"review_status: {bad_status}")
    with pytest.raises(RuntimeError, match="explicit decision design review failed"):
        validator.validate_text(text)


def test_validator_rejects_missing_evidence_reference() -> None:
    text = _text().replace("tools/validate_stage2_promotion_review_decision_hardening.py", "")
    with pytest.raises(RuntimeError, match="explicit decision design review failed"):
        validator.validate_text(text)


def test_cli_validator_prints_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_explicit_decision_design_review.py"])
    validator.main()
    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_DESIGN_REVIEW_OK" in out
