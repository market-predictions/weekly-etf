from __future__ import annotations

import pytest

from runtime.render_cockpit_front_page import _action_surface
from runtime.trade_lineage import normalize_and_validate_trade_lineage


def test_fresh_valuation_resets_historical_per_run_trade_fields() -> None:
    rows = normalize_and_validate_trade_lineage(
        [
            {
                "ticker": "PAVE",
                "shares": 107.0,
                "shares_delta_this_run": 107.0,
                "action_executed_this_run": "Buy",
                "weight_change_pct": 4.9708,
                "current_weight_pct": 4.90,
                "previous_weight_pct": 4.94,
                "report_date": "2026-07-17",
                "price_date": "2026-07-22",
                "market_value_local": 6056.20,
                "market_value_eur": 5306.39,
            }
        ],
        context="fresh_valuation",
    )

    row = rows[0]
    assert row["shares_delta_this_run"] == pytest.approx(0.0)
    assert row["weight_change_pct"] == pytest.approx(0.0)
    assert row["action_executed_this_run"] == "None"
    assert row["previous_shares"] == pytest.approx(107.0)
    assert row["previous_weight_pct"] == pytest.approx(4.90)
    assert row["pre_trade_weight_pct"] == pytest.approx(4.90)
    assert row["trade_lineage_source"] == "current_snapshot_no_trade"

    title, note = _action_surface({"positions": rows}, "en")
    assert title == "No portfolio action"
    assert "No positions opened" in note
