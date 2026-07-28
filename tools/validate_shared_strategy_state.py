from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class SharedStrategyStateError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SharedStrategyStateError(f"Shared strategy state is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SharedStrategyStateError("Shared strategy state must be a JSON object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []

    if payload.get("schema_version") != "etf_shared_strategy_state_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_shared_strategy_decision_state":
        blockers.append("unexpected artifact_type")
    if payload.get("source_repository") != "market-predictions/weekly-etf":
        blockers.append("unexpected source_repository")
    if not payload.get("report_date") or not payload.get("source_run_id"):
        blockers.append("missing report_date or source_run_id")

    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    if authority.get("strategy_research_authority") is not True:
        blockers.append("strategy research authority is not explicit")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "broker_execution_authority"):
        if authority.get(key) is not False:
            blockers.append(f"{key} must be false")
    if authority.get("consumer_must_apply_local_implementation_constraints") is not True:
        blockers.append("consumer implementation-constraint boundary is missing")

    source_files = payload.get("source_files") if isinstance(payload.get("source_files"), dict) else {}
    for key in ("lane_assessment", "runtime_state", "portfolio_state"):
        if not source_files.get(key):
            blockers.append(f"missing source file lineage: {key}")

    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), list) else []
    if not lanes:
        blockers.append("lanes is empty")
        return blockers

    exposure_ids = [str(lane.get("exposure_id") or "") for lane in lanes if isinstance(lane, dict)]
    if any(not value for value in exposure_ids):
        blockers.append("one or more lanes have an empty exposure_id")
    duplicates = sorted({value for value in exposure_ids if value and exposure_ids.count(value) > 1})
    if duplicates:
        blockers.append("duplicate exposure_ids: " + ", ".join(duplicates))

    ranks = [lane.get("rank") for lane in lanes if isinstance(lane, dict)]
    if ranks != list(range(1, len(lanes) + 1)):
        blockers.append("lane ranks must be contiguous and sorted")

    previous_score: float | None = None
    promoted_ids: list[str] = []
    for lane in lanes:
        if not isinstance(lane, dict):
            blockers.append("lane row is not an object")
            continue
        scores = lane.get("scores") if isinstance(lane.get("scores"), dict) else {}
        required_scores = (
            "methodology_base",
            "market_evidence_adjustment",
            "macro_adjustment",
            "donor_context_adjustment",
            "donor_final_rank_score",
        )
        if any(key not in scores for key in required_scores):
            blockers.append(f"lane {lane.get('exposure_id')} has incomplete score decomposition")
            continue
        current_score = float(scores["donor_final_rank_score"])
        if previous_score is not None and current_score > previous_score + 1e-9:
            blockers.append("lanes are not sorted by donor_final_rank_score")
        previous_score = current_score
        reconstructed = sum(float(scores[key]) for key in required_scores[:-1])
        if abs(reconstructed - current_score) > 0.011:
            blockers.append(f"lane {lane.get('exposure_id')} score decomposition does not reconcile")
        if lane.get("desired_direction") not in {
            "add_candidate",
            "hold_or_monitor",
            "watch",
            "avoid_or_underweight",
        }:
            blockers.append(f"lane {lane.get('exposure_id')} has invalid desired_direction")
        if lane.get("promoted") is True:
            promoted_ids.append(str(lane.get("exposure_id")))

    promoted = payload.get("promoted_exposures") if isinstance(payload.get("promoted_exposures"), list) else []
    promoted_contract_ids = [str(row.get("exposure_id") or "") for row in promoted if isinstance(row, dict)]
    if promoted_contract_ids != promoted_ids:
        blockers.append("promoted_exposures does not match promoted lane order")
    if [row.get("rank") for row in promoted if isinstance(row, dict)] != list(range(1, len(promoted) + 1)):
        blockers.append("promoted ranks must be contiguous")

    portfolio_context = payload.get("portfolio_context") if isinstance(payload.get("portfolio_context"), dict) else {}
    if portfolio_context.get("context_is_not_consumer_instruction") is not True:
        blockers.append("portfolio context boundary is missing")

    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("lane_count") != len(lanes):
        blockers.append("validation lane_count mismatch")
    if validation.get("promoted_count") != len(promoted):
        blockers.append("validation promoted_count mismatch")
    if validation.get("duplicate_exposure_ids") not in ([], None):
        blockers.append("validation reports duplicate exposure IDs")
    if validation.get("portfolio_context_separation_status") not in {"partial_v1", "complete"}:
        blockers.append("invalid portfolio_context_separation_status")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate shared ETF strategy decision state")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    payload = _load(args.path)
    blockers = validate(payload)
    result = {
        "artifact_type": "etf_shared_strategy_state_validation",
        "path": str(args.path),
        "valid": not blockers,
        "blockers": blockers,
        "lane_count": len(payload.get("lanes") or []),
        "promoted_count": len(payload.get("promoted_exposures") or []),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
