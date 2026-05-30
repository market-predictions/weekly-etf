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

from runtime.finalize_executed_etf_report import finalize_from_artifact

POINTER = Path("output/runtime/latest_etf_model_execution_path.txt")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw or fallback


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _resolve(path_arg: str | None) -> Path:
    if path_arg:
        path = Path(path_arg)
        if path.exists():
            return path
        raise RuntimeError(f"Explicit model-execution artifact does not exist: {path}")
    env = os.environ.get("ETF_MODEL_EXECUTION_PATH") or os.environ.get("MRKT_RPRTS_MODEL_EXECUTION_PATH")
    if env:
        path = Path(env)
        if path.exists():
            return path
    if POINTER.exists():
        raw = POINTER.read_text(encoding="utf-8").strip()
        if raw:
            path = Path(raw)
            if path.exists():
                return path
            candidate = POINTER.parent / path.name
            if candidate.exists():
                return candidate
    raise RuntimeError("No ETF model-execution artifact found.")


def validate(path: Path, *, expected_mode: str, finalize_report: bool = True) -> None:
    payload = _read_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != "1.0":
        errors.append("schema_version_not_1.0")
    if payload.get("execution_mode") != expected_mode:
        errors.append(f"execution_mode_mismatch:{payload.get('execution_mode')}!={expected_mode}")
    policy = payload.get("policy_checks") or {}
    if policy.get("passed") is not True:
        errors.append("policy_checks_not_passed:" + ";".join(policy.get("errors") or []))
    rows = payload.get("proposed_ledger_rows") or []
    if not rows:
        errors.append("no_proposed_ledger_rows")
    shadow_positions = payload.get("shadow_positions") or []
    if not shadow_positions:
        errors.append("no_shadow_positions")
    post = payload.get("post_trade_shadow_portfolio") or {}
    if abs(_float(post.get("nav_drift_eur"))) > 1.0:
        errors.append(f"nav_drift_too_large:{post.get('nav_drift_eur')}")
    for row in rows:
        if not _text(row.get("source_ticker")) or not _text(row.get("destination_ticker")):
            errors.append("ledger_row_missing_source_or_destination")
        if _float(row.get("estimated_notional_eur")) <= 0:
            errors.append("ledger_row_non_positive_notional")
        if _float(row.get("source_delta_weight_pct")) >= 0:
            errors.append("ledger_row_source_delta_not_negative")
        if _float(row.get("destination_delta_weight_pct")) <= 0:
            errors.append("ledger_row_destination_delta_not_positive")
    if expected_mode == "guarded_auto":
        if payload.get("execution_status") != "executed":
            errors.append(f"guarded_auto_not_executed:{payload.get('execution_status')}")
        result = payload.get("guarded_auto_result") or {}
        if result.get("portfolio_state_written") is not True:
            errors.append("portfolio_state_not_written")
        if result.get("trade_ledger_written") is not True:
            errors.append("trade_ledger_not_written")
        official_rows = result.get("official_ledger_rows") or []
        if not official_rows:
            errors.append("no_official_ledger_rows")
        for row in official_rows:
            action = _text(row.get("action"))
            shares_delta = _float(row.get("shares_delta"))
            if action == "Sell" and shares_delta >= 0:
                errors.append("sell_row_delta_not_negative")
            if action == "Buy" and shares_delta <= 0:
                errors.append("buy_row_delta_not_positive")
    if errors:
        raise RuntimeError("ETF model execution validation failed for " + path.name + ": " + "; ".join(sorted(set(errors))))
    print(f"ETF_MODEL_EXECUTION_VALIDATION_OK | artifact={path.name} | mode={expected_mode} | trades={len(rows)} | positions={len(shadow_positions)}")
    if expected_mode == "guarded_auto" and finalize_report:
        finalize_from_artifact(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--expected-mode", default="shadow", choices=["shadow", "guarded_auto"])
    parser.add_argument("--no-finalize-report", action="store_true")
    args = parser.parse_args()
    validate(_resolve(args.artifact), expected_mode=args.expected_mode, finalize_report=not args.no_finalize_report)


if __name__ == "__main__":
    main()
