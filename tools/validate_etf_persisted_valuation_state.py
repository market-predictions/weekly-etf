from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from runtime import model_execution_engine as execution_engine
from runtime.model_execution_guarded_auto import (
    _portfolio_execution_authorized,
    _whole_share_engine_patch,
)
from runtime.position_count_contract import (
    PositionCountAssessment,
    assess_current_positions,
    assess_position_count_transition,
    resolve_max_active_positions,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _text(value: Any) -> str:
    return str(value or "").strip()


def _runtime_nav(runtime_state: dict[str, Any]) -> tuple[str, float, float, float]:
    report_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"))
    cash = round(_float((runtime_state.get("portfolio") or {}).get("cash_eur")), 2)
    invested = round(sum(_float(row.get("previous_market_value_eur")) for row in runtime_state.get("positions", []) or []), 2)
    nav = round(cash + invested, 2)
    return report_date, cash, invested, nav


def _history_row(path: Path, report_date: str) -> dict[str, str]:
    if not path.exists():
        raise RuntimeError(f"Valuation history missing: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    matches = [row for row in rows if _text(row.get("date")) == report_date]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one valuation-history row for {report_date}; found {len(matches)}")
    return matches[0]


def _position_count(runtime_state: dict[str, Any]) -> int:
    return len([
        row
        for row in runtime_state.get("positions", []) or []
        if _text(row.get("ticker"))
        and _text(row.get("ticker")).upper() != "CASH"
        and _float(row.get("shares")) > 0.0
    ])


def _trade_intents(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = runtime_state.get("trade_intents") or (runtime_state.get("rotation_plan") or {}).get("trade_intents") or []
    return [dict(row) for row in rows if isinstance(row, dict)]


def _position_count_preflight(
    runtime_state: dict[str, Any],
    portfolio_state: dict[str, Any],
    portfolio_state_path: Path,
    *,
    enforce_request_authority: bool = False,
) -> PositionCountAssessment:
    maximum = resolve_max_active_positions(runtime_state)
    current_positions = portfolio_state.get("positions", []) or []
    current = assess_current_positions(current_positions, max_active_positions=maximum)
    if not current.passed:
        raise RuntimeError(
            "ETF position-count contract rejected official state: "
            + "; ".join(current.errors)
        )

    if enforce_request_authority and not _portfolio_execution_authorized():
        return current

    intents = _trade_intents(runtime_state)
    if not intents:
        return current

    prepared = execution_engine._prepare_runtime_state(runtime_state, portfolio_state_path)
    execution_errors, _warnings = execution_engine._validate_inputs(prepared)
    if execution_errors:
        raise RuntimeError(
            "ETF position-count preflight could not safely project invalid execution inputs: "
            + "; ".join(execution_errors)
        )

    with _whole_share_engine_patch():
        projected_positions = execution_engine._build_shadow_positions(prepared)

    transition = assess_position_count_transition(
        current_positions,
        projected_positions,
        max_active_positions=maximum,
        trade_intents_present=True,
    )
    if not transition.passed:
        raise RuntimeError(
            "ETF position-count contract blocked guarded execution before mutation: "
            + "; ".join(transition.errors)
        )
    return transition


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate canonical ETF portfolio state and valuation history against runtime state.")
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_valuation_history.csv")
    parser.add_argument("--tolerance", type=float, default=0.05)
    args = parser.parse_args()

    runtime_state_path = Path(args.runtime_state)
    portfolio_state_path = Path(args.portfolio_state)
    valuation_history_path = Path(args.valuation_history)

    runtime_state = _read_json(runtime_state_path)
    portfolio_state = _read_json(portfolio_state_path)
    report_date, runtime_cash, runtime_invested, runtime_nav = _runtime_nav(runtime_state)
    if not report_date:
        raise RuntimeError("Runtime state does not contain requested_close_date/report_date.")

    state_date = _text((portfolio_state.get("last_valuation") or {}).get("date"))
    if state_date != report_date:
        raise RuntimeError(f"Portfolio state last_valuation.date={state_date}, expected {report_date}")

    checks = {
        "nav_eur": (portfolio_state.get("nav_eur"), runtime_nav),
        "cash_eur": (portfolio_state.get("cash_eur"), runtime_cash),
        "invested_market_value_eur": (portfolio_state.get("invested_market_value_eur"), runtime_invested),
        "last_valuation.nav_eur": ((portfolio_state.get("last_valuation") or {}).get("nav_eur"), runtime_nav),
        "last_valuation.cash_eur": ((portfolio_state.get("last_valuation") or {}).get("cash_eur"), runtime_cash),
        "last_valuation.invested_market_value_eur": ((portfolio_state.get("last_valuation") or {}).get("invested_market_value_eur"), runtime_invested),
    }
    for label, (actual, expected) in checks.items():
        if abs(_float(actual) - expected) > args.tolerance:
            raise RuntimeError(f"Portfolio state mismatch for {label}: actual={actual}, expected={expected:.2f}")

    runtime_positions = _position_count(runtime_state)
    state_positions = _position_count({"positions": portfolio_state.get("positions", [])})
    if state_positions != runtime_positions:
        raise RuntimeError(f"Portfolio state position count={state_positions}, expected runtime count={runtime_positions}")

    history = _history_row(valuation_history_path, report_date)
    for label, expected in {
        "nav_eur": runtime_nav,
        "cash_eur": runtime_cash,
        "invested_market_value_eur": runtime_invested,
    }.items():
        if abs(_float(history.get(label)) - expected) > args.tolerance:
            raise RuntimeError(f"Valuation history mismatch for {label}: actual={history.get(label)}, expected={expected:.2f}")

    position_count = _position_count_preflight(
        runtime_state,
        portfolio_state,
        portfolio_state_path,
        enforce_request_authority=True,
    )

    print(
        "ETF_PERSISTED_VALUATION_STATE_OK | "
        f"date={report_date} | nav={runtime_nav:.2f} | cash={runtime_cash:.2f} | "
        f"invested={runtime_invested:.2f} | positions={runtime_positions} | "
        f"position_count_status={position_count.status} | "
        f"projected_positions={position_count.projected_count}/{position_count.max_active_positions} | "
        f"portfolio_state={portfolio_state_path} | valuation_history={valuation_history_path}"
    )


if __name__ == "__main__":
    main()
