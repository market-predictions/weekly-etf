from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.whole_share_contract import WHOLE_SHARE_TOLERANCE, validate_whole_share_positions


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def validate_portfolio_state(path: Path) -> list[str]:
    payload = _read_json(path)
    errors = validate_whole_share_positions(payload.get("positions", []) or [], context="portfolio_state")
    invested = round(
        sum(
            _float(row.get("market_value_eur") or row.get("previous_market_value_eur"))
            for row in payload.get("positions", []) or []
        ),
        2,
    )
    cash = _float(payload.get("cash_eur"))
    nav = _float(payload.get("nav_eur"))
    if abs(invested - _float(payload.get("invested_market_value_eur"))) > 0.05:
        errors.append("portfolio_state:invested_value_mismatch")
    if abs((invested + cash) - nav) > 0.05:
        errors.append("portfolio_state:nav_reconciliation_mismatch")
    return errors


def validate_execution_artifact(path: Path) -> list[str]:
    payload = _read_json(path)
    errors: list[str] = []
    if payload.get("execution_mode") != "guarded_auto":
        return errors
    errors.extend(
        validate_whole_share_positions(
            payload.get("shadow_positions", []) or [], context="guarded_artifact"
        )
    )
    for row in (payload.get("guarded_auto_result") or {}).get("official_ledger_rows") or []:
        if str(row.get("action") or "") not in {"Buy", "Sell"}:
            continue
        delta = _float(row.get("shares_delta"))
        if abs(delta - round(delta)) > WHOLE_SHARE_TOLERANCE:
            errors.append(f"guarded_artifact:fractional_trade_delta:{row.get('ticker')}:{delta}")
    post = payload.get("post_trade_shadow_portfolio") or {}
    if abs(_float(post.get("nav_drift_eur"))) > 0.05:
        errors.append(f"guarded_artifact:nav_drift:{post.get('nav_drift_eur')}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Weekly ETF whole-share state contract.")
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--artifact", default=None)
    args = parser.parse_args()
    errors = validate_portfolio_state(Path(args.portfolio_state))
    if args.artifact:
        errors.extend(validate_execution_artifact(Path(args.artifact)))
    if errors:
        raise RuntimeError(
            "ETF whole-share contract validation failed: " + "; ".join(sorted(set(errors)))
        )
    print(
        "ETF_WHOLE_SHARE_CONTRACT_OK | "
        f"portfolio_state={args.portfolio_state} | artifact={args.artifact or 'not_requested'}"
    )


if __name__ == "__main__":
    main()
