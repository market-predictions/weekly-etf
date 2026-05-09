from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_report_state import build_runtime_state
from runtime.replacement_duel_v2 import PRIORITY_DUEL_PAIRS, replacement_duel_v2_rows

ACTIONABLE_DECISION_MARKERS = (
    "replacement trigger watch",
    "challenger improving",
    "fundable",
    "actionable",
    "promoted",
)
NON_ACTIONABLE_DECISION_MARKERS = (
    "not fundable",
    "not decision-grade",
    "close proof incomplete",
    "pricing exception",
    "current holding still leads",
)


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _has_price(value: Any) -> bool:
    try:
        return value is not None and float(value) > 0
    except (TypeError, ValueError):
        return False


def _is_incomplete(row: dict[str, Any]) -> bool:
    return not _has_price(row.get("current_close")) or not _has_price(row.get("challenger_close"))


def _looks_actionable(row: dict[str, Any]) -> bool:
    decision = str(row.get("decision") or "").lower()
    if any(marker in decision for marker in NON_ACTIONABLE_DECISION_MARKERS):
        return False
    return any(marker in decision for marker in ACTIONABLE_DECISION_MARKERS)


def _current_holding_price_failures(state: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for position in state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if not ticker or ticker == "CASH":
            continue
        close = position.get("previous_price_local") or position.get("current_price_local")
        if not _has_price(close):
            failures.append(ticker)
    return failures


def _priced_rows_by_holding(rows: list[dict[str, Any]]) -> dict[str, int]:
    priced: dict[str, int] = {}
    for row in rows:
        holding = _ticker(row.get("current_holding"))
        if not holding:
            continue
        if _has_price(row.get("current_close")) and _has_price(row.get("challenger_close")):
            priced[holding] = priced.get(holding, 0) + 1
    return priced


def validate() -> None:
    state = build_runtime_state()
    rows = replacement_duel_v2_rows(state, limit=100)
    row_map = {(_ticker(row.get("current_holding")), _ticker(row.get("challenger"))): row for row in rows}

    hard_failures: list[str] = []
    warnings: list[str] = []

    missing_holding_prices = _current_holding_price_failures(state)
    if missing_holding_prices:
        hard_failures.append(
            "current holding closes missing: " + ", ".join(sorted(missing_holding_prices))
        )

    for row in rows:
        if _is_incomplete(row) and _looks_actionable(row):
            hard_failures.append(
                f"incomplete pricing but actionable decision: {_ticker(row.get('current_holding'))}->{_ticker(row.get('challenger'))} decision={row.get('decision')!r}"
            )

    priced_by_holding = _priced_rows_by_holding(rows)
    current_holdings = {
        _ticker(position.get("ticker"))
        for position in state.get("positions", []) or []
        if _ticker(position.get("ticker")) and _ticker(position.get("ticker")) != "CASH"
    }
    holdings_with_duel_policy = {holding for holding, _challenger in PRIORITY_DUEL_PAIRS}
    for holding in sorted(current_holdings & holdings_with_duel_policy):
        if priced_by_holding.get(holding, 0) == 0:
            warnings.append(
                f"{holding} has no fully priced challenger row; report remains valid but that duel is not decision-grade this week."
            )

    for pair in sorted(PRIORITY_DUEL_PAIRS):
        holding, challenger = pair
        row = row_map.get(pair)
        if row is None:
            warnings.append(f"canonical duel row missing: {holding}->{challenger}")
            continue
        if _is_incomplete(row):
            warnings.append(
                f"canonical duel pricing incomplete: {holding}->{challenger} current_close={row.get('current_close')} challenger_close={row.get('challenger_close')} basis={row.get('pricing_basis')}"
            )

    if hard_failures:
        raise RuntimeError(
            "Replacement Duel Pricing Contract failed: " + " | ".join(hard_failures)
        )

    for warning in warnings:
        print(f"::warning title=Replacement Duel Pricing::{warning}")

    print(
        "REPLACEMENT_DUEL_PRICING_CONTRACT_OK | "
        f"canonical_pairs={len(PRIORITY_DUEL_PAIRS)} | rows={len(rows)} | warnings={len(warnings)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    validate()


if __name__ == "__main__":
    main()
