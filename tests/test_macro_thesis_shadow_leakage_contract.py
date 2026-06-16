from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_etf_macro_thesis_surface_leakage as validator


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_clean_current_style_report_text_passes(tmp_path: Path) -> None:
    report = _write(
        tmp_path / "weekly_analysis_pro_260616.md",
        """
        # Weekly ETF Pro Review

        The report describes current macro conditions. Portfolio actions still require pricing,
        relative-strength and position-discipline gates.
        """,
    )

    validator.validate_files([report])


def test_english_markdown_shadow_fundable_status_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    report = _write(
        tmp_path / "weekly_analysis_pro_260616.md",
        "# Weekly ETF Pro Review\nstage_2_fundable_ready_shadow should not be visible.\n",
    )

    with pytest.raises(RuntimeError, match="surface leakage detected"):
        validator.validate_files([report])

    out = capsys.readouterr().out
    assert str(report) in out
    assert "stage_2_fundable_ready_shadow" in out
    assert "shadow-only" in out or "shadow" in out


def test_dutch_markdown_stage2_confirmation_phrase_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    report = _write(
        tmp_path / "weekly_analysis_pro_nl_260616.md",
        "# Wekelijkse ETF-review\nStage-2 confirmation staat per ongeluk in de Nederlandse tekst.\n",
    )

    with pytest.raises(RuntimeError, match="surface leakage detected"):
        validator.validate_files([report])

    out = capsys.readouterr().out
    assert str(report) in out
    assert "Stage-2 confirmation" in out


def test_delivery_html_driver_catalog_artifact_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    html = _write(
        tmp_path / "weekly_analysis_pro_260616_delivery.html",
        "<html><body>Internal config/driver_catalog.yml leaked.</body></html>",
    )

    with pytest.raises(RuntimeError, match="surface leakage detected"):
        validator.validate_files([html])

    out = capsys.readouterr().out
    assert str(html) in out
    assert "driver_catalog" in out
    assert "internal macro/thesis configuration" in out


def test_current_client_files_include_clean_markdown_and_delivery_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(tmp_path / "weekly_analysis_pro_260616.md", "# Report\n")
    clean = _write(tmp_path / "weekly_analysis_pro_260616_clean.md", "# Clean report\n")
    html = _write(tmp_path / "weekly_analysis_pro_260616_delivery.html", "<html>Report</html>")
    nl_report = _write(tmp_path / "weekly_analysis_pro_nl_260616.md", "# Rapport\n")
    nl_clean = _write(tmp_path / "weekly_analysis_pro_nl_260616_clean.md", "# Schoon rapport\n")
    nl_html = _write(tmp_path / "weekly_analysis_pro_nl_260616_delivery.html", "<html>Rapport</html>")

    monkeypatch.delenv("MRKT_RPRTS_EXPLICIT_REPORT_PATH", raising=False)
    monkeypatch.delenv("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", raising=False)

    selected = validator.current_client_files(tmp_path)

    assert selected == [report, clean, html, nl_report, nl_clean, nl_html]


def test_explicit_report_path_selection_ignores_stale_lexicographic_delivery_html(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path / "weekly_analysis_pro_260615.md", "# Stale report\n")
    _write(
        tmp_path / "weekly_analysis_pro_260615_delivery.html",
        "<html><body>stage_2_fundable_ready_shadow in stale artifact</body></html>",
    )
    current = _write(tmp_path / "weekly_analysis_pro_260616_02.md", "# Current report\n")
    current_clean = _write(tmp_path / "weekly_analysis_pro_260616_02_clean.md", "# Current clean report\n")
    current_html = _write(tmp_path / "weekly_analysis_pro_260616_02_delivery.html", "<html><body>Current report</body></html>")

    monkeypatch.setenv("MRKT_RPRTS_EXPLICIT_REPORT_PATH", str(current))
    monkeypatch.delenv("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", raising=False)

    selected = validator.current_client_files(tmp_path)

    assert selected == [current, current_clean, current_html]
    validator.validate_files(selected)
