from __future__ import annotations

from pathlib import Path

from tools.validate_etf_pdf_polish_contract import latest_delivery_html


def test_latest_delivery_html_prefers_explicit_current_report(monkeypatch, tmp_path: Path) -> None:
    stale = tmp_path / "weekly_analysis_pro_260615_delivery.html"
    current_report = tmp_path / "weekly_analysis_pro_260615_02.md"
    current_delivery = tmp_path / "weekly_analysis_pro_260615_02_delivery.html"

    stale.write_text("stale", encoding="utf-8")
    current_report.write_text("current", encoding="utf-8")
    current_delivery.write_text("current delivery", encoding="utf-8")
    monkeypatch.setenv("MRKT_RPRTS_EXPLICIT_REPORT_PATH", str(current_report))

    assert latest_delivery_html(tmp_path, language="en") == current_delivery


def test_latest_delivery_html_prefers_explicit_current_dutch_report(monkeypatch, tmp_path: Path) -> None:
    stale = tmp_path / "weekly_analysis_pro_nl_260615_delivery.html"
    current_report = tmp_path / "weekly_analysis_pro_nl_260615_02.md"
    current_delivery = tmp_path / "weekly_analysis_pro_nl_260615_02_delivery.html"

    stale.write_text("stale", encoding="utf-8")
    current_report.write_text("current", encoding="utf-8")
    current_delivery.write_text("current delivery", encoding="utf-8")
    monkeypatch.setenv("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", str(current_report))

    assert latest_delivery_html(tmp_path, language="nl") == current_delivery
