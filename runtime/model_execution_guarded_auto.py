from __future__ import annotations

import argparse
import csv
import json
import math
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import runtime.model_execution_engine as engine
from runtime.whole_share_contract import (
    WHOLE_SHARE_TOLERANCE,
    floor_whole_shares,
    validate_whole_share_positions,
    whole_shares_for_notional,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _trade_date(state: dict[str, Any]) -> str:
    return str(state.get("requested_close_date") or state.get("report_date") or "").strip()


def _trade_intents(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = state.get("trade_intents") or (state.get("rotation_plan") or {}).get("trade_intents") or []
    return [dict(row) for row in rows if isinstance(row, dict)]


def _ledger_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _existing_pairs(path: Path) -> set[tuple[str, str, str]]:
    rows = _ledger_rows(path)
    grouped: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        trade_date = str(row.get("trade_date") or "").strip()
        source_report = str(row.get("source_report") or "").strip()
        ticker = _ticker(row.get("ticker"))
        action = str(row.get("action") or "").strip().lower()
        if not trade_date or not source_report.startswith("runtime:") or not ticker:
            continue
        key = (trade_date, source_report)
        grouped.setdefault(key, {})
        if action in {"sell", "decrease", "reduce"}:
            grouped[key]["source"] = ticker
        elif action in {"buy", "increase", "add"}:
            grouped[key]["destination"] = ticker
    out: set[tuple[str, str, str]] = set()
    for (trade_date, _source_report), legs in grouped.items():
        source = legs.get("source")
        destination = legs.get("destination")
        if source and destination:
            out.add((trade_date, source, destination))
    return out


def _positions_from_portfolio_state(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    state = _read_json(path)
    return [dict(row) for row in state.get("positions", []) or [] if isinstance(row, dict)]


def _assert_official_state_is_whole_share(path: Path) -> None:
    positions = _positions_from_portfolio_state(path)
    errors = validate_whole_share_positions(positions, context="official_portfolio_state")
    if errors:
        raise RuntimeError(
            "Guarded ETF execution blocked: official portfolio state violates the whole-share contract. "
            "Run tools/reconcile_etf_whole_share_state.py first. Errors: " + "; ".join(errors)
        )


@contextmanager
def _whole_share_engine_patch():
    original_shares_for_notional = engine._shares_for_notional
    original_execution_notional = engine._execution_notional

    def _whole_share_count(notional_eur: float, price_local: float, currency: str, fx: float) -> float:
        return float(whole_shares_for_notional(notional_eur, price_local, currency, fx))

    def _whole_share_notional(
        intent: dict[str, Any], source_row: dict[str, Any], runtime_state: dict[str, Any]
    ) -> tuple[float, float, bool, str]:
        actual, requested, capped, cap_reason = original_execution_notional(intent, source_row, runtime_state)
        ticker = _ticker(source_row.get("ticker"))
        price_map = engine._pricing_map(runtime_state)
        price = engine._price_local(ticker, source_row, price_map)
        currency = engine._currency(ticker, source_row, price_map)
        fx = engine._fx(runtime_state)
        available_units = floor_whole_shares(source_row.get("shares"))
        requested_units = whole_shares_for_notional(actual, price, currency, fx)
        sell_units = min(available_units, requested_units)
        exact_eur = engine._eur_from_local(sell_units * price, currency, fx) if sell_units else 0.0
        rounded_notional = math.ceil(exact_eur * 100.0 - WHOLE_SHARE_TOLERANCE) / 100.0 if sell_units else 0.0
        whole_share_capped = requested - rounded_notional > 1.0
        if whole_share_capped and not cap_reason:
            cap_reason = "whole_share_rounding"
        return rounded_notional, requested, capped or whole_share_capped, cap_reason

    engine._shares_for_notional = _whole_share_count
    engine._execution_notional = _whole_share_notional
    try:
        yield
    finally:
        engine._shares_for_notional = original_shares_for_notional
        engine._execution_notional = original_execution_notional


def _reconcile_guarded_cash(
    artifact: dict[str, Any], *, pre_trade_nav: float, portfolio_state_path: Path
) -> dict[str, Any]:
    if artifact.get("execution_status") != "executed":
        return artifact

    state = _read_json(portfolio_state_path)
    positions = [dict(row) for row in state.get("positions", []) or [] if isinstance(row, dict)]
    errors = validate_whole_share_positions(positions, context="post_guarded_execution")
    if errors:
        raise RuntimeError("Guarded execution produced fractional official positions: " + "; ".join(errors))

    invested = round(sum(engine._market_value_eur(row) for row in positions), 2)
    cash = round(pre_trade_nav - invested, 2)
    if cash < -0.05:
        raise RuntimeError(
            f"Whole-share execution would require negative residual cash: pre_nav={pre_trade_nav:.2f}, invested={invested:.2f}, cash={cash:.2f}"
        )
    nav = round(invested + cash, 2)
    for row in positions:
        market_value = engine._market_value_eur(row)
        weight = round(market_value / nav * 100.0, 2) if nav else 0.0
        row["current_weight_pct"] = weight
        row["previous_weight_pct"] = weight
        row["weight_inherited_pct"] = weight
        if row.get("action_executed_this_run") in {"Buy", "Sell"}:
            row["target_weight_pct"] = weight

    state.update(
        {
            "cash_eur": cash,
            "invested_market_value_eur": invested,
            "nav_eur": nav,
            "peak_nav_eur": max(float(state.get("peak_nav_eur") or nav), nav),
            "positions": positions,
            "whole_share_contract": {
                "status": "compliant",
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
                "execution_mode": "guarded_auto",
                "residual_cash_eur": cash,
                "nav_drift_eur": round(nav - pre_trade_nav, 2),
            },
        }
    )
    _write_json(portfolio_state_path, state)

    artifact["shadow_positions"] = positions
    artifact["post_trade_shadow_portfolio"] = {
        "cash_eur": cash,
        "invested_market_value_eur": invested,
        "nav_eur": nav,
        "nav_drift_eur": round(nav - pre_trade_nav, 2),
    }
    result = artifact.setdefault("guarded_auto_result", {})
    result.update(
        {
            "post_trade_nav_eur": nav,
            "post_trade_invested_market_value_eur": invested,
            "post_trade_cash_eur": cash,
            "whole_share_contract_status": "compliant",
        }
    )
    _write_json(Path(artifact["artifact_path"]), artifact)
    return artifact


def _build_already_executed_artifact(
    runtime_state_path: Path,
    portfolio_state_path: Path,
    trade_ledger_path: Path,
    output_dir: Path,
    matched_pairs: list[tuple[str, str, str]],
) -> dict[str, Any]:
    _assert_official_state_is_whole_share(portfolio_state_path)
    state = _read_json(runtime_state_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_token = str(state.get("report_date") or state.get("requested_close_date") or "unknown").replace("-", "")
    run_id = str(state.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    out_path = output_dir / f"etf_model_execution_{report_token}_{run_id}_already_executed.json"
    positions = _positions_from_portfolio_state(portfolio_state_path)
    portfolio_state = _read_json(portfolio_state_path) if portfolio_state_path.exists() else {}
    artifact = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "guarded_auto",
        "execution_status": "already_executed",
        "run_id": state.get("run_id"),
        "report_date": state.get("report_date"),
        "requested_close_date": state.get("requested_close_date"),
        "source_files": {
            "runtime_state": str(runtime_state_path),
            "portfolio_state": str(portfolio_state_path),
            "trade_ledger": str(trade_ledger_path),
            "pricing_audit": (state.get("source_files") or {}).get("pricing_audit"),
            "rotation_plan": (state.get("source_files") or {}).get("rotation_plan"),
        },
        "policy_checks": {
            "passed": True,
            "errors": [],
            "warnings": ["guarded_rotation_already_executed_for_trade_date_and_pair"],
            "mode_note": "No portfolio-state or trade-ledger write was performed because the same guarded model rotation already exists for the trade date and source/destination pair.",
        },
        "pre_trade_portfolio": {
            "cash_eur": portfolio_state.get("cash_eur"),
            "total_portfolio_value_eur": portfolio_state.get("nav_eur"),
            "base_currency": "EUR",
        },
        "post_trade_shadow_portfolio": {
            "cash_eur": portfolio_state.get("cash_eur"),
            "invested_market_value_eur": portfolio_state.get("invested_market_value_eur"),
            "nav_eur": portfolio_state.get("nav_eur"),
            "nav_drift_eur": 0.0,
        },
        "proposed_ledger_rows": [],
        "shadow_positions": positions,
        "guarded_auto_result": {
            "official_ledger_rows": [],
            "portfolio_state_written": False,
            "trade_ledger_written": False,
            "idempotency_status": "already_executed",
            "matched_pairs": [f"{d}:{s}->{dst}" for d, s, dst in matched_pairs],
            "post_trade_nav_eur": portfolio_state.get("nav_eur"),
            "post_trade_invested_market_value_eur": portfolio_state.get("invested_market_value_eur"),
            "post_trade_cash_eur": portfolio_state.get("cash_eur"),
            "whole_share_contract_status": "compliant",
        },
        "artifact_path": str(out_path),
    }
    _write_json(out_path, artifact)
    (output_dir / "latest_etf_model_execution_path.txt").write_text(str(out_path) + "\n", encoding="utf-8")
    return artifact


def build_guarded_artifact(
    runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, output_dir: Path
) -> dict[str, Any]:
    _assert_official_state_is_whole_share(portfolio_state_path)
    state = _read_json(runtime_state_path)
    trade_date = _trade_date(state)
    existing = _existing_pairs(trade_ledger_path)
    requested: list[tuple[str, str, str]] = []
    for intent in _trade_intents(state):
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        if trade_date and source and destination:
            requested.append((trade_date, source, destination))
    matched = [pair for pair in requested if pair in existing]
    if matched:
        return _build_already_executed_artifact(
            runtime_state_path, portfolio_state_path, trade_ledger_path, output_dir, matched
        )

    prepared = engine._prepare_runtime_state(_read_json(runtime_state_path), portfolio_state_path)
    pre_trade_nav = engine._nav(prepared)
    with _whole_share_engine_patch():
        artifact = engine.build_execution_artifact(
            runtime_state_path, portfolio_state_path, trade_ledger_path, "guarded_auto", output_dir
        )
    artifact = _reconcile_guarded_cash(
        artifact, pre_trade_nav=pre_trade_nav, portfolio_state_path=portfolio_state_path
    )
    official_rows = (artifact.get("guarded_auto_result") or {}).get("official_ledger_rows") or []
    for row in official_rows:
        if str(row.get("action") or "") in {"Buy", "Sell"}:
            delta = float(row.get("shares_delta") or 0.0)
            if abs(delta - round(delta)) > WHOLE_SHARE_TOLERANCE:
                raise RuntimeError(f"Guarded execution emitted fractional trade delta for {row.get('ticker')}: {delta}")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Idempotent guarded ETF model execution wrapper.")
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_trade_ledger.csv")
    parser.add_argument("--output-dir", default="output/runtime")
    args = parser.parse_args()
    artifact = build_guarded_artifact(
        Path(args.runtime_state), Path(args.portfolio_state), Path(args.trade_ledger), Path(args.output_dir)
    )
    print(
        "ETF_MODEL_EXECUTION_OK | "
        f"artifact={artifact['artifact_path']} | "
        f"mode={artifact.get('execution_mode')} | "
        f"trades={len(artifact.get('proposed_ledger_rows', []))} | "
        f"status={artifact.get('execution_status')}"
    )


if __name__ == "__main__":
    main()
