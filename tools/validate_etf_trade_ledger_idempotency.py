from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

MODEL_TRADE_RE = re.compile(r"^model-(\d{4}-\d{2}-\d{2})-(.+)-(\d{2})-([A-Z0-9.]+)-(SELL|BUY)$")


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"Trade ledger not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _model_pairs(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], list[str]]:
    grouped: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    source_reports: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        trade_id = str(row.get("trade_id") or "").strip()
        match = MODEL_TRADE_RE.match(trade_id)
        if not match:
            continue
        date_from_id, run_id, pair_index, ticker, side = match.groups()
        trade_date = str(row.get("trade_date") or date_from_id).strip() or date_from_id
        group_key = (trade_date, run_id, pair_index)
        grouped[group_key][side] = ticker.upper()
        source_reports[group_key].add(str(row.get("source_report") or "").strip())
    pairs: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for group_key, legs in grouped.items():
        source = legs.get("SELL")
        destination = legs.get("BUY")
        if not source or not destination:
            continue
        trade_date = group_key[0]
        pair_key = (trade_date, source, destination)
        pairs[pair_key].extend(sorted(source_reports[group_key]))
    return pairs


def validate(path: Path) -> None:
    rows = _read_rows(path)
    pairs = _model_pairs(rows)
    errors: list[str] = []
    for (trade_date, source, destination), sources in sorted(pairs.items()):
        if len(sources) > 1:
            errors.append(
                f"duplicate_guarded_model_execution:{trade_date}:{source}->{destination}:count={len(sources)}:sources={','.join(sources)}"
            )
    if errors:
        raise RuntimeError("ETF trade-ledger idempotency validation failed: " + "; ".join(errors))
    print(f"ETF_TRADE_LEDGER_IDEMPOTENCY_OK | ledger={path} | model_pairs={len(pairs)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate that guarded model rotations are idempotent per trade date and source->destination pair.")
    parser.add_argument("--trade-ledger", default="output/etf_trade_ledger.csv")
    args = parser.parse_args()
    validate(Path(args.trade_ledger))


if __name__ == "__main__":
    main()
