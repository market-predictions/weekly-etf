from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.model_execution_engine import LEDGER_FIELDS
from runtime.whole_share_contract import reconcile_portfolio_state, validate_whole_share_positions


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _read_ledger(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_ledger(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = [{field: row.get(field, "") for field in LEDGER_FIELDS} for row in rows]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(normalized)


def reconcile(
    *,
    runtime_state_path: Path,
    portfolio_state_path: Path,
    trade_ledger_path: Path,
    output_dir: Path,
    close_tickers: list[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    runtime_state = _read_json(runtime_state_path)
    portfolio_state = _read_json(portfolio_state_path)
    reconciled, artifact, reconciliation_rows = reconcile_portfolio_state(
        portfolio_state,
        runtime_state,
        close_tickers=close_tickers,
        source_name=str(runtime_state_path),
    )
    errors = validate_whole_share_positions(reconciled.get("positions", []), context="reconciled_portfolio_state")
    if errors:
        raise RuntimeError("Whole-share reconciliation failed: " + "; ".join(errors))
    if abs(float(artifact.get("nav_drift_eur") or 0.0)) > 0.05:
        raise RuntimeError(f"Whole-share reconciliation NAV drift exceeds tolerance: {artifact.get('nav_drift_eur')}")

    output_dir.mkdir(parents=True, exist_ok=True)
    report_token = str(artifact.get("report_date") or "unknown").replace("-", "")
    run_id = str(artifact.get("run_id") or "unknown")
    artifact_path = output_dir / f"etf_whole_share_reconciliation_{report_token}_{run_id}.json"
    artifact["artifact_path"] = str(artifact_path)
    artifact["portfolio_state_path"] = str(portfolio_state_path)
    artifact["trade_ledger_path"] = str(trade_ledger_path)
    artifact["dry_run"] = dry_run

    if not dry_run and artifact.get("status") == "reconciled":
        existing_rows = _read_ledger(trade_ledger_path)
        existing_ids = {row.get("trade_id") for row in existing_rows}
        rows_to_append = [row for row in reconciliation_rows if row.get("trade_id") not in existing_ids]
        _write_ledger(trade_ledger_path, existing_rows + rows_to_append)
        _write_json(portfolio_state_path, reconciled)
        artifact["ledger_rows_appended"] = len(rows_to_append)
        artifact["portfolio_state_written"] = True
        artifact["trade_ledger_written"] = True
    else:
        artifact["ledger_rows_appended"] = 0
        artifact["portfolio_state_written"] = False
        artifact["trade_ledger_written"] = False

    _write_json(artifact_path, artifact)
    (output_dir / "latest_etf_whole_share_reconciliation_path.txt").write_text(
        str(artifact_path) + "\n", encoding="utf-8"
    )
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile the official ETF portfolio to whole shares.")
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_trade_ledger.csv")
    parser.add_argument("--output-dir", default="output/runtime")
    parser.add_argument("--close-ticker", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    artifact = reconcile(
        runtime_state_path=Path(args.runtime_state),
        portfolio_state_path=Path(args.portfolio_state),
        trade_ledger_path=Path(args.trade_ledger),
        output_dir=Path(args.output_dir),
        close_tickers=args.close_ticker,
        dry_run=args.dry_run,
    )
    print(
        "ETF_WHOLE_SHARE_RECONCILIATION_OK | "
        f"status={artifact.get('status')} | adjusted={artifact.get('adjusted_position_count')} | "
        f"nav_drift={artifact.get('nav_drift_eur')} | artifact={artifact.get('artifact_path')}"
    )


if __name__ == "__main__":
    main()
