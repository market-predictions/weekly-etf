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
    "trade_id",
    "trade_date",
    "source_report",
    "ticker",
    "action",
    "shares_delta",
    "previous_weight_pct",
    "new_weight_pct",
    "weight_change_pct",
    "target_weight_pct",
    "conviction_tier",
    "portfolio_role",
    "funding_source_note",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write ETF trade ledger from runtime state")
    p.add_argument("--output-dir", default="output")
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


def _should_record(row: dict[str, Any]) -> bool:
    shares_delta = _num(row.get("shares_delta_this_run"))
    action = str(row.get("action_executed_this_run") or "").strip().lower()
    if shares_delta is not None and abs(shares_delta) > 0:
        return True
    if action and action not in {"none", "no change", "hold", "maintain"}:
        return True
    return False


def _existing_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def build_trade_rows(output_dir: Path) -> list[dict[str, str]]:
    path = output_dir / "etf_trade_ledger.csv"
    rows = _existing_rows(path)
    existing_ids = {row.get("trade_id") for row in rows}
    state = build_runtime_state()
    report_date = str(state.get("report_date") or state.get("requested_close_date") or "")
    source = f"runtime:{(state.get('source_files') or {}).get('pricing_audit', '')}"

    for position in state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if not ticker or not _should_record(position):
            continue
        trade_id = f"runtime-{report_date}-{ticker}"
        if trade_id in existing_ids:
            continue
        shares_delta = _num(position.get("shares_delta_this_run"))
        previous_weight = _num(position.get("previous_weight_pct"))
        weight_change = _num(position.get("weight_change_pct"))
        target_weight = _num(position.get("target_weight_pct"))
        if previous_weight is not None and weight_change is not None:
            new_weight = previous_weight + weight_change
        else:
            new_weight = _num(position.get("current_weight_pct"))
        rows.append(
            {
                "trade_id": trade_id,
                "trade_date": report_date,
                "source_report": source,
                "ticker": ticker,
                "action": str(position.get("action_executed_this_run") or position.get("suggested_action") or "Unknown"),
                "shares_delta": "" if shares_delta is None else f"{shares_delta:.6f}",
                "previous_weight_pct": "" if previous_weight is None else f"{previous_weight:.4f}",
                "new_weight_pct": "" if new_weight is None else f"{new_weight:.4f}",
                "weight_change_pct": "" if weight_change is None else f"{weight_change:.4f}",
                "target_weight_pct": "" if target_weight is None else f"{target_weight:.4f}",
                "conviction_tier": str(position.get("conviction_tier") or ""),
                "portfolio_role": str(position.get("portfolio_role") or ""),
                "funding_source_note": str(position.get("funding_source_note") or ""),
            }
        )
    rows.sort(key=lambda r: (r.get("trade_date", ""), r.get("trade_id", "")))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    ledger_path = output_dir / "etf_trade_ledger.csv"
    rows = build_trade_rows(output_dir)
    if args.check_only:
        print(f"ETF_TRADE_LEDGER_DERIVATION_OK | source=runtime | ledger={ledger_path.name} | rows={len(rows)}")
        return
    write_csv(ledger_path, rows)
    print(f"ETF_TRADE_LEDGER_OK | source=runtime | ledger={ledger_path.name} | rows={len(rows)}")


if __name__ == "__main__":
    main()
