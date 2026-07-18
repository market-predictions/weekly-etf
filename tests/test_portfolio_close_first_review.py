from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from runtime.build_portfolio_close_first_review import (
    build_evidence,
    decide,
    rank_sources,
    render,
)

FIXTURES = Path("fixtures/portfolio_close_first_review")
TICKERS = ["XLU", "URNM", "CIBR", "GSG", "IEFA", "PAVE", "SMH", "XBI", "XLV"]


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def state_for(source: str, source_shares: int) -> dict:
    positions = []
    for index, ticker in enumerate(TICKERS):
        shares = source_shares if ticker == source else 100 + index
        positions.append(
            {
                "ticker": ticker,
                "shares": shares,
                "current_weight_pct": 0.5 if ticker == "XLU" else 10.0,
            }
        )
    return {"cash_eur": 2500.0, "nav_eur": 100000.0, "positions": positions}


def ranking_for(top_source: str) -> list[dict]:
    ordered = [top_source] + [ticker for ticker in TICKERS if ticker != top_source]
    rows = []
    for index, ticker in enumerate(ordered):
        is_top = index == 0
        rows.append(
            {
                "ticker": ticker,
                "close_priority_score": 90.0 if is_top else 69.0 - index,
                "non_size_priority_score": 85.0 if is_top else 64.0 - index,
                "issue_family_count": 4 if is_top else 1,
                "independent_issue_families": ["release", "quality", "market", "discipline"] if is_top else ["market"],
                "release_score": 80.0 if is_top else 10.0,
                "suggested_action": "replace_partial" if is_top else "hold",
                "total_score": 3.0 if is_top else (4.97 if ticker == "CIBR" else 3.8),
                "current_weight_pct": 0.5 if ticker == "XLU" else 10.0,
                "action_executed_this_run": "None",
                "market": {
                    "rs_vs_spy_3m_pct": 12.0 if ticker == "CIBR" else -5.0,
                    "trend_quality": 5.0 if ticker == "CIBR" else 2.0,
                },
            }
        )
    return rows


def snapshot(status: str = "complete") -> dict:
    rows = {
        ticker: {
            "status": "complete",
            "observed_price_date": "2026-07-17",
            "close": 45.0 if ticker == "XLU" else 50.0 if ticker == "URNM" else 100.0,
            "rs_vs_spy_1m_pct": -2.0,
            "rs_vs_spy_3m_pct": 12.0 if ticker == "CIBR" else -5.0,
            "trend_quality": 5.0 if ticker == "CIBR" else 2.0,
        }
        for ticker in TICKERS
    }
    rows["EURUSD=X"] = {"status": "complete", "observed_price_date": "2026-07-17", "close": 1.1}
    rows["SPY"] = {"status": "complete", "observed_price_date": "2026-07-17", "close": 600.0}
    return {"freshness_status": status, "requested_close_date": "2026-07-17", "rows": rows}


def test_close_to_cash_fixture_restores_count() -> None:
    fixture = load_fixture("close_to_cash")
    result = decide(
        state_for(fixture["top_source"], fixture["source_shares"]),
        ranking_for(fixture["top_source"]),
        snapshot(),
    )
    assert result["conclusion"] == fixture["expected_conclusion"]
    assert result["selected_source"] == "XLU"
    assert result["selected_destination"] == ""
    assert result["transition"]["passed"] is True
    assert result["transition"]["projected_count"] == fixture["expected_projected_count"]
    assert result["transition"]["opened_tickers"] == []


def test_reallocate_existing_fixture_uses_only_existing_ticker() -> None:
    fixture = load_fixture("reallocate_existing")
    result = decide(
        state_for(fixture["top_source"], fixture["source_shares"]),
        ranking_for(fixture["top_source"]),
        snapshot(),
    )
    assert result["conclusion"] == fixture["expected_conclusion"]
    assert result["selected_source"] == "URNM"
    assert result["selected_destination"] == fixture["preferred_existing_destination"]
    assert result["destination_shares_added"] > 0
    assert result["transition"]["passed"] is True
    assert result["transition"]["projected_count"] == fixture["expected_projected_count"]
    assert result["transition"]["opened_tickers"] == []


def test_incomplete_freshness_fails_closed() -> None:
    fixture = load_fixture("insufficient_evidence")
    result = decide(state_for("XLU", 14), ranking_for("XLU"), snapshot(fixture["freshness_status"]))
    assert result["conclusion"] == fixture["expected_conclusion"]
    assert result["selected_source"] == ""
    assert result["transition"]["projected_count"] == fixture["expected_projected_count"]


