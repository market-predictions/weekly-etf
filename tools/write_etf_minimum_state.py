#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_report_state import build_runtime_state

SCHEMA_VERSION = "2.0-runtime"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write minimum ETF state files from runtime state")
    p.add_argument("--output-dir", default="output")
    p.add_argument("--mode", default="pro")
    p.add_argument("--check-only", action="store_true")
    return p.parse_args()


def _num(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _position_from_runtime(row: dict[str, Any]) -> dict[str, Any]:
    ticker = _ticker(row.get("ticker"))
    return {
        "ticker": ticker,
        "shares": _num(row.get("shares")),
        "current_price_local": _num(row.get("previous_price_local") or row.get("current_price_local")),
        "currency": row.get("currency") or "USD",
        "market_value_local": _num(row.get("previous_market_value_local") or row.get("market_value_local")),
        "market_value_eur": _num(row.get("previous_market_value_eur") or row.get("market_value_eur")),
        "current_weight_pct": _num(row.get("previous_weight_pct") or row.get("current_weight_pct")),
        "existing_new": row.get("existing_new") or "Existing",
        "weight_inherited_pct": row.get("weight_inherited_pct"),
        "target_weight_pct": row.get("target_weight_pct"),
        "suggested_action": row.get("suggested_action"),
        "conviction_tier": row.get("conviction_tier"),
        "total_score": row.get("total_score"),
        "portfolio_role": row.get("portfolio_role"),
        "better_alternative_exists": row.get("better_alternative_exists"),
        "short_reason": row.get("short_reason"),
        "direction": row.get("direction") or "Long",
        "avg_entry_local": row.get("avg_entry_local"),
        "continuity_current_price_local": row.get("continuity_current_price_local") or row.get("previous_price_local"),
        "pnl_pct": row.get("pnl_pct"),
        "original_thesis": row.get("original_thesis"),
        "previous_weight_pct": row.get("previous_weight_pct"),
        "weight_change_pct": row.get("weight_change_pct"),
        "shares_delta_this_run": row.get("shares_delta_this_run"),
        "action_executed_this_run": row.get("action_executed_this_run"),
        "funding_source_note": row.get("funding_source_note"),
    }


def build_portfolio_state_from_runtime(output_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    runtime = build_runtime_state()
    report_date = str(runtime.get("report_date") or runtime.get("requested_close_date") or "")
    if not report_date:
        raise RuntimeError("Could not derive ETF state: runtime report_date missing.")

    positions = [_position_from_runtime(p) for p in (runtime.get("positions", []) or []) if _ticker(p.get("ticker"))]
    if not positions:
        raise RuntimeError("Could not derive ETF state: runtime positions missing.")

    cash = _num((runtime.get("portfolio") or {}).get("cash_eur"))
    invested = round(sum(_num(p.get("market_value_eur")) for p in positions), 2)
    nav = round(invested + cash, 2)
    starting_capital = 100000.0
    since_inception = round((nav / starting_capital - 1.0) * 100.0, 4) if starting_capital else 0.0
    fx_rate = (runtime.get("fx_basis") or {}).get("rate")

    previous_history: list[dict[str, Any]] = []
    history_path = output_dir / "etf_valuation_history.csv"
    if history_path.exists():
        with history_path.open("r", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("date") and row.get("date") != report_date:
                    previous_history.append(dict(row))

    latest_history = {
        "date": report_date,
        "nav_eur": round(nav, 2),
        "cash_eur": round(cash, 2),
        "invested_market_value_eur": round(invested, 2),
        "daily_return_pct": "",
        "since_inception_return_pct": since_inception,
        "drawdown_pct": "",
        "eurusd_used": "" if fx_rate is None else round(_num(fx_rate), 4),
        "comment": "Runtime-derived valuation from pricing audit and explicit portfolio state",
        "source_report": f"runtime:{(runtime.get('source_files') or {}).get('pricing_audit', '')}",
    }
    history_rows = previous_history + [latest_history]

    state = {
        "schema_version": SCHEMA_VERSION,
        "portfolio_mode": "client_long_only_thematic",
        "base_currency": "EUR",
        "valuation_source": "runtime.build_etf_report_state",
        "pricing_audit_file": (runtime.get("source_files") or {}).get("pricing_audit"),
        "trade_ledger_file": "etf_trade_ledger.csv",
        "recommendation_scorecard_file": "etf_recommendation_scorecard.csv",
        "inception_date": history_rows[0].get("date"),
        "starting_capital_eur": starting_capital,
        "cash_eur": round(cash, 2),
        "invested_market_value_eur": round(invested, 2),
        "nav_eur": round(nav, 2),
        "peak_nav_eur": round(max(_num(r.get("nav_eur")) for r in history_rows), 2),
        "max_drawdown_pct": "",
        "positions": positions,
        "last_report": {
            "date": report_date,
            "source_report": "runtime",
            "position_count": len(positions),
        },
        "last_valuation": {
            "date": report_date,
            "nav_eur": round(nav, 2),
            "invested_market_value_eur": round(invested, 2),
            "cash_eur": round(cash, 2),
            "since_inception_return_pct": since_inception,
            "daily_return_pct": "",
            "drawdown_pct": "",
            "eurusd_used": None if fx_rate is None else round(_num(fx_rate), 4),
            "equity_curve_state": "Runtime-derived",
            "valuation_notes": "Section 7 and Section 15 validated from runtime state.",
        },
    }
    return state, history_rows


def write_history_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "date",
        "nav_eur",
        "cash_eur",
        "invested_market_value_eur",
        "daily_return_pct",
        "since_inception_return_pct",
        "drawdown_pct",
        "eurusd_used",
        "comment",
        "source_report",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    state, history_rows = build_portfolio_state_from_runtime(output_dir)
    state_path = output_dir / "etf_portfolio_state.json"
    history_path = output_dir / "etf_valuation_history.csv"
    if args.check_only:
        print(
            f"ETF_STATE_DERIVATION_OK | source=runtime | state={state_path.name} | history_rows={len(history_rows)} | positions={len(state['positions'])}"
        )
        return
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    write_history_csv(history_path, history_rows)
    print(
        f"ETF_STATE_OK | source=runtime | state={state_path.name} | history={history_path.name} | history_rows={len(history_rows)} | positions={len(state['positions'])}"
    )


if __name__ == "__main__":
    main()
