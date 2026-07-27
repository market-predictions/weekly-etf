from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_DIR = Path("output/runtime")
DEFAULT_OUTPUT_DIR = Path("output/shared")


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Required JSON input is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _latest(directory: Path, pattern: str) -> Path:
    paths = sorted(directory.glob(pattern), key=lambda path: (path.stat().st_mtime, path.name))
    if not paths:
        raise RuntimeError(f"No files matching {pattern!r} in {directory}")
    return paths[-1]


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _lane_index(shared: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    primary: dict[str, dict[str, Any]] = {}
    alternative: dict[str, dict[str, Any]] = {}
    for lane in shared.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        p = str(lane.get("us_primary_etf") or "").upper()
        a = str(lane.get("us_alternative_etf") or "").upper()
        if p and p not in primary:
            primary[p] = lane
        if a and a not in alternative:
            alternative[a] = lane
    return primary, alternative


def _rotation_index(rotation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rotation.get("rotation_decisions") or []:
        if isinstance(row, dict) and row.get("ticker"):
            result[str(row["ticker"]).upper()] = row
    return result


def _target_index(rotation: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for row in rotation.get("target_weights") or []:
        if isinstance(row, dict) and row.get("ticker"):
            result[str(row["ticker"]).upper()] = _num(row.get("target_weight_pct"))
    return result


def _resolve_exposure(
    ticker: str,
    primary: dict[str, dict[str, Any]],
    alternative: dict[str, dict[str, Any]],
) -> tuple[str | None, dict[str, Any] | None, str]:
    if ticker in primary:
        lane = primary[ticker]
        return str(lane.get("exposure_id") or "") or None, lane, "primary_etf_match"
    if ticker in alternative:
        lane = alternative[ticker]
        return str(lane.get("exposure_id") or "") or None, lane, "alternative_etf_match"
    return None, None, "unmapped"


def build_target(
    shared: dict[str, Any],
    runtime: dict[str, Any],
    rotation: dict[str, Any],
    shared_path: Path,
    runtime_path: Path,
    rotation_path: Path,
) -> dict[str, Any]:
    if shared.get("schema_version") != "etf_shared_strategy_state_v1":
        raise RuntimeError("Unsupported shared strategy state schema")
    if str(shared.get("source_run_id")) != str(runtime.get("run_id")):
        raise RuntimeError("Shared strategy state and runtime state run IDs differ")
    if str(rotation.get("run_id")) != str(runtime.get("run_id")):
        raise RuntimeError("Rotation plan and runtime state run IDs differ")

    primary, alternative = _lane_index(shared)
    rotation_by_ticker = _rotation_index(rotation)
    target_by_ticker = _target_index(rotation)
    positions = [row for row in (runtime.get("positions") or []) if isinstance(row, dict)]

    position_targets: list[dict[str, Any]] = []
    exposure_accumulator: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "current_weight_pct": 0.0,
            "target_weight_pct": 0.0,
            "source_tickers": [],
            "actions": [],
            "position_scores": [],
            "fresh_cash_tests": [],
            "promoted_in_shared_radar": False,
        }
    )
    unmapped: list[str] = []

    for position in positions:
        ticker = str(position.get("ticker") or "").upper()
        if not ticker or _num(position.get("shares")) <= 0:
            continue
        exposure_id, lane, mapping_status = _resolve_exposure(ticker, primary, alternative)
        if not exposure_id:
            exposure_id = f"unmapped_{ticker.lower()}"
            unmapped.append(ticker)

        decision = rotation_by_ticker.get(ticker, {})
        current_weight = _num(position.get("current_weight_pct"))
        target_weight = target_by_ticker.get(ticker, _num(position.get("target_weight_pct"), current_weight))
        action_code = str(decision.get("action_code") or position.get("rotation_action_code") or position.get("suggested_action") or "hold")

        row = {
            "ticker": ticker,
            "exposure_id": exposure_id,
            "lane_name": lane.get("lane_name") if lane else None,
            "mapping_status": mapping_status,
            "current_weight_pct": round(current_weight, 6),
            "target_weight_pct": round(target_weight, 6),
            "delta_weight_pct": round(target_weight - current_weight, 6),
            "current_market_value_eur": round(_num(position.get("market_value_eur")), 2),
            "action_code": action_code,
            "release_score": decision.get("release_score", position.get("rotation_release_score")),
            "role_validity": decision.get("role_validity"),
            "fresh_cash_test": position.get("fresh_cash_test"),
            "would_initiate_today": position.get("would_initiate_today"),
            "would_initiate_at_current_weight": position.get("would_initiate_at_current_weight"),
            "replaceable_status": position.get("replaceable_status"),
            "weeks_replaceable": position.get("weeks_replaceable"),
            "position_score": _num(position.get("total_score")),
            "portfolio_role": position.get("portfolio_role"),
            "reason_codes": list(decision.get("reason_codes") or position.get("rotation_reason_codes") or []),
            "override_status": decision.get("override_status", position.get("rotation_override_status")),
            "override_reason_code": decision.get("override_reason_code", position.get("rotation_override_reason_code")),
            "promoted_in_shared_radar": bool(lane and lane.get("promoted") is True),
            "portfolio_mutation": False,
        }
        position_targets.append(row)

        aggregate = exposure_accumulator[exposure_id]
        aggregate["current_weight_pct"] += current_weight
        aggregate["target_weight_pct"] += target_weight
        aggregate["source_tickers"].append(ticker)
        aggregate["actions"].append(action_code)
        aggregate["position_scores"].append(_num(position.get("total_score")))
        if position.get("fresh_cash_test"):
            aggregate["fresh_cash_tests"].append(str(position.get("fresh_cash_test")))
        aggregate["promoted_in_shared_radar"] = aggregate["promoted_in_shared_radar"] or bool(lane and lane.get("promoted") is True)
        aggregate["lane_name"] = lane.get("lane_name") if lane else None

    exposure_targets: list[dict[str, Any]] = []
    for exposure_id, aggregate in exposure_accumulator.items():
        scores = aggregate.pop("position_scores")
        aggregate["current_weight_pct"] = round(aggregate["current_weight_pct"], 6)
        aggregate["target_weight_pct"] = round(aggregate["target_weight_pct"], 6)
        aggregate["delta_weight_pct"] = round(aggregate["target_weight_pct"] - aggregate["current_weight_pct"], 6)
        aggregate["source_tickers"] = sorted(set(aggregate["source_tickers"]))
        aggregate["actions"] = sorted(set(aggregate["actions"]))
        aggregate["fresh_cash_tests"] = sorted(set(aggregate["fresh_cash_tests"]))
        aggregate["mean_position_score"] = round(sum(scores) / len(scores), 4) if scores else None
        exposure_targets.append({"exposure_id": exposure_id, **aggregate})
    exposure_targets.sort(key=lambda row: (-_num(row.get("target_weight_pct")), str(row.get("exposure_id"))))

    portfolio = runtime.get("portfolio") if isinstance(runtime.get("portfolio"), dict) else {}
    nav = _num(portfolio.get("total_portfolio_value_eur"))
    cash = _num(portfolio.get("cash_eur"))
    cash_weight = round(cash / nav * 100.0, 6) if nav else 0.0
    target_weight_total = round(sum(_num(row.get("target_weight_pct")) for row in position_targets) + cash_weight, 6)
    constraint_validation = rotation.get("portfolio_constraint_validation") if isinstance(rotation.get("portfolio_constraint_validation"), dict) else {}
    initial_assessment = constraint_validation.get("initial_position_count_assessment") if isinstance(constraint_validation.get("initial_position_count_assessment"), dict) else {}

    return {
        "schema_version": "etf_shared_portfolio_target_v1",
        "artifact_type": "etf_shared_exposure_portfolio_target",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": runtime.get("report_date"),
        "source_repository": "market-predictions/weekly-etf",
        "source_run_id": runtime.get("run_id"),
        "authority": {
            "portfolio_reference_authority": True,
            "portfolio_mutation": False,
            "funding_authority": False,
            "execution_authority": False,
            "consumer_must_remap_instruments": True,
        },
        "source_files": {
            "shared_strategy_state": str(shared_path),
            "runtime_state": str(runtime_path),
            "rotation_plan": str(rotation_path),
        },
        "portfolio_summary": {
            "base_currency": portfolio.get("base_currency"),
            "nav_eur": nav,
            "cash_eur": cash,
            "cash_weight_pct": cash_weight,
            "position_count": len(position_targets),
            "target_weight_total_pct": target_weight_total,
            "trade_intent_count": len(rotation.get("trade_intents") or []),
            "target_basis": "validated_rotation_plan_target_weights",
        },
        "position_targets": position_targets,
        "exposure_targets": exposure_targets,
        "constraints": {
            "max_active_positions": (rotation.get("policy") or {}).get("max_active_positions"),
            "current_active_positions": initial_assessment.get("current_count", len(position_targets)),
            "position_count_status": initial_assessment.get("status"),
            "block_reason": constraint_validation.get("block_reason"),
            "leveraged_etfs_allowed": (rotation.get("policy") or {}).get("leveraged_etfs_allowed"),
            "trade_intents_empty": len(rotation.get("trade_intents") or []) == 0,
        },
        "validation": {
            "position_count": len(position_targets),
            "mapped_position_count": len(position_targets) - len(unmapped),
            "unmapped_tickers": sorted(unmapped),
            "weight_reconciliation_status": "pass" if abs(target_weight_total - 100.0) <= 0.1 else "fail",
            "target_weight_total_pct": target_weight_total,
            "portfolio_mutation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build shared exposure-level portfolio target")
    parser.add_argument("--shared-strategy-state", type=Path, required=True)
    parser.add_argument("--runtime-state", type=Path)
    parser.add_argument("--rotation-plan", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    runtime_path = args.runtime_state or _latest(DEFAULT_RUNTIME_DIR, "etf_report_state_*.json")
    runtime = _load(runtime_path)
    rotation_source = ((runtime.get("source_files") or {}).get("rotation_plan") if isinstance(runtime.get("source_files"), dict) else None)
    rotation_path = args.rotation_plan or (Path(str(rotation_source)) if rotation_source else _latest(DEFAULT_RUNTIME_DIR, "etf_rotation_plan_*.json"))
    shared = _load(args.shared_strategy_state)
    state = build_target(
        shared=shared,
        runtime=runtime,
        rotation=_load(rotation_path),
        shared_path=args.shared_strategy_state,
        runtime_path=runtime_path,
        rotation_path=rotation_path,
    )

    output = args.output
    if output is None:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = DEFAULT_OUTPUT_DIR / f"etf_shared_portfolio_target_{state['report_date']}_{state['source_run_id']}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
