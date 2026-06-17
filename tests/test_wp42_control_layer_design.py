from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import wp42_validator as validator

DOC = Path("control/STAGE2_CONTROL_LAYER_PACKAGE_DESIGN.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_design_document_exists() -> None:
    assert DOC.exists()


def test_design_document_states_required_boundary_phrases() -> None:
    text = _text()
    for phrase in validator.REQUIRED_PHRASES:
        assert phrase in text


def test_design_document_separates_four_layers() -> None:
    text = _text()
    for section in validator.REQUIRED_SECTIONS:
        assert section in text


def test_design_document_defines_allowed_future_statuses() -> None:
    text = _text()
    for status in validator.ALLOWED_STATUSES:
        assert status in text


def test_design_document_defines_forbidden_future_statuses() -> None:
    text = _text()
    for status in validator.FORBIDDEN_STATUSES:
        assert status in text


def test_design_document_references_wp34_through_wp41_evidence() -> None:
    text = _text()
    for evidence in validator.REQUIRED_EVIDENCE:
        assert evidence in text


def test_design_document_defines_exact_future_authority_defaults() -> None:
    text = _text()
    for authority in validator.REQUIRED_AUTHORITY_DEFAULTS:
        assert authority in text


def test_design_document_requires_future_control_layer_decision_package() -> None:
    assert "A future explicit control-layer decision package is required." in _text()


def test_design_document_requires_separate_future_implementation_package() -> None:
    assert "A separate future implementation package is required." in _text()


def test_validator_rejects_missing_evidence_reference() -> None:
    text = _text().replace("tools/wp41_validator.py", "")
    with pytest.raises(RuntimeError, match="control-layer decision package design failed"):
        validator.validate_text(text)


def test_validator_rejects_missing_authority_default() -> None:
    text = _text().replace("delivery_authority: false", "")
    with pytest.raises(RuntimeError, match="control-layer decision package design failed"):
        validator.validate_text(text)


def test_validator_rejects_forbidden_status_used_as_allowed_status() -> None:
    bad_status = "production" + "_ready"
    text = _text().replace("not_promoted", bad_status, 1)
    with pytest.raises(RuntimeError, match="control-layer decision package design failed"):
        validator.validate_text(text)


def test_cli_validator_prints_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["wp42_validator.py"])
    validator.main()
    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_EXPLICIT_CONTROL_LAYER_DECISION_PACKAGE_DESIGN_OK" in out
