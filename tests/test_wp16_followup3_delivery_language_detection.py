from __future__ import annotations

from pathlib import Path

from tools.validate_etf_client_surface_clean import _language_for_path


def test_wp16_followup3_classifies_dutch_delivery_html_as_dutch() -> None:
    assert _language_for_path(Path("weekly_analysis_pro_nl_260611_05_delivery.html")) == "nl"


def test_wp16_followup3_classifies_english_delivery_html_as_english() -> None:
    assert _language_for_path(Path("weekly_analysis_pro_260611_05_delivery.html")) == "en"
