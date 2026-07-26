from __future__ import annotations

import json
from pathlib import Path

from runtime.report_portfolio_integrity_contract import (
    apply_report_portfolio_integrity,
    validate_report_portfolio_integrity,
)

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "output/runtime/etf_report_state_20260724_20260726_132731.json"
EN_PATH = ROOT / "output/weekly_analysis_pro_260724_06.md"
NL_PATH = ROOT / "output/weekly_analysis_pro_nl_260724_06.md"


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_exact_july24_reports_are_repaired_and_validate() -> None:
    state = _state()
    en = apply_report_portfolio_integrity(EN_PATH.read_text(encoding="utf-8"), state, "en")
    nl = apply_report_portfolio_integrity(NL_PATH.read_text(encoding="utf-8"), state, "nl")

    validate_report_portfolio_integrity(en, state, "en")
    validate_report_portfolio_integrity(nl, state, "nl")

    assert "PPA and PAVE remain replaceable" not in en
    assert "PPA en PAVE blijven vervangbaar" not in nl
    assert "SPY plus SMH" not in en
    assert "SPY plus SMH" not in nl
    assert "PPA and ITA are defense-watchlist candidates only" in en
    assert "PPA en ITA zijn uitsluitend defensie-volglijstkandidaten" in nl
    assert "Non-held watchlist" in en
    assert "Niet-aangehouden volglijst" in nl


def test_continuity_pnl_uses_same_attribution_basis_as_performance_section() -> None:
    state = _state()
    en = apply_report_portfolio_integrity(EN_PATH.read_text(encoding="utf-8"), state, "en")
    nl = apply_report_portfolio_integrity(NL_PATH.read_text(encoding="utf-8"), state, "nl")

    # These values are the ledger-derived values already shown in section 7A,
    # not the stale snapshot values previously repeated in continuity input.
    for ticker, expected in {
        "CIBR": "-3.60",
        "IEFA": "1.06",
        "PAVE": "2.24",
        "XBI": "-2.78",
        "XLU": "7.85",
        "XLV": "1.10",
    }.items():
        en_row = next(line for line in en.splitlines() if line.startswith(f"| {ticker} |") and "Original thesis" not in line)
        nl_row = next(line for line in nl.splitlines() if line.startswith(f"| {ticker} |") and "Oorspronkelijke thesis" not in line)
        assert expected in en_row
        assert expected in nl_row


def test_fresh_valuation_and_macro_wording_are_not_stale() -> None:
    state = _state()
    en = apply_report_portfolio_integrity(EN_PATH.read_text(encoding="utf-8"), state, "en")
    nl = apply_report_portfolio_integrity(NL_PATH.read_text(encoding="utf-8"), state, "nl")

    assert "2026-07-24 | 107189.79 | Portfolio valuation based on confirmed closing prices and official holdings" in en
    assert "2026-07-24 | 107189.79 | Waardering op basis van bevestigde slotkoersen en officiële posities" in nl
    assert "weekly observations" not in en
    assert "wekelijkse meetmomenten" not in nl
    assert "ECB stance: On hold after June tightening / data-dependent" in en
    assert "ECB-houding: Ongewijzigd na de verkrapping in juni / datagedreven" in nl


def test_zero_action_report_has_no_stale_rotation_or_internal_reason_codes() -> None:
    state = _state()
    assert not state.get("trade_intents")

    en = apply_report_portfolio_integrity(EN_PATH.read_text(encoding="utf-8"), state, "en")
    nl = apply_report_portfolio_integrity(NL_PATH.read_text(encoding="utf-8"), state, "nl")

    for report in (en, nl):
        lower = report.lower()
        assert "rotation limit reached" not in lower
        assert "rotatielimiet bereikt" not in lower
        assert "negative pnl gt" not in lower
        assert "loss and sub4 forced reunderwrite" not in lower
        assert "dfen" not in report[report.find("## 12.") : report.find("## 15.")]


def test_contract_is_idempotent_for_exact_reports() -> None:
    state = _state()
    en_once = apply_report_portfolio_integrity(EN_PATH.read_text(encoding="utf-8"), state, "en")
    en_twice = apply_report_portfolio_integrity(en_once, state, "en")
    nl_once = apply_report_portfolio_integrity(NL_PATH.read_text(encoding="utf-8"), state, "nl")
    nl_twice = apply_report_portfolio_integrity(nl_once, state, "nl")
    assert en_twice == en_once
    assert nl_twice == nl_once


def test_nonheld_defense_tickers_remain_allowed_only_as_explicit_watchlist_research() -> None:
    state = _state()
    assert "PPA" not in {row["ticker"] for row in state["positions"]}
    assert "ITA" not in {row["ticker"] for row in state["positions"]}

    nl = apply_report_portfolio_integrity(NL_PATH.read_text(encoding="utf-8"), state, "nl")
    risk_section = nl[nl.index("## 5.") : nl.index("## 6.")]
    action_section = nl[nl.index("## 12.") : nl.index("## 15.")]
    radar_section = nl[nl.index("## 4.") : nl.index("## 4A.")]

    assert "PPA" not in risk_section
    assert "PPA" not in action_section
    assert "PPA" in radar_section
    assert "Niet-aangehouden volglijst" in radar_section
