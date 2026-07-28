from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Portfolio target must be a JSON object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_shared_portfolio_target_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_shared_exposure_portfolio_target":
        blockers.append("unexpected artifact_type")
    if payload.get("source_repository") != "market-predictions/weekly-etf":
        blockers.append("unexpected source_repository")
    if not payload.get("report_date") or not payload.get("source_run_id"):
        blockers.append("missing report or run lineage")

    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    if authority.get("portfolio_reference_authority") is not True:
        blockers.append("portfolio reference authority missing")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if authority.get(key) is not False:
            blockers.append(f"{key} must be false")
    if authority.get("consumer_must_remap_instruments") is not True:
        blockers.append("instrument-remapping boundary missing")

    positions = payload.get("position_targets") if isinstance(payload.get("position_targets"), list) else []
    exposures = payload.get("exposure_targets") if isinstance(payload.get("exposure_targets"), list) else []
    if not positions or not exposures:
        blockers.append("position or exposure targets are empty")
        return blockers

    tickers = [str(row.get("ticker") or "") for row in positions if isinstance(row, dict)]
    if any(not ticker for ticker in tickers):
        blockers.append("position target has empty ticker")
    duplicates = sorted({ticker for ticker in tickers if ticker and tickers.count(ticker) > 1})
    if duplicates:
        blockers.append("duplicate position tickers: " + ", ".join(duplicates))

    exposure_totals: dict[str, tuple[float, float]] = {}
    for row in exposures:
        if not isinstance(row, dict):
            blockers.append("exposure target is not an object")
            continue
        exposure_id = str(row.get("exposure_id") or "")
        if not exposure_id:
            blockers.append("exposure target has empty exposure_id")
            continue
        exposure_totals[exposure_id] = (float(row.get("current_weight_pct") or 0), float(row.get("target_weight_pct") or 0))

    reconstructed: dict[str, list[float]] = {}
    for row in positions:
        if not isinstance(row, dict):
            continue
        if row.get("portfolio_mutation") is not False:
            blockers.append(f"position {row.get('ticker')} violates mutation boundary")
        exposure_id = str(row.get("exposure_id") or "")
        values = reconstructed.setdefault(exposure_id, [0.0, 0.0])
        values[0] += float(row.get("current_weight_pct") or 0)
        values[1] += float(row.get("target_weight_pct") or 0)
    for exposure_id, values in reconstructed.items():
        actual = exposure_totals.get(exposure_id)
        if actual is None:
            blockers.append(f"missing aggregate for exposure {exposure_id}")
        elif abs(actual[0] - values[0]) > 0.001 or abs(actual[1] - values[1]) > 0.001:
            blockers.append(f"exposure aggregate mismatch for {exposure_id}")

    summary = payload.get("portfolio_summary") if isinstance(payload.get("portfolio_summary"), dict) else {}
    total = float(summary.get("target_weight_total_pct") or 0)
    if abs(total - 100.0) > 0.1:
        blockers.append(f"target weights plus cash do not reconcile to 100%: {total}")
    if int(summary.get("position_count") or 0) != len(positions):
        blockers.append("portfolio summary position_count mismatch")

    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("position_count") != len(positions):
        blockers.append("validation position_count mismatch")
    if validation.get("mapped_position_count") != len(positions):
        blockers.append("all donor positions must map to exposure IDs")
    if validation.get("unmapped_tickers") not in ([], None):
        blockers.append("unmapped donor tickers remain")
    if validation.get("weight_reconciliation_status") != "pass":
        blockers.append("weight reconciliation did not pass")
    if validation.get("portfolio_mutation") is not False:
        blockers.append("validation portfolio_mutation must be false")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate shared ETF exposure portfolio target")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = _load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_shared_portfolio_target_validation",
        "path": str(args.path),
        "valid": not blockers,
        "blockers": blockers,
        "position_count": len(payload.get("position_targets") or []),
        "exposure_count": len(payload.get("exposure_targets") or []),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
