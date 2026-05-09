#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_report_state import build_runtime_state

FIELDNAMES = [
    "report_date",
    "ticker",
    "weight_pct",
    "shares",
    "current_price_local",
    "currency",
    "market_value_eur",
    "pnl_pct",
    "total_score",
    "suggested_action",
    "conviction_tier",
    "portfolio_role",
    "fresh_cash_test",
    "would_initiate_today",
    "would_initiate_at_current_weight",
    "thesis_score",
    "implementation_score",
    "replaceable_status",
    "weeks_replaceable",
    "best_alternative",
    "alternative_score",
    "contribution_quality",
    "factor_overlap_flag",
    "hedge_validity_status",
    "cash_policy_flag",
    "required_next_action",
    "override_reason",
    "discipline_flags",
    "source_report",
]

ALT_BY_TICKER = {
    "SPY": "QUAL/IEFA",
    "SMH": "SOXX",
    "PPA": "ITA",
    "PAVE": "GRID",
    "URNM": "URA/NLR",
    "GLD": "GSG/DBC/BIL",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write ETF recommendation scorecard from runtime state")
    p.add_argument("--output-dir", default="output")
    p.add_argument("--mode", default="pro")
    p.add_argument("--check-only", action="store_true")
    return p.parse_args()


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _num(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt(value: Any, digits: int = 2) -> str:
    number = _num(value)
    return "" if number is None else f"{number:.{digits}f}"


def _flag_text(position: dict[str, Any]) -> str:
    flags: list[str] = []
    action = str(position.get("suggested_action") or "").lower()
    better = str(position.get("better_alternative_exists") or "").lower()
    ticker = _ticker(position.get("ticker"))
    pnl = _num(position.get("pnl_pct"))
    if "review" in action or better == "yes":
        flags.append("replaceable")
    if pnl is not None and pnl < -10:
        flags.append("loss_gt_10pct")
    if ticker in {"SPY", "SMH"}:
        flags.append("factor_overlap")
    if ticker == "GLD":
        flags.append("hedge_review")
    return ";".join(flags)


def _replaceable_status(position: dict[str, Any]) -> str:
    action = str(position.get("suggested_action") or "").lower()
    better = str(position.get("better_alternative_exists") or "").lower()
    if "review" in action or better == "yes":
        return "Hold under review"
    return "None"


def _contribution_quality(position: dict[str, Any]) -> str:
    pnl = _num(position.get("pnl_pct"))
    if pnl is None:
        return "Unresolved"
    if pnl > 10:
        return "Strong positive contributor"
    if pnl > 3:
        return "Positive contributor"
    if pnl >= -3:
        return "Flat / opportunity-cost review"
    if pnl > -10:
        return "Negative contributor"
    return "Material drag"


def _factor_flag(ticker: str) -> str:
    if ticker in {"SPY", "SMH"}:
        return "U.S. tech / AI overlap"
    if ticker == "PAVE":
        return "U.S. capex / infrastructure beta"
    if ticker == "GLD":
        return "Hedge / real-rate sensitivity"
    if ticker == "PPA":
        return "Defense resilience concentration"
    return ""


def _hedge_status(ticker: str, position: dict[str, Any]) -> str:
    if ticker != "GLD":
        return "Not hedge sleeve"
    pnl = _num(position.get("pnl_pct"))
    if pnl is not None and pnl < -10:
        return "Hedge review: drawdown"
    return "Valid but monitor"


def _would_today(position: dict[str, Any]) -> tuple[str, str]:
    fresh = str(position.get("fresh_cash_test") or "").lower()
    if "yes" in fresh:
        return "Yes", "Smaller" if "limited" in fresh or "smaller" in fresh else "Yes"
    if "no" in fresh or "reduce" in fresh:
        return "No", "No"
    if "hold" in fresh or "review" in fresh or "smaller" in fresh:
        return "Smaller", "No"
    return "Unresolved", "No"


def build_rows(output_dir: Path) -> list[dict[str, str]]:
    state = build_runtime_state()
    report_date = str(state.get("report_date") or state.get("requested_close_date") or "")
    source = f"runtime:{(state.get('source_files') or {}).get('pricing_audit', '')}"
    rows: list[dict[str, str]] = []
    for position in state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if not ticker:
            continue
        would_today, would_weight = _would_today(position)
        flags = _flag_text(position)
        rows.append(
            {
                "report_date": report_date,
                "ticker": ticker,
                "weight_pct": _fmt(position.get("previous_weight_pct") or position.get("current_weight_pct")),
                "shares": _fmt(position.get("shares"), 6),
                "current_price_local": _fmt(position.get("previous_price_local") or position.get("current_price_local")),
                "currency": str(position.get("currency") or "USD"),
                "market_value_eur": _fmt(position.get("previous_market_value_eur") or position.get("market_value_eur")),
                "pnl_pct": _fmt(position.get("pnl_pct")),
                "total_score": _fmt(position.get("total_score")),
                "suggested_action": str(position.get("suggested_action") or ""),
                "conviction_tier": str(position.get("conviction_tier") or ""),
                "portfolio_role": str(position.get("portfolio_role") or ""),
                "fresh_cash_test": str(position.get("fresh_cash_test") or ""),
                "would_initiate_today": would_today,
                "would_initiate_at_current_weight": would_weight,
                "thesis_score": _fmt(position.get("thesis_score")),
                "implementation_score": _fmt(position.get("implementation_score")),
                "replaceable_status": _replaceable_status(position),
                "weeks_replaceable": "1" if _replaceable_status(position) != "None" else "0",
                "best_alternative": ALT_BY_TICKER.get(ticker, ""),
                "alternative_score": "",
                "contribution_quality": _contribution_quality(position),
                "factor_overlap_flag": _factor_flag(ticker),
                "hedge_validity_status": _hedge_status(ticker, position),
                "cash_policy_flag": "Review if cash >3% and actionable lanes exist",
                "required_next_action": str(position.get("required_next_action") or ""),
                "override_reason": "Required if final action remains Hold despite discipline flags" if flags else "",
                "discipline_flags": flags,
                "source_report": source,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    rows = build_rows(output_dir)
    if not rows:
        raise RuntimeError("Could not derive recommendation scorecard rows from runtime state")
    path = output_dir / "etf_recommendation_scorecard.csv"
    flagged = sum(1 for r in rows if r.get("discipline_flags"))
    if args.check_only:
        print(f"ETF_RECOMMENDATION_SCORECARD_DERIVATION_OK | source=runtime | rows={len(rows)} | flagged={flagged} | scorecard={path.name}")
        return
    write_csv(path, rows)
    print(f"ETF_RECOMMENDATION_SCORECARD_OK | source=runtime | rows={len(rows)} | flagged={flagged} | scorecard={path.name}")


if __name__ == "__main__":
    main()