def test_smallest_recent_high_quality_position_is_not_automatically_selected() -> None:
    continuity = {
        "PAVE": {
            "ticker": "PAVE",
            "shares": 10,
            "current_weight_pct": 0.2,
            "total_score": 4.8,
            "suggested_action": "hold",
            "fresh_cash_test": "Hold",
            "replaceable_status": "None",
            "weeks_replaceable": 0,
            "contribution_quality": "Flat",
            "pnl_pct": 0.0,
            "release_score": 10,
            "reason_codes": [],
            "action_executed_this_run": "Buy",
            "portfolio_role": "Rotation destination",
            "conviction_tier": "Tier 2",
        },
        "URNM": {
            "ticker": "URNM",
            "shares": 48,
            "current_weight_pct": 1.9,
            "total_score": 3.7,
            "suggested_action": "hold_with_override",
            "fresh_cash_test": "Hold",
            "replaceable_status": "None",
            "weeks_replaceable": 0,
            "contribution_quality": "Material drag",
            "pnl_pct": -27.0,
            "release_score": 90,
            "reason_codes": ["role_failed"],
            "action_executed_this_run": "None",
            "portfolio_role": "Strategic energy",
            "conviction_tier": "Tier 2",
        },
    }
    market = {
        "rows": {
            "PAVE": {"rs_vs_spy_1m_pct": 2.0, "rs_vs_spy_3m_pct": 5.0, "trend_quality": 5.0},
            "URNM": {"rs_vs_spy_1m_pct": -8.0, "rs_vs_spy_3m_pct": -12.0, "trend_quality": 1.0},
        }
    }
    ranked = rank_sources(continuity, market)
    assert ranked[0]["ticker"] == "URNM"
    assert ranked[0]["non_size_priority_score"] > ranked[1]["non_size_priority_score"]


def test_build_evidence_preserves_inputs_and_surfaces_are_clean() -> None:
    state = state_for("XLU", 14)
    state["positions"][0].update(
        {
            "suggested_action": "replace_partial",
            "fresh_cash_test": "No / under review",
            "replaceable_status": "Hold under review",
            "weeks_replaceable": 2,
            "total_score": 3.0,
            "rotation_release_score": 80,
            "rotation_reason_codes": ["role_impaired"],
        }
    )
    originals = deepcopy((state, {}, {}, snapshot()))
    evidence, en, nl = build_evidence(state, {}, {}, originals[3])
    assert (state, {}, {}, originals[3]) == originals
    assert evidence["authority_boundary"]["portfolio_state_mutation"] is False
    assert "Official portfolio state was not changed" in en
    assert "De officiële portefeuille is niet gewijzigd" in nl
    for blocked in ("shadow", "workflow", "guarded", "release score"):
        assert blocked not in en.lower()
        assert blocked not in nl.lower()


def test_render_rejects_internal_terms_by_contract() -> None:
    evidence = {
        "decision": {
            "conclusion": "no_trade_insufficient_evidence",
            "selected_source": "",
            "selected_destination": "",
            "transition": {"projected_count": 9},
            "projected_cash_eur": 2500.0,
        },
        "market_snapshot": {"requested_close_date": "2026-07-17"},
        "current_state": {"active_count": 9, "maximum": 8},
        "ranking": [
            {
                "ticker": "XLU",
                "close_priority_score": 1.0,
                "total_score": 3.0,
                "market": {"rs_vs_spy_3m_pct": -1.0},
                "current_weight_pct": 0.5,
            }
        ],
    }
    en, nl = render(evidence)
    assert "separate authorization" in en
    assert "afzonderlijke toestemming" in nl

def test_current_lane_score_sets_decision_quality_floor() -> None:
    from runtime.build_portfolio_close_first_review import continuity_rows

    state = {
        "positions": [
            {
                "ticker": "URNM",
                "shares": 48,
                "current_weight_pct": 1.9,
                "total_score": 3.7,
            }
        ]
    }
    lanes = {
        "URNM": {
            "total_score": 2.96,
            "evidence_summary": "Nuclear fuel security remains structural.",
            "why_now": "Timing is less urgent.",
            "macro_freshness_note": "Strategic but weakly confirmed.",
        }
    }
    row = continuity_rows(state, {}, lanes)["URNM"]
    assert row["holding_score"] == 3.7
    assert row["lane_score"] == 2.96
    assert row["total_score"] == 2.96
    assert row["lane_why_now"] == "Timing is less urgent."

