from __future__ import annotations

import json
from pathlib import Path

from runtime import add_etf_position_performance_section as perf
from runtime.portfolio_attribution_basis import ledger_entry_bases


def _write_runtime_state(path: Path, ticker: str, selected_close: float, fx_rate: float = 1.2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fx_basis": {"rate": fx_rate},
        "positions": [
            {
                "ticker": ticker,
                "selected_close": selected_close,
                "currency": "USD",
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_trade_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "trade_id,trade_date,source_report,ticker,action,shares_delta,previous_weight_pct,new_weight_pct,weight_change_pct,target_weight_pct,conviction_tier,portfolio_role,funding_source_note"
    lines = [header]
    for row in rows:
        values = [
            row.get("trade_id", "trade-1"),
            row.get("trade_date", "2026-06-01"),
            row["source_report"],
            row["ticker"],
            row.get("action", "Buy"),
            row["shares_delta"],
            "0",
            "0",
            "0",
            "0",
            "",
            "Rotation destination",
            "test",
        ]
        lines.append(",".join(values))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_ledger_backfill_reconstructs_missing_cibr_attribution(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _write_runtime_state(Path("output/runtime/state_1.json"), "CIBR", selected_close=80.0, fx_rate=1.2)
    _write_runtime_state(Path("output/runtime/state_2.json"), "CIBR", selected_close=90.0, fx_rate=1.25)
    _write_trade_ledger(
        Path("output/etf_trade_ledger.csv"),
        [
            {"trade_id": "buy-1", "source_report": "runtime:output/runtime/state_1.json", "ticker": "CIBR", "shares_delta": "10"},
            {"trade_id": "buy-2", "source_report": "runtime:output/runtime/state_2.json", "ticker": "CIBR", "shares_delta": "5"},
        ],
    )
    state = {
        "portfolio": {"starting_capital_eur": 100000.0, "total_portfolio_value_eur": 1363.64},
        "fx_basis": {"rate": 1.1},
        "positions": [
            {
                "ticker": "CIBR",
                "shares": 15.0,
                "current_price_local": 100.0,
                "previous_market_value_eur": 1363.64,
                "currency": "USD",
                "portfolio_role": "Rotation destination",
            }
        ],
    }

    bases = ledger_entry_bases(state)
    assert bases["CIBR"]["shares"] == 15.0
    rows = perf._performance_rows(state)
    row = rows[0]
    assert row["ticker"] == "CIBR"
    assert row["pl_eur"] == 336.97
    assert row["since_entry_pct"] == 32.82
    assert row["contribution_pct"] == 0.34


def test_ledger_backfill_resolves_bare_runtime_artifact_names(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _write_runtime_state(Path("output/runtime/etf_report_state_test.json"), "DFEN", selected_close=70.0, fx_rate=1.4)
    _write_trade_ledger(
        Path("output/etf_trade_ledger.csv"),
        [{"trade_id": "buy-1", "source_report": "runtime:etf_report_state_test.json", "ticker": "DFEN", "shares_delta": "10"}],
    )
    state = {
        "portfolio": {"starting_capital_eur": 100000.0, "total_portfolio_value_eur": 625.0},
        "fx_basis": {"rate": 1.2},
        "positions": [
            {
                "ticker": "DFEN",
                "shares": 10.0,
                "current_price_local": 75.0,
                "previous_market_value_eur": 625.0,
                "currency": "USD",
                "portfolio_role": "Rotation destination",
            }
        ],
    }

    row = perf._performance_rows(state)[0]
    assert row["ticker"] == "DFEN"
    assert row["pl_eur"] == 125.0
    assert row["since_entry_pct"] == 25.0
    assert row["contribution_pct"] == 0.12


def test_ledger_backfill_refuses_partial_unreconciled_basis(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _write_runtime_state(Path("output/runtime/state_1.json"), "IEFA", selected_close=80.0, fx_rate=1.2)
    _write_trade_ledger(
        Path("output/etf_trade_ledger.csv"),
        [{"trade_id": "buy-1", "source_report": "runtime:output/runtime/state_1.json", "ticker": "IEFA", "shares_delta": "10"}],
    )
    state = {
        "portfolio": {"starting_capital_eur": 100000.0, "total_portfolio_value_eur": 1818.18},
        "fx_basis": {"rate": 1.1},
        "positions": [
            {
                "ticker": "IEFA",
                "shares": 20.0,
                "current_price_local": 100.0,
                "previous_market_value_eur": 1818.18,
                "currency": "USD",
                "portfolio_role": "Rotation destination",
            }
        ],
    }

    assert ledger_entry_bases(state) == {}
    row = perf._performance_rows(state)[0]
    assert row["pl_eur"] is None
    assert row["since_entry_pct"] is None
    assert row["contribution_pct"] is None
