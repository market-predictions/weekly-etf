from __future__ import annotations

import csv
import json

import pytest

from runtime.portfolio_rotation_engine import (
    build_decisions,
    candidate_reviews,
    capital_release_score,
)
from runtime.rotation_state_authority import (
    build_current_run_valuation_state,
    reconstruct_average_entry_local,
    refresh_scorecard_rows,
    validate_current_run_authority,
)


def _pricing() -> dict:
    return {
        "run_id": "20260715_164128",
        "requested_close_date": "2026-07-14",
        "fx_basis": {"rate": 1.1421},
        "price_results": [
            {
                "symbol": "URNM",
                "selected_close": 51.59,
                "status": "fresh_exact_unverified",
                "pricing_tier": "valuation_grade",
                "currency": "USD",
                "source": "twelve_data",
                "returned_close_date": "2026-07-14",
            }
        ],
    }


def _portfolio() -> dict:
    return {
        "cash_eur": 1936.52,
        "positions": [
            {
                "ticker": "URNM",
                "shares": 171,
                "avg_entry_local": 67.50,
                "total_score": 3.70,
                "suggested_action": "Hold",
                "fresh_cash_test": "Hold / wait for confirmation",
                "portfolio_role": "Strategic energy",
            }
        ],
    }


def _current_state() -> dict:
    return build_current_run_valuation_state(_portfolio(), _pricing())


def test_current_run_valuation_builds_position() -> None:
    state = _current_state()
    assert len(state["positions"]) == 1


def test_current_run_valuation_recomputes_pnl() -> None:
    position = _current_state()["positions"][0]
    assert position["pnl_pct"] == -23.57


def test_current_run_valuation_records_pnl_basis() -> None:
    position = _current_state()["positions"][0]
    assert position["pnl_basis"] == "current_close_vs_avg_entry"


def test_current_run_valuation_recomputes_nav_and_weight() -> None:
    state = _current_state()
    position = state["positions"][0]
    assert state["portfolio"]["total_portfolio_value_eur"] > 0
    assert position["current_weight_pct"] > 0


def test_scorecard_refresh_blocks_stale_or_inconsistent_pnl() -> None:
    state = _current_state()
    previous = [
        {
            "report_date": "2026-05-05",
            "ticker": "URNM",
            "pnl_pct": "-0.55",
            "weeks_replaceable": "0",
            "total_score": "3.70",
            "implementation_score": "3.50",
            "fresh_cash_test": "Hold / wait for confirmation",
        }
    ]
    rows = refresh_scorecard_rows(
        previous, state["positions"], "2026-07-14", "current_run:test"
    )
    assert rows[0]["report_date"] == "2026-07-14"
    assert rows[0]["pnl_pct"] == "-23.57"
    result = validate_current_run_authority(
        rows, state["positions"], "2026-07-14"
    )
    assert result["validated_holding_count"] == 1

    rows[0]["pnl_pct"] = "-0.55"
    with pytest.raises(RuntimeError, match="pnl_mismatch"):
        validate_current_run_authority(
            rows, state["positions"], "2026-07-14"
        )


def test_deep_loss_sub4_position_clears_release_threshold() -> None:
    position = {"ticker": "URNM", "pnl_pct": -23.57, "total_score": 3.70}
    row = {
        "fresh_cash_test": "Hold / wait for confirmation",
        "replaceable_status": "None",
        "contribution_quality": "Material drag",
        "implementation_score": "3.50",
    }
    score, reasons, role = capital_release_score(position, row)
    assert role == "fail"
    assert score >= 80
    assert "loss_and_sub4_forced_reunderwrite" in reasons


def test_alternative_etf_is_independent_replacement_candidate() -> None:
    lane = {
        "lane_name": "Cybersecurity resilience",
        "primary_etf": "CIBR",
        "alternative_etf": "BUG",
        "total_score": 4.97,
        "portfolio_differentiation": 5,
        "promoted_to_live_radar": True,
        "is_fundable_candidate": False,
        "primary_price_status": "fresh_exact_unverified",
        "alternative_price_status": "fresh_exact_unverified",
        "primary_pricing_tier": "valuation_grade",
        "alternative_pricing_tier": "valuation_grade",
        "primary_pricing_source": "twelve_data",
        "alternative_pricing_source": "twelve_data",
    }
    metrics = {
        "CIBR": {
            "return_1m_pct": 8.70,
            "return_3m_pct": 47.71,
            "trend_quality": 5,
            "rs_vs_spy_1m_pct": 7.26,
            "rs_vs_spy_3m_pct": 39.36,
            "max_drawdown_3m_pct": -11.74,
            "volatility_3m_pct": 32.82,
            "tradability_status": "pass",
        },
        "BUG": {
            "return_1m_pct": 19.79,
            "return_3m_pct": 68.56,
            "trend_quality": 5,
            "rs_vs_spy_1m_pct": 18.35,
            "rs_vs_spy_3m_pct": 60.21,
            "max_drawdown_3m_pct": -13.59,
            "volatility_3m_pct": 41.25,
            "tradability_status": "pass",
        },
    }
    candidates = candidate_reviews([lane], metrics, {"CIBR"})
    bug = next(row for row in candidates if row["candidate"] == "BUG")
    assert bug["candidate_role"] == "alternative"
    assert bug["direct_rs_vs_holding"] == "CIBR"
    assert bug["direct_rs_vs_holding_3m_pct"] == 20.85
    assert bug["is_fundable_candidate"] is True


