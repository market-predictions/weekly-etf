from __future__ import annotations

import json
from pathlib import Path

from runtime.model_execution_guarded_auto import (
    _portfolio_execution_authorized,
    build_guarded_artifact,
)


def _request(directory: Path, value: str | None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    lines = ["# Weekly ETF report request", "delivery_authorized: true"]
    if value is not None:
        lines.append(f"portfolio_execution_authorized: {value}")
    (directory / "weekly_etf_report_request_20260718_125324.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_request_authorization_is_explicit_and_fail_closed(tmp_path: Path) -> None:
    queue = tmp_path / "queue"
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, None)
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, "not-a-boolean")
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, "false")
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, "true")
    assert _portfolio_execution_authorized(queue) is True


def test_unauthorized_report_request_writes_no_portfolio_or_ledger(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    queue = tmp_path / "control/run_queue"
    _request(queue, "false")
    output = tmp_path / "output/runtime"
    output.mkdir(parents=True)
    portfolio = tmp_path / "output/etf_portfolio_state.json"
    portfolio.parent.mkdir(parents=True, exist_ok=True)
    portfolio.write_text(json.dumps({
        "cash_eur": 1000.0,
        "invested_market_value_eur": 1000.0,
        "nav_eur": 2000.0,
        "positions": [{
            "ticker": "AAA", "shares": 10, "currency": "EUR",
            "current_price_local": 100.0, "previous_price_local": 100.0,
            "market_value_local": 1000.0, "previous_market_value_local": 1000.0,
            "market_value_eur": 1000.0, "previous_market_value_eur": 1000.0,
            "current_weight_pct": 50.0, "previous_weight_pct": 50.0,
            "weight_inherited_pct": 50.0, "target_weight_pct": 50.0,
        }],
        "whole_share_contract": {"status": "compliant"},
    }), encoding="utf-8")
    ledger = tmp_path / "output/etf_trade_ledger.csv"
    ledger.write_text("trade_id,trade_date,source_report,ticker,action,shares_delta\n", encoding="utf-8")
    runtime = tmp_path / "output/runtime/state.json"
    runtime.write_text(json.dumps({
        "run_id": "20260718_125324",
        "report_date": "2026-07-17",
        "requested_close_date": "2026-07-17",
        "portfolio": {"cash_eur": 1000.0, "total_portfolio_value_eur": 2000.0, "base_currency": "EUR"},
        "fx_basis": {"rate": 1.0},
        "pricing": [{"symbol": "AAA", "selected_close": 100.0, "currency": "EUR", "status": "fresh_exact_close", "pricing_tier": "valuation_grade"}],
        "positions": [{"ticker": "AAA", "shares": 10}],
        "trade_intents": [{"source_ticker": "AAA", "destination_ticker": "BBB"}],
        "source_files": {"pricing_audit": "fixture.json", "rotation_plan": "plan.json"},
    }), encoding="utf-8")

    portfolio_before = portfolio.read_bytes()
    ledger_before = ledger.read_bytes()
    artifact = build_guarded_artifact(
        runtime, portfolio, ledger, output, enforce_request_authority=True
    )

    assert artifact["execution_mode"] == "guarded_auto"
    assert artifact["execution_status"] == "no_trade_intents"
    assert artifact["guarded_auto_result"]["authorization_status"] == "not_authorized"
    assert artifact["guarded_auto_result"]["portfolio_state_written"] is False
    assert artifact["guarded_auto_result"]["trade_ledger_written"] is False
    assert artifact["proposed_ledger_rows"] == []
    assert portfolio.read_bytes() == portfolio_before
    assert ledger.read_bytes() == ledger_before
