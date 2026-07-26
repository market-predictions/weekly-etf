from __future__ import annotations

from runtime.apply_nl_localization import _clean_runtime_artifacts
from runtime.macro_report_surface import POLICY_AREA_NL, STANCE_NL, _client_safe_nl


def test_latest_ecb_stance_and_policy_area_have_native_dutch_labels() -> None:
    assert STANCE_NL["On hold after June tightening / data-dependent"] == "Ongewijzigd na de verkrapping in juni / datagedreven"
    assert POLICY_AREA_NL["ECB rate-policy hold"] == "ECB-rente ongewijzigd"


def test_regime_memory_and_decision_rule_are_fully_localized() -> None:
    summary = _client_safe_nl(
        "Risk-on growth has persisted across 8 weekly observation(s); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed."
    )
    decision = _client_safe_nl(
        "Do not rotate aggressively unless a regime shift persists across at least two distinct report dates or cross-asset confirmation becomes broad."
    )
    assert summary == "Risk-on groei houdt al 8 wekelijkse observaties aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-assetbevestiging blijft gemengd."
    assert decision == "Roteer niet agressief tenzij een regimeverschuiving op minstens twee afzonderlijke rapportdatums aanhoudt of cross-assetbevestiging breed wordt."


def test_latest_ecb_implication_and_catalyst_are_fully_localized() -> None:
    implication = _client_safe_nl(
        "IEFA exposure is already material; further allocation still requires relative-strength, pricing and portfolio-concentration confirmation."
    )
    catalyst = _client_safe_nl(
        "The ECB kept its key interest rates unchanged on 23 July 2026 and retained a data-dependent, meeting-by-meeting approach; this is descriptive policy context and does not override portfolio gates."
    )
    assert implication == "IEFA is al een materiële positie; verdere allocatie vraagt nog bevestiging in relatieve sterkte, prijsbasis en portefeuilleconcentratie."
    assert catalyst == "De ECB hield de beleidsrentes op 23 juli 2026 ongewijzigd en bleef per vergadering datagedreven beslissen; dit is beschrijvende beleidscontext en vervangt geen portefeuillevoorwaarden."


def test_historical_valuation_comment_is_localized_on_native_dutch_surface() -> None:
    source = "Portfolio valuation based on confirmed prices and official holdings"
    assert _clean_runtime_artifacts(source) == "Waardering op basis van bevestigde slotkoersen en officiële posities"