def test_failed_holding_can_rotate_to_general_fundable_candidate() -> None:
    incumbents = [
        {
            "ticker": "URNM",
            "current_weight_pct": 7.0,
            "release_score": 90,
            "release_reasons": ["loss_and_sub4_forced_reunderwrite"],
            "role_validity": "fail",
            "weeks_replaceable": 0,
        }
    ]
    candidates = [
        {
            "candidate": "XBI",
            "candidate_role": "primary",
            "destination_score": 100,
            "is_fundable_candidate": True,
            "funding_scope": "general",
            "price_status": "fresh_exact_unverified",
            "pricing_tier": "valuation_grade",
            "direct_rs_vs_holding": "",
            "direct_rs_vs_holding_1m_pct": 0.0,
            "direct_rs_vs_holding_3m_pct": 0.0,
        }
    ]
    decisions, targets, intents = build_decisions(
        incumbents, candidates, 110000.0, {"URNM"}
    )
    assert decisions[0]["action_code"] == "replace_partial"
    assert intents[0]["source_ticker"] == "URNM"
    assert intents[0]["destination_ticker"] == "XBI"
    assert intents[0]["delta_weight_pct"] == -5.0



def test_average_entry_reconstructed_from_execution_history(tmp_path) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    ledger = tmp_path / "etf_trade_ledger.csv"
    with ledger.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["ticker", "shares_delta", "source_report"])
        writer.writeheader()
        writer.writerow({"ticker": "TEST", "shares_delta": "10", "source_report": "runtime:output/runtime/etf_report_state_20260701_run1.json"})
        writer.writerow({"ticker": "TEST", "shares_delta": "5", "source_report": "runtime:output/runtime/etf_report_state_20260702_run2.json"})
    for name, shares_delta, price in (("etf_model_execution_20260701_run1.json", 10, 100.0), ("etf_model_execution_20260702_run2.json", 5, 110.0)):
        (runtime_dir / name).write_text(json.dumps({"execution_status": "executed", "shadow_positions": [{"ticker": "TEST", "shares_delta_this_run": shares_delta, "selected_close": price}]}), encoding="utf-8")
    avg_entry = reconstruct_average_entry_local("TEST", trade_ledger_path=ledger, runtime_dir=runtime_dir)
    assert avg_entry == 103.333333
    portfolio = {"cash_eur": 0.0, "positions": [{"ticker": "TEST", "shares": 15, "total_score": 4.0, "fresh_cash_test": "Hold"}]}
    pricing = {"requested_close_date": "2026-07-14", "fx_basis": {"rate": 1.0}, "price_results": [{"symbol": "TEST", "selected_close": 120.0, "status": "fresh_exact_unverified", "pricing_tier": "valuation_grade", "currency": "USD"}]}
    state = build_current_run_valuation_state(portfolio, pricing, trade_ledger_path=ledger, runtime_dir=runtime_dir)
    position = state["positions"][0]
    assert position["avg_entry_source"] == "model_execution_history"
    assert position["pnl_pct"] == 16.13


def test_destination_ranking_prefers_live_primary_over_alphabetical_tie() -> None:
    incumbents = [{"ticker": "URNM", "current_weight_pct": 7.0, "release_score": 90, "release_reasons": ["loss_and_sub4_forced_reunderwrite"], "role_validity": "fail", "weeks_replaceable": 0}]
    shared = {"destination_score": 100, "is_fundable_candidate": True, "funding_scope": "general", "price_status": "fresh_exact_unverified", "pricing_tier": "valuation_grade", "direct_rs_vs_holding": "", "direct_rs_vs_holding_1m_pct": 0.0, "direct_rs_vs_holding_3m_pct": 0.0, "relative_strength_score": 1.25}
    candidates = [{**shared, "candidate": "IAI", "candidate_role": "alternative", "promoted_to_live_radar": False, "total_score": 3.8, "avg_dollar_volume_3m": 20_000_000}, {**shared, "candidate": "XBI", "candidate_role": "primary", "promoted_to_live_radar": True, "total_score": 4.36, "avg_dollar_volume_3m": 1_300_000_000}]
    _, _, intents = build_decisions(incumbents, candidates, 110000.0, {"URNM"})
    assert intents[0]["destination_ticker"] == "XBI"
