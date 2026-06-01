from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PORTFOLIO_STATE = Path("output/etf_portfolio_state.json")
DEFAULT_POINTER = Path("output/runtime/latest_etf_model_execution_path.txt")
SHARE_TOL = 0.0005
VALUE_TOL = 0.75
WEIGHT_TOL = 0.08


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw or fallback


def _ticker(value: Any) -> str:
    return _text(value).upper()


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row and row.get(key) not in (None, ""):
            return row.get(key)
    return None


def _positions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (payload.get("positions") or payload.get("shadow_positions") or []) if isinstance(row, dict)]


def _position_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): dict(row) for row in _positions(payload) if _ticker(row.get("ticker"))}


def _cash(payload: dict[str, Any]) -> float:
    p = payload.get("portfolio") or payload
    return _float(p.get("cash_eur"))


def _nav(payload: dict[str, Any]) -> float:
    p = payload.get("portfolio") or payload
    return _float(_first(p, "total_portfolio_value_eur", "nav_eur"))


def _fx(payload: dict[str, Any]) -> float:
    return _float((payload.get("fx_basis") or {}).get("rate"), 1.0) or 1.0


def _price(row: dict[str, Any]) -> float:
    return _float(_first(row, "selected_close", "current_price_local", "continuity_current_price_local", "previous_price_local"))


def _local(row: dict[str, Any]) -> float:
    return _float(_first(row, "market_value_local", "previous_market_value_local"))


def _eur(row: dict[str, Any]) -> float:
    return _float(_first(row, "market_value_eur", "previous_market_value_eur"))


def _weight(row: dict[str, Any]) -> float:
    return _float(_first(row, "current_weight_pct", "previous_weight_pct", "weight_pct"))


def _is_zero_exited_position(row: dict[str, Any]) -> bool:
    """Return true for a sold-out artifact row omitted from active official state.

    Official portfolio state is an active-holdings file. After guarded execution,
    a fully sold position can be absent from `output/etf_portfolio_state.json`
    while still appearing in the execution artifact with zero shares/value as
    proof of the sell-down. That absence is valid only when shares, EUR/local
    value and weight are all effectively zero.
    """

    return (
        abs(_float(row.get("shares"))) <= SHARE_TOL
        and abs(_local(row)) <= VALUE_TOL
        and abs(_eur(row)) <= VALUE_TOL
        and abs(_weight(row)) <= WEIGHT_TOL
    )


def _row_math_errors(rows: list[dict[str, Any]], *, fx: float, nav: float, context: str) -> list[str]:
    errors: list[str] = []
    for row in rows:
        ticker = _ticker(row.get("ticker"))
        if not ticker or ticker == "CASH":
            continue
        shares = _float(row.get("shares"))
        price = _price(row)
        local = _local(row)
        eur = _eur(row)
        currency = _text(row.get("currency"), "USD").upper()
        if shares > SHARE_TOL and price <= 0:
            errors.append(f"{context}:missing_price:{ticker}")
        if shares >= 0 and price > 0 and local > 0:
            expected_local = round(shares * price, 2)
            if abs(expected_local - local) > VALUE_TOL:
                errors.append(f"{context}:local_value_mismatch:{ticker}:expected={expected_local:.2f}:actual={local:.2f}")
        if local > 0 and eur > 0:
            expected_eur = round(local if currency == "EUR" else local / fx, 2)
            if abs(expected_eur - eur) > VALUE_TOL:
                errors.append(f"{context}:eur_value_mismatch:{ticker}:expected={expected_eur:.2f}:actual={eur:.2f}")
        if eur > 0 and nav > 0:
            expected_weight = round(eur / nav * 100.0, 2)
            weight = _weight(row)
            if abs(expected_weight - weight) > WEIGHT_TOL:
                errors.append(f"{context}:weight_mismatch:{ticker}:expected={expected_weight:.2f}:actual={weight:.2f}")
    return errors


def validate_runtime_state_authority(runtime_state_path: Path, portfolio_state_path: Path = DEFAULT_PORTFOLIO_STATE, *, context: str = "runtime_state", raise_on_error: bool = True) -> list[str]:
    runtime_state = _read_json(runtime_state_path)
    portfolio_state = _read_json(portfolio_state_path)
    errors: list[str] = []
    runtime_positions = _position_map(runtime_state)
    official_positions = _position_map(portfolio_state)
    for ticker, official in official_positions.items():
        actual = runtime_positions.get(ticker)
        if not actual:
            errors.append(f"{context}:official_holding_missing_from_runtime:{ticker}")
            continue
        if abs(_float(actual.get("shares")) - _float(official.get("shares"))) > SHARE_TOL:
            errors.append(f"{context}:shares_authority_mismatch:{ticker}:expected={_float(official.get('shares')):.6f}:actual={_float(actual.get('shares')):.6f}")
        if abs(_eur(actual) - _eur(official)) > VALUE_TOL:
            errors.append(f"{context}:market_value_eur_authority_mismatch:{ticker}:expected={_eur(official):.2f}:actual={_eur(actual):.2f}")
    if abs(_cash(runtime_state) - _cash(portfolio_state)) > VALUE_TOL:
        errors.append(f"{context}:cash_authority_mismatch:expected={_cash(portfolio_state):.2f}:actual={_cash(runtime_state):.2f}")
    if _nav(portfolio_state) > 0 and abs(_nav(runtime_state) - _nav(portfolio_state)) > VALUE_TOL:
        errors.append(f"{context}:nav_authority_mismatch:expected={_nav(portfolio_state):.2f}:actual={_nav(runtime_state):.2f}")
    errors.extend(_row_math_errors(list(runtime_positions.values()), fx=_fx(runtime_state), nav=_nav(runtime_state), context=context))
    if errors and raise_on_error:
        raise RuntimeError("ETF execution-state authority validation failed: " + "; ".join(sorted(set(errors))))
    return errors


