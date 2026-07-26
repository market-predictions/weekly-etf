from __future__ import annotations

import csv
from pathlib import Path

from runtime.portfolio_rotation_engine import (
    _normalize_blocked_zero_trade_overrides,
    _validate_constrained_plan,
)
from runtime.render_etf_report_nl_from_state import nl_history_comment

ROOT = Path(__file__).resolve().parents[1]


def test_constrained_zero_trade_plan_cannot_claim_rotation_budget_used() -> None:
    plan = {
        "trade_intents": [],
        "rotation_decisions": [
            {
                "ticker": "PAVE",
                "action_code": "hold_with_override",
                "current_weight_pct": 5.06,
                "target_weight_pct": 5.06,
                "delta_weight_pct": 0.0,
                "destination_ticker": "",
                "override_status": "engine",
                "override_reason_code": "churn_budget_used",
                "reason_codes": [],
            }
        ],
        "portfolio_constraint_validation": {
            "block_reason": "position_count_close_first",
            "final_position_count_assessment": {"passed": True},
            "blocked_candidates": [],
        },
        "validation_flags": {
            "instrument_eligibility_enforced": True,
            "leveraged_etf_constraint_enforced": True,
            "position_count_transition_enforced": True,
            "portfolio_constraint_validation_passed": True,
        },
    }
    normalized = _normalize_blocked_zero_trade_overrides(plan)
    decision = normalized["rotation_decisions"][0]
    assert decision["override_reason_code"] == "portfolio_constraint_blocked"
    assert "position_count_close_first" in decision["reason_codes"]
    assert normalized["validation_flags"]["zero_trade_stale_churn_status_removed"] is True
    _validate_constrained_plan(normalized)


def test_canonical_july14_history_comment_uses_supported_localization_basis() -> None:
    path = ROOT / "output/etf_valuation_history.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = {row["date"]: row for row in csv.DictReader(handle)}
    raw = rows["2026-07-14"]["comment"]
    assert raw == "Runtime valuation repriced from official portfolio-state shares"
    assert nl_history_comment(raw) != "Portfolio valuation based on confirmed prices and official holdings"
