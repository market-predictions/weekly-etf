from __future__ import annotations

import json
from pathlib import Path

from runtime.etf_instrument_constraints import apply_rotation_policy_constraints
from runtime.render_etf_report_nl_from_state import nl_history_comment, valuation_history_points
from tools.validate_etf_rotation_output_contract import validate

ROOT = Path(__file__).resolve().parents[1]


def _constraints() -> dict:
    return {
        "schema_version": "1.1",
        "portfolio_policy": {"max_active_positions": 8, "leveraged_etfs_allowed": False},
        "instruments": {},
    }


def test_blocked_only_rotation_removes_stale_churn_budget_status() -> None:
    incumbents = [
        {"ticker": ticker, "current_weight_pct": 10.0}
        for ticker in ("A", "B", "C", "D", "E", "F", "G", "H", "I")
    ]
    plan = {
        "schema_version": "1.2",
        "created_at_utc": "2026-07-26T00:00:00Z",
        "run_id": "test",
        "report_token": "260724",
        "requested_close_date": "2026-07-24",
        "source_files": {},
        "policy": {},
        "incumbent_reviews": incumbents,
        "candidate_reviews": [],
        "rotation_decisions": [
            {
                "ticker": "A",
                "action_code": "replace_partial",
                "current_weight_pct": 10.0,
                "target_weight_pct": 8.0,
                "delta_weight_pct": -2.0,
                "destination_ticker": "J",
                "release_score": 90,
                "role_validity": "fail",
                "reason_codes": [],
                "override_status": "none",
                "override_reason_code": "",
            },
            {
                "ticker": "B",
                "action_code": "hold_with_override",
                "current_weight_pct": 10.0,
                "target_weight_pct": 10.0,
                "delta_weight_pct": 0.0,
                "destination_ticker": "",
                "release_score": 70,
                "role_validity": "impaired",
                "reason_codes": [],
                "override_status": "engine",
                "override_reason_code": "churn_budget_used",
            },
        ],
        "target_weights": [
            *[{"ticker": row["ticker"], "target_weight_pct": 8.0 if row["ticker"] == "A" else 10.0} for row in incumbents],
            {"ticker": "J", "target_weight_pct": 2.0},
        ],
        "trade_intents": [
            {
                "source_ticker": "A",
                "destination_ticker": "J",
                "delta_weight_pct": -2.0,
                "destination_delta_weight_pct": 2.0,
                "estimated_notional_eur": 2000.0,
                "action_code": "replace_partial",
                "reason_codes": [],
            }
        ],
        "validation_flags": {},
    }

    constrained = apply_rotation_policy_constraints(plan, _constraints())
    assert constrained["trade_intents"] == []
    reasons = {row["ticker"]: row["override_reason_code"] for row in constrained["rotation_decisions"]}
    assert reasons["A"] == "portfolio_constraint_blocked"
    assert reasons["B"] == "portfolio_constraint_blocked"
    validate(constrained, Path("synthetic_plan.json"))


def test_dutch_history_comment_localizes_confirmed_valuation_phrases() -> None:
    expected = "Waardering op basis van bevestigde slotkoersen en officiële posities"
    assert nl_history_comment("Portfolio valuation based on confirmed prices and official holdings") == expected
    assert nl_history_comment("Portfolio valuation based on confirmed closing prices and official holdings") == expected
    assert nl_history_comment("Runtime valuation repriced from official portfolio-state shares") == expected


def test_exact_july24_state_uses_fresh_dutch_current_history_comment() -> None:
    state_path = ROOT / "output/runtime/etf_report_state_20260724_20260726_170345.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    points = valuation_history_points(state)
    current = next(row for row in points if row["date"] == "2026-07-24")
    assert current["comment"] == "Waardering op basis van bevestigde slotkoersen en officiële posities"
