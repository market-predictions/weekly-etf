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


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _has_price(value: Any) -> bool:
    try:
        return value is not None and float(value) > 0
    except (TypeError, ValueError):
        return False


def validate() -> None:
    state = build_runtime_state()
    rows = replacement_duel_v2_rows(state, limit=100)
    row_map = {(_ticker(row.get("current_holding")), _ticker(row.get("challenger"))): row for row in rows}

    missing_rows: list[str] = []
    incomplete_rows: list[str] = []

    for pair in sorted(PRIORITY_DUEL_PAIRS):
        holding, challenger = pair
        row = row_map.get(pair)
        if row is None:
            missing_rows.append(f"{holding}->{challenger}")
            continue
        if not _has_price(row.get("current_close")) or not _has_price(row.get("challenger_close")):
            incomplete_rows.append(
                f"{holding}->{challenger} current_close={row.get('current_close')} challenger_close={row.get('challenger_close')} basis={row.get('pricing_basis')}"
            )

    if missing_rows or incomplete_rows:
        details = []
        if missing_rows:
            details.append("missing priority rows: " + ", ".join(missing_rows))
        if incomplete_rows:
            details.append("incomplete priority pricing: " + " | ".join(incomplete_rows))
        raise RuntimeError("Replacement Duel Pricing Contract failed: " + " ; ".join(details))

    print(
        "REPLACEMENT_DUEL_PRICING_CONTRACT_OK | "
        f"priority_pairs={len(PRIORITY_DUEL_PAIRS)} | rows={len(rows)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    validate()


if __name__ == "__main__":
    main()