def _resolve_artifact(path_arg: str | None) -> Path:
    if path_arg:
        path = Path(path_arg)
        if path.exists():
            return path
        raise RuntimeError(f"Explicit ETF model-execution artifact does not exist: {path}")
    env = os.environ.get("ETF_MODEL_EXECUTION_PATH") or os.environ.get("MRKT_RPRTS_MODEL_EXECUTION_PATH")
    if env and Path(env).exists():
        return Path(env)
    if DEFAULT_POINTER.exists():
        raw = DEFAULT_POINTER.read_text(encoding="utf-8").strip()
        if raw and Path(raw).exists():
            return Path(raw)
    raise RuntimeError("No ETF model-execution artifact found.")


def validate_execution_artifact(artifact_path: Path, *, expected_mode: str | None = None, portfolio_state_path: Path | None = None, raise_on_error: bool = True) -> list[str]:
    artifact = _read_json(artifact_path)
    mode = _text(artifact.get("execution_mode"))
    status = _text(artifact.get("execution_status"))
    errors: list[str] = []
    if expected_mode and mode != expected_mode:
        errors.append(f"artifact:execution_mode_mismatch:{mode}!={expected_mode}")
    portfolio_state_path = portfolio_state_path or Path((artifact.get("source_files") or {}).get("portfolio_state") or DEFAULT_PORTFOLIO_STATE)
    portfolio_state = _read_json(portfolio_state_path)
    official = _position_map(portfolio_state)
    shadow = _position_map({"positions": artifact.get("shadow_positions") or []})
    runtime_path = (artifact.get("source_files") or {}).get("runtime_state")
    runtime_state = _read_json(Path(runtime_path)) if runtime_path and Path(runtime_path).exists() else {}
    post = artifact.get("post_trade_shadow_portfolio") or {}
    nav = _float(_first(post, "nav_eur") or _nav(portfolio_state))
    errors.extend(_row_math_errors(list(shadow.values()), fx=_fx(runtime_state), nav=nav, context=f"artifact_{mode or 'unknown'}"))
    if mode == "shadow":
        for ticker, row in shadow.items():
            if ticker not in official:
                continue
            delta = _float(row.get("shares_delta_this_run"))
            if abs(delta) <= SHARE_TOL:
                continue
            expected_after = _float(official[ticker].get("shares")) + delta
            if abs(_float(row.get("shares")) - expected_after) > SHARE_TOL:
                errors.append(f"artifact_shadow:shares_delta_does_not_bridge_official_state:{ticker}:expected_after={expected_after:.6f}:actual_after={_float(row.get('shares')):.6f}")
    if mode == "guarded_auto":
        for ticker, row in shadow.items():
            if ticker not in official:
                if _is_zero_exited_position(row):
                    continue
                errors.append(f"artifact_guarded_auto:position_missing_from_official_state:{ticker}")
                continue
            if abs(_float(row.get("shares")) - _float(official[ticker].get("shares"))) > SHARE_TOL:
                errors.append(f"artifact_guarded_auto:shares_authority_mismatch:{ticker}:expected={_float(official[ticker].get('shares')):.6f}:actual={_float(row.get('shares')):.6f}")
        result = artifact.get("guarded_auto_result") or {}
        if status == "executed":
            if result.get("portfolio_state_written") is not True:
                errors.append("artifact_guarded_auto:portfolio_state_not_written")
            if result.get("trade_ledger_written") is not True:
                errors.append("artifact_guarded_auto:trade_ledger_not_written")
        elif status == "already_executed":
            if result.get("idempotency_status") != "already_executed":
                errors.append("artifact_guarded_auto:missing_already_executed_status")
            if result.get("portfolio_state_written") is True or result.get("trade_ledger_written") is True:
                errors.append("artifact_guarded_auto:already_executed_must_not_write")
        else:
            errors.append(f"artifact_guarded_auto:unexpected_status:{status}")
    if errors and raise_on_error:
        raise RuntimeError("ETF execution artifact authority validation failed: " + "; ".join(sorted(set(errors))))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF execution-state authority and row-level valuation arithmetic.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--runtime-state")
    group.add_argument("--artifact")
    parser.add_argument("--portfolio-state", default=str(DEFAULT_PORTFOLIO_STATE))
    parser.add_argument("--expected-mode", choices=["shadow", "guarded_auto"], default=None)
    parser.add_argument("--context", default="manual")
    args = parser.parse_args()
    if args.runtime_state:
        errors = validate_runtime_state_authority(Path(args.runtime_state), Path(args.portfolio_state), context=args.context, raise_on_error=False)
        target = args.runtime_state
    else:
        artifact_path = _resolve_artifact(args.artifact)
        errors = validate_execution_artifact(artifact_path, expected_mode=args.expected_mode, portfolio_state_path=Path(args.portfolio_state), raise_on_error=False)
        target = str(artifact_path)
    if errors:
        raise RuntimeError("ETF execution-state authority validation failed for " + target + ": " + "; ".join(sorted(set(errors))))
    print(f"ETF_EXECUTION_STATE_AUTHORITY_OK | target={target} | context={args.context}")


if __name__ == "__main__":
    main()
