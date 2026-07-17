from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from runtime.model_execution_guarded_auto import build_guarded_artifact
from runtime.whole_share_contract import (
    is_whole_share,
    reconcile_portfolio_state,
    validate_whole_share_positions,
    whole_shares_for_notional,
)


def _pricing(symbol: str, price: float, currency: str = "EUR") -> dict:
    return {
        "symbol": symbol,
        "selected_close": price,
        "currency": currency,
        "status": "fresh_exact_close",
        "pricing_tier": "valuation_grade",
        "selected_close_type": "raw_close",
        "returned_close_date": "2026-07-16",
        "source": "fixture",
    }


def test_reconcile_floors_fractional_positions_closes_policy_ticker_and_preserves_nav() -> None:
    runtime = {
        "run_id": "run-1",
        "report_date": "2026-07-16",
        "requested_close_date": "2026-07-16",
        "fx_basis": {"rate": 1.0},
        "pricing": [_pricing("AAA", 100.0), _pricing("DFEN", 50.0), _pricing("DUST", 25.0)],
        "portfolio": {"cash_eur": 100.0},
    }
    state = {
        "cash_eur": 100.0,
        "invested_market_value_eur": 12687.5,
        "nav_eur": 12787.5,
        "positions": [
            {"ticker": "AAA", "shares": 123.75, "currency": "EUR", "current_price_local": 100.0},
            {"ticker": "DFEN", "shares": 6.2, "currency": "EUR", "current_price_local": 50.0},
            {"ticker": "DUST", "shares": 0.1, "currency": "EUR", "current_price_local": 25.0},
        ],
    }

    reconciled, artifact, rows = reconcile_portfolio_state(
        state, runtime, close_tickers=["DFEN"], source_name="fixture.json"
    )

    assert artifact["status"] == "reconciled"
    assert artifact["nav_drift_eur"] == pytest.approx(0.0)
    assert reconciled["nav_eur"] == pytest.approx(12787.5)
    assert reconciled["cash_eur"] == pytest.approx(487.5)
    assert {row["ticker"] for row in reconciled["positions"]} == {"AAA"}
    assert reconciled["positions"][0]["shares"] == 123
    assert validate_whole_share_positions(reconciled["positions"]) == []
    assert {row["action"] for row in rows} == {"FractionalReconciliation", "PolicyClose"}


def test_reconcile_is_idempotent_after_state_is_compliant() -> None:
    runtime = {
        "run_id": "run-2",
        "report_date": "2026-07-16",
        "fx_basis": {"rate": 1.0},
        "pricing": [_pricing("AAA", 10.0)],
    }
    state = {
        "cash_eur": 50.0,
        "invested_market_value_eur": 1000.0,
        "nav_eur": 1050.0,
        "positions": [{"ticker": "AAA", "shares": 100, "currency": "EUR", "current_price_local": 10.0}],
    }
    reconciled, artifact, rows = reconcile_portfolio_state(state, runtime, source_name="fixture.json")
    assert artifact["status"] == "already_compliant"
    assert rows == []
    assert reconciled["cash_eur"] == 50.0
    assert reconciled["positions"][0]["shares"] == 100


def test_whole_share_notional_rounding_handles_fx_cent_round_trip() -> None:
    assert whole_shares_for_notional(454.55, 100.0, "USD", 1.1) == 5
    assert whole_shares_for_notional(499.99, 100.0, "EUR", 1.0) == 4
    assert is_whole_share(5.0)
    assert not is_whole_share(5.01)


def test_guarded_execution_writes_integer_trade_deltas_and_residual_cash(tmp_path: Path) -> None:
    runtime_state = {
        "run_id": "run-guarded",
        "report_date": "2026-07-16",
        "requested_close_date": "2026-07-16",
        "source_files": {"pricing_audit": "fixture", "rotation_plan": "fixture"},
        "fx_basis": {"rate": 1.0},
        "portfolio": {
            "cash_eur": 1000.0,
            "total_portfolio_value_eur": 11000.0,
            "base_currency": "EUR",
        },
        "pricing": [_pricing("SRC", 100.0), _pricing("DST", 60.0)],
        "positions": [
            {
                "ticker": "SRC",
                "shares": 100,
                "currency": "EUR",
                "current_price_local": 100.0,
                "previous_price_local": 100.0,
                "market_value_local": 10000.0,
                "previous_market_value_local": 10000.0,
                "market_value_eur": 10000.0,
                "previous_market_value_eur": 10000.0,
                "current_weight_pct": 90.91,
                "previous_weight_pct": 90.91,
                "weight_inherited_pct": 90.91,
                "target_weight_pct": 90.91,
                "conviction_tier": "Tier 2",
                "portfolio_role": "Source",
            }
        ],
        "rotation_plan": {
            "policy": {
                "min_trade_size_pct_nav": 2.0,
                "max_single_source_reduction_pct_nav": 5.0,
                "max_major_rotations_per_run": 1,
            },
            "trade_intents": [
                {
                    "source_ticker": "SRC",
                    "destination_ticker": "DST",
                    "delta_weight_pct": -5.0,
                    "destination_delta_weight_pct": 5.0,
                    "estimated_notional_eur": 550.0,
                    "action_code": "replace_partial",
                    "reason_codes": ["fixture"],
                }
            ],
        },
    }
    portfolio_state = {
        "schema_version": "2.0-runtime",
        "portfolio_mode": "client_long_only_thematic",
        "base_currency": "EUR",
        "cash_eur": 1000.0,
        "invested_market_value_eur": 10000.0,
        "nav_eur": 11000.0,
        "peak_nav_eur": 11000.0,
        "positions": runtime_state["positions"],
    }
    runtime_path = tmp_path / "runtime.json"
    portfolio_path = tmp_path / "portfolio.json"
    ledger_path = tmp_path / "ledger.csv"
    output_dir = tmp_path / "runtime"
    runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")
    portfolio_path.write_text(json.dumps(portfolio_state), encoding="utf-8")

    artifact = build_guarded_artifact(runtime_path, portfolio_path, ledger_path, output_dir)
    assert artifact["execution_status"] == "executed"
    persisted = json.loads(portfolio_path.read_text(encoding="utf-8"))
    by_ticker = {row["ticker"]: row for row in persisted["positions"]}
    assert by_ticker["SRC"]["shares"] == 95
    assert by_ticker["DST"]["shares"] == 8
    assert persisted["cash_eur"] == pytest.approx(1020.0)
    assert persisted["nav_eur"] == pytest.approx(11000.0)
    assert validate_whole_share_positions(persisted["positions"]) == []

    with ledger_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert {row["shares_delta"] for row in rows} == {"-5.000000", "8.000000"}
