from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_macro_thesis_bilingual_aliases as validator


def _write_aliases(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "macro_thesis_bilingual_aliases.yml"
    path.write_text(body, encoding="utf-8")
    return path


def _valid_minimal() -> str:
    return """
version: 1
purpose: "Test aliases"
concepts:
  macro_context:
    en: "Macro context"
    nl: "Macrocontext"
    client_safe: true
"""


def test_valid_minimal_alias_source_passes(tmp_path: Path) -> None:
    validator.validate_alias_file(_write_aliases(tmp_path, _valid_minimal()))


def test_missing_dutch_alias_fails(tmp_path: Path) -> None:
    path = _write_aliases(
        tmp_path,
        """
version: 1
concepts:
  macro_context:
    en: "Macro context"
    client_safe: true
""",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_alias_file(path)


def test_missing_english_alias_fails(tmp_path: Path) -> None:
    path = _write_aliases(
        tmp_path,
        """
version: 1
concepts:
  macro_context:
    nl: "Macrocontext"
    client_safe: true
""",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_alias_file(path)


def test_stage2_shadow_alias_value_fails(tmp_path: Path) -> None:
    path = _write_aliases(
        tmp_path,
        """
version: 1
concepts:
  macro_context:
    en: "stage_2_fundable_ready_shadow"
    nl: "Macrocontext"
    client_safe: true
""",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_alias_file(path)


def test_driver_id_alias_value_fails(tmp_path: Path) -> None:
    path = _write_aliases(
        tmp_path,
        """
version: 1
concepts:
  macro_context:
    en: "driver_id context"
    nl: "Macrocontext"
    client_safe: true
""",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_alias_file(path)


def test_recommendation_or_fundability_authority_alias_fails(tmp_path: Path) -> None:
    path = _write_aliases(
        tmp_path,
        """
version: 1
concepts:
  macro_context:
    en: "Recommendation and fundability authority"
    nl: "Macrocontext"
    client_safe: true
""",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_alias_file(path)


def test_failure_report_identifies_concept_language_and_reason(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _write_aliases(
        tmp_path,
        """
version: 1
concepts:
  macro_context:
    en: "stage_2_fundable_ready_shadow"
    nl: "Macrocontext"
    client_safe: true
""",
    )

    with pytest.raises(RuntimeError, match="validation failed"):
        validator.validate_alias_file(path)

    out = capsys.readouterr().out
    assert "concept=macro_context" in out
    assert "language=en" in out
    assert "stage_2_fundable_ready_shadow" in out
    assert "reason=" in out


def test_production_alias_source_validates() -> None:
    validator.validate_alias_file(Path("config/macro_thesis_bilingual_aliases.yml"))
