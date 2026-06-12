from __future__ import annotations

from tools.validate_etf_client_surface_clean import _move_chart_before_pricing_disclosure


def test_chart_placeholder_moves_before_nl_price_block() -> None:
    placeholder = "`EQUITY_CURVE_CHART_PLACEHOLDER`"
    heading = "### Gebruikte slotkoersen in dit rapport"
    text = f"## 7. Portefeuillecurve\n\n| Datum | Waarde |\n|---|---:|\n| 2026-06-11 | 107747.59 |\n\n{heading}\n\n| Positie | Datum |\n|---|---|\n| SMH | 2026-06-11 |\n\n{placeholder}\n\n## 7A. Rendement"

    cleaned = _move_chart_before_pricing_disclosure(text, "nl")

    assert cleaned.count(placeholder) == 1
    assert cleaned.find(placeholder) < cleaned.find(heading)


def test_chart_placeholder_stays_when_already_before_price_block() -> None:
    placeholder = "`EQUITY_CURVE_CHART_PLACEHOLDER`"
    heading = "### Closing prices used in this report"
    text = f"## 7. Equity Curve\n\n{placeholder}\n\n{heading}\n"

    assert _move_chart_before_pricing_disclosure(text, "en") == text
