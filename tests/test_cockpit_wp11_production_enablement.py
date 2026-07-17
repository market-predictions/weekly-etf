from __future__ import annotations

from tools.validate_cockpit_wp11_production_enablement import (
    build_exact_current_overlay,
    production_feature_value,
)


def test_exact_current_overlay_uses_official_whole_share_authority() -> None:
    base = {
        "run_id": "run-1",
        "report_date": "2026-07-16",
        "positions": [{"ticker": "STALE", "shares": 1.5}],
        "portfolio": {"cash_eur": 1.0, "total_portfolio_value_eur": 2.0},
        "trade_intents": [{"source_ticker": "STALE", "destination_ticker": "NEW"}],
        "rotation_plan": {"trade_intents": [{"source_ticker": "STALE"}]},
    }
    official = {
        "base_currency": "EUR",
        "cash_eur": 100.0,
        "invested_market_value_eur": 900.0,
        "nav_eur": 1000.0,
        "positions": [
            {
                "ticker": "AAA",
                "shares": 9,
                "market_value_eur": 900.0,
                "previous_market_value_eur": 900.0,
            }
        ],
        "whole_share_contract": {"status": "compliant"},
    }

    overlay = build_exact_current_overlay(base, official)

    assert overlay["positions"] == official["positions"]
    assert overlay["portfolio"] == {
        "cash_eur": 100.0,
        "total_portfolio_value_eur": 1000.0,
        "base_currency": "EUR",
    }
    assert overlay["trade_intents"] == []
    assert overlay["rotation_plan"] == {}
    assert overlay["validation_flags"]["wp11_exact_current_overlay"] is True
    assert overlay["execution_context"]["state_mutation"] is False


def test_exact_current_overlay_rejects_fractional_official_state() -> None:
    base = {"report_date": "2026-07-16"}
    official = {
        "cash_eur": 50.0,
        "nav_eur": 150.0,
        "positions": [
            {
                "ticker": "AAA",
                "shares": 1.5,
                "market_value_eur": 100.0,
            }
        ],
    }

    try:
        build_exact_current_overlay(base, official)
    except RuntimeError as exc:
        assert "fractional_shares:AAA:1.5" in str(exc)
    else:
        raise AssertionError("fractional official state should be rejected")


def test_production_feature_value_requires_send_report_job_env() -> None:
    workflow = """name: Send weekly ETF Pro report
jobs:
  send-report:
    runs-on: ubuntu-latest
    env:
      MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
    steps:
      - run: echo ok
"""
    assert production_feature_value(workflow) == "enabled"
    assert production_feature_value(workflow.replace("enabled", "disabled")) == "disabled"
    assert production_feature_value(workflow.replace("    env:\n      MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled\n", "")) is None
