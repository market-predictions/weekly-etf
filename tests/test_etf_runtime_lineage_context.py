from __future__ import annotations

import pytest

from runtime.build_etf_report_state import _enrich_positions
from runtime.render_cockpit_front_page import _action_surface


def test_runtime_state_resets_previous_execution_by_run_identity() -> None:
    positions = _enrich_positions(
        {
            "cash_eur": 1000.0,
            "last_model_execution": {"run_id": "20260717_154351"},
            "positions": [
                {
                    "ticker": "PAVE",
                    "shares": 107.0,
                    "shares_delta_this_run": 107.0,
                    "action_executed_this_run": "Buy",
                    "weight_change_pct": 4.9708,
                    "current_weight_pct": 4.94,
                    "previous_weight_pct": 0.0,
                    "report_date": "2026-07-17",
                    "market_value_local": 6024.10,
                    "market_value_eur": 5266.88,
                }
            ],
        },
        {
            "run_id": "20260722_223651",
            "requested_close_date": "2026-07-22",
            "fx_basis": {"rate": 1.14128},
            "price_results": [
                {
                    "symbol": "PAVE",
                    "selected_close": 56.60,
                    "currency": "USD",
                    "status": "fresh_exact_unverified",
                    "pricing_tier": "valuation_grade",
                    "selected_close_type": "raw_close",
                    "returned_close_date": "2026-07-22",
                    "source": "test",
                }
            ],
        },
        [{"ticker": "PAVE", "report_date": "2026-07-22", "total_score": "3.83"}],
        {"assessed_lanes": []},
        {"rotation_decisions": [], "target_weights": [], "trade_intents": []},
    )

    row = positions[0]
    assert row["shares_delta_this_run"] == pytest.approx(0.0)
    assert row["weight_change_pct"] == pytest.approx(0.0)
    assert row["action_executed_this_run"] == "None"
    assert row["previous_shares"] == pytest.approx(107.0)
    assert row["previous_weight_pct"] == pytest.approx(row["current_weight_pct"])
    assert row["trade_lineage_source"] == "current_snapshot_no_trade"

    title, _note = _action_surface({"positions": positions}, "en")
    assert title == "No portfolio action"
