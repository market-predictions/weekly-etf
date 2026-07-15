from __future__ import annotations

from runtime.decision_cockpit_html import (
    decision_cockpit_html_from_markdown,
    decision_cockpit_items_from_markdown,
)


def test_english_delivery_cockpit_is_derived_from_executed_markdown() -> None:
    markdown = """## 2A. Decision cockpit

- **This week:** Guarded model rotation executed and persisted: reduced URNM and added XBI.
- **Main active risk:** SMH concentration remains above the soft position cap.

## 3. Regime Dashboard
"""
    title, items = decision_cockpit_items_from_markdown(markdown)
    html = decision_cockpit_html_from_markdown(markdown)
    assert title == "Decision cockpit"
    assert items[0].startswith("This week: Guarded model rotation executed")
    assert "URNM" in html and "XBI" in html
    assert "no portfolio action" not in html.lower()


def test_dutch_delivery_cockpit_is_derived_from_executed_markdown() -> None:
    markdown = """## 2A. Besliscockpit

- **Deze week:** Bewaakte modelrotatie uitgevoerd en verwerkt: URNM verlaagd en XBI toegevoegd.
- **Belangrijkste actieve risico:** SMH-concentratie blijft boven de zachte positielimiet.

## 3. Regime-dashboard
"""
    title, items = decision_cockpit_items_from_markdown(markdown)
    html = decision_cockpit_html_from_markdown(markdown)
    assert title == "Besliscockpit"
    assert items[0].startswith("Deze week: Bewaakte modelrotatie uitgevoerd")
    assert "URNM" in html and "XBI" in html
    assert "geen portefeuilleactie" not in html.lower()


def test_delivery_cockpit_returns_empty_when_section_is_absent() -> None:
    assert decision_cockpit_html_from_markdown("## 1. Executive Summary") == ""
