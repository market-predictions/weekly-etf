from __future__ import annotations

from tools.validate_etf_client_surface_clean import _move_chart_before_pricing_disclosure


def test_dutch_chart_moves_to_top_of_section_7_before_valuation_table() -> None:
    chart = "`EQUITY_CURVE_CHART_PLACEHOLDER`"
    section = "## 7. Portefeuillecurve en portefeuilleontwikkeling"
    pricing = "### Gebruikte slotkoersen in dit rapport"
    table = "| Datum | Portefeuillewaarde EUR | Opmerking |"
    text = f"{section}\n\nStartkapitaal (EUR): 100000.00\n\n{table}\n|---|---:|---|\n| 2026-06-11 | 107747.59 | Laatste waardering |\n\n{pricing}\n\n{chart}\n"

    cleaned = _move_chart_before_pricing_disclosure(text, "nl")

    assert cleaned.count(chart) == 1
    assert cleaned.find(section) < cleaned.find(chart) < cleaned.find(table) < cleaned.find(pricing)


def test_english_chart_still_moves_only_before_pricing_disclosure() -> None:
    chart = "`EQUITY_CURVE_CHART_PLACEHOLDER`"
    pricing = "### Closing prices used in this report"
    table = "| Date | Portfolio value (EUR) | Comment |"
    text = f"## 7. Equity Curve and Portfolio Development\n\n{table}\n|---|---:|---|\n| 2026-06-11 | 107747.59 | Latest value |\n\n{pricing}\n\n{chart}\n"

    cleaned = _move_chart_before_pricing_disclosure(text, "en")

    assert cleaned.count(chart) == 1
    assert cleaned.find(table) < cleaned.find(chart) < cleaned.find(pricing)
