from __future__ import annotations

from runtime.client_facing_sanitizer import sanitize_client_facing_html


def test_english_delivery_html_position_change_heading_is_reflected_not_executed() -> None:
    html = "<html><body><h2>Position Changes Executed This Run</h2></body></html>"

    cleaned = sanitize_client_facing_html(html, md_text="# Weekly ETF Review\n## 1. Executive Summary\n## 2. Portfolio Action Snapshot", language="en")

    assert "Position Changes Executed This Run" not in cleaned
    assert "Position Changes Reflected in Official State" in cleaned


def test_dutch_delivery_html_position_change_heading_is_reflected_not_in_deze_run() -> None:
    html = "<html><body><h2>Positiewijzigingen in deze run</h2></body></html>"

    cleaned = sanitize_client_facing_html(html, md_text="# Wekelijkse ETF-review\n## 1. Kernsamenvatting\n## 2. Portefeuille-acties", language="nl")

    assert "Positiewijzigingen in deze run" not in cleaned
    assert "Positiewijzigingen verwerkt in de officiële portefeuillestaat" in cleaned
