from __future__ import annotations

from pathlib import Path

from runtime.wp16_followup2_cleanup import clean_residual_text, residual_failures
from tools.validate_etf_client_surface_clean import _apply_nl_equity_curve_guard


def test_wp16_followup2_cleans_stale_non_us_exposure_copy() -> None:
    text = "\n".join([
        "Watchlist only; non-U.S. exposure remains a diversification gap.",
        "Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof.",
    ])

    cleaned = clean_residual_text(text)

    assert "diversification gap" not in cleaned
    assert "diversificatiekloof" not in cleaned
    assert "IEFA now provides non-U.S. developed-market exposure" in cleaned
    assert "IEFA biedt nu blootstelling" in cleaned
    assert residual_failures(cleaned) == []


def test_wp16_followup2_translates_dutch_regime_memory_sentence() -> None:
    text = "Risk-on growth has persisted for 23 run(s); transition state is stable, breadth is improving, and cross-asset confirmation is mixed."

    cleaned = clean_residual_text(text)

    assert "Risk-on growth has persisted" not in cleaned
    assert "Risk-on groei houdt al 23 runs aan" in cleaned
    assert residual_failures(cleaned) == []


def test_wp16_followup2_injects_dutch_equity_curve_guard_once() -> None:
    path = Path("weekly_analysis_pro_nl_260611_03.md")
    text = "## 7. Portefeuillecurve en portefeuilleontwikkeling\n\n`EQUITY_CURVE_CHART_PLACEHOLDER`"

    guarded = _apply_nl_equity_curve_guard(text, path)
    guarded_again = _apply_nl_equity_curve_guard(guarded, path)

    assert guarded.count("wp16-nl-equity-curve-guard") == 1
    assert guarded == guarded_again
