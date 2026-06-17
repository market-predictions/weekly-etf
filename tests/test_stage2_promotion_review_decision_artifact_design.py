from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_decision_artifact_design as validator

DESIGN_PATH = Path("control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md")


def _design_text() -> str:
    return DESIGN_PATH.read_text(encoding="utf-8")


def _write_design(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "design.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_production_design_validates() -> None:
    validator.validate_design_file(DESIGN_PATH)


def test_missing_design_only_wording_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("Design-only.", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_missing_no_live_artifact_wording_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("No live decision artifact is created.", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_missing_no_promotion_decision_wording_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("No Stage-2 promotion decision is made.", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_missing_authority_false_field_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("fundability_authority: false", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_missing_wp33_fixture_reference_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("fixtures/stage2_promotion_review/manifest.json", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_missing_leakage_validator_reference_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("tools/validate_etf_macro_thesis_surface_leakage.py", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_forbidden_now_promoted_wording_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text() + "\nStage-2 is now promoted.\n")

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_forbidden_fundable_current_status_wording_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text() + "\nStage-2 is fundable.\n")

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)


def test_missing_future_separate_implementation_package_requirement_fails(tmp_path: Path) -> None:
    path = _write_design(tmp_path, _design_text().replace("separate future implementation package", ""))

    with pytest.raises(RuntimeError, match="design validation failed"):
        validator.validate_design_file(path)
