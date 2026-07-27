from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LANE_WEIGHTS = {
    "structural_strength": 0.16,
    "persistence": 0.10,
    "implementation_quality": 0.11,
    "macro_alignment": 0.15,
    "second_order_relevance": 0.10,
    "timing_confirmation": 0.10,
    "valuation_crowding": 0.07,
    "portfolio_differentiation": 0.07,
}

DEFAULT_LANE_DIR = Path("output/lane_reviews")
DEFAULT_RUNTIME_DIR = Path("output/runtime")
DEFAULT_PORTFOLIO = Path("output/etf_portfolio_state.json")
DEFAULT_MACRO = Path("output/macro/latest.json")
DEFAULT_OUTPUT_DIR = Path("output/shared")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Required JSON input is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected a JSON object: {path}")
    return payload


def _latest(directory: Path, pattern: str) -> Path:
    paths = sorted(directory.glob(pattern), key=lambda path: (path.stat().st_mtime, path.name))
    if not paths:
        raise RuntimeError(f"No files matching {pattern!r} in {directory}")
    return paths[-1]


def _number(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _slug(value: Any) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    return text or "unnamed_exposure"


def _methodology_base(lane: dict[str, Any]) -> float:
    return round(sum(_number(lane.get(key)) * weight for key, weight in LANE_WEIGHTS.items()), 4)


def _desired_direction(lane: dict[str, Any], held_tickers: set[str]) -> str:
    promoted = lane.get("promoted_to_live_radar") is True
    primary = str(lane.get("primary_etf") or "").upper()
    alternative = str(lane.get("alternative_etf") or "").upper()
    funding = str(lane.get("fundability_status") or "")

    if primary in held_tickers or alternative in held_tickers or funding == "held_or_overlap_not_new_funding_candidate":
        return "hold_or_monitor"
    if promoted and funding == "funding_candidate_valuation_grade":
        return "add_candidate"
    if promoted:
        return "watch"
    if lane.get("challenger") is True or _number(lane.get("structural_strength")) >= 4:
        return "watch"
    return "avoid_or_underweight"


def _runtime_run_id(runtime: dict[str, Any], runtime_path: Path) -> str:
    for key in ("run_id", "runtime_run_id", "source_run_id"):
        if runtime.get(key):
            return str(runtime[key])
    match = re.search(r"_(\d{8}_\d{6})\.json$", runtime_path.name)
    return match.group(1) if match else runtime_path.stem


def _regime(macro: dict[str, Any]) -> dict[str, Any]:
    regime = macro.get("regime") if isinstance(macro.get("regime"), dict) else {}
    memory = macro.get("regime_memory") if isinstance(macro.get("regime_memory"), dict) else {}
    confidence = regime.get("confidence")
    confidence_num = None if confidence in (None, "") else _number(confidence)
    if confidence_num is not None and confidence_num <= 1.0:
        confidence_num = round(confidence_num * 100.0, 2)
    return {
        "current": regime.get("current"),
        "confidence_pct": confidence_num,
        "what_changed": [str(item) for item in (regime.get("what_changed") or [])],
        "decision_rule": memory.get("decision_rule"),
        "source_report_date": macro.get("report_date"),
        "source_generated_at_utc": macro.get("generated_at_utc"),
    }


def build_shared_strategy_state(
    lane_path: Path,
    runtime_path: Path,
    portfolio_path: Path,
    macro_path: Path | None,
) -> dict[str, Any]:
    lane_payload = _load_json(lane_path)
    runtime = _load_json(runtime_path)
    portfolio = _load_json(portfolio_path)
    macro = _load_json(macro_path) if macro_path and macro_path.is_file() else {}

    report_date = str(
        lane_payload.get("report_date")
        or runtime.get("report_date")
        or runtime.get("requested_close_date")
        or ""
    )
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date):
        raise RuntimeError(f"Could not resolve an ISO report date from {lane_path} and {runtime_path}")

    positions = portfolio.get("positions") if isinstance(portfolio.get("positions"), list) else []
    held_tickers = {
        str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
        for position in positions
        if isinstance(position, dict) and _number(position.get("shares")) > 0
    }
    held_tickers.discard("")
    nav = _number(portfolio.get("nav_eur"))
    cash = _number(portfolio.get("cash_eur"))
    cash_pct = round(cash / nav * 100.0, 4) if nav else None

    assessed = lane_payload.get("assessed_lanes")
    if not isinstance(assessed, list) or not assessed:
        raise RuntimeError("Lane assessment has no assessed_lanes")

    sorted_lanes = sorted(
        [lane for lane in assessed if isinstance(lane, dict)],
        key=lambda lane: _number(lane.get("total_score")),
        reverse=True,
    )

    lanes: list[dict[str, Any]] = []
    promoted: list[dict[str, Any]] = []
    exposure_ids: list[str] = []

    for rank, lane in enumerate(sorted_lanes, start=1):
        exposure_id = _slug(lane.get("taxonomy_tag") or lane.get("bucket") or lane.get("lane_name"))
        exposure_ids.append(exposure_id)
        base_score = _methodology_base(lane)
        market_adjustment = round(_number(lane.get("relative_strength_score")), 4)
        macro_adjustment = round(_number(lane.get("macro_policy_adjustment")), 4)
        final_score = round(_number(lane.get("total_score")), 4)
        donor_context_adjustment = round(final_score - base_score - market_adjustment - macro_adjustment, 4)
        direction = _desired_direction(lane, held_tickers)
        is_promoted = lane.get("promoted_to_live_radar") is True

        market_evidence = {
            key: lane.get(key)
            for key in (
                "return_1m_pct",
                "return_3m_pct",
                "trend_quality",
                "max_drawdown_3m_pct",
                "volatility_3m_pct",
                "rs_vs_spy_1m_pct",
                "rs_vs_spy_3m_pct",
                "relative_strength_score",
                "avg_volume_3m",
                "avg_dollar_volume_3m",
                "liquidity_score",
                "tradability_status",
                "direct_rs_vs_holding",
                "direct_rs_vs_holding_3m_pct",
            )
            if key in lane
        }

        row = {
            "rank": rank,
            "exposure_id": exposure_id,
            "lane_name": str(lane.get("lane_name") or exposure_id),
            "taxonomy_tag": lane.get("taxonomy_tag"),
            "bucket": lane.get("bucket"),
            "promoted": is_promoted,
            "challenger": lane.get("challenger") is True,
            "us_primary_etf": str(lane.get("primary_etf") or "").upper() or None,
            "us_alternative_etf": str(lane.get("alternative_etf") or "").upper() or None,
            "scores": {
                "methodology_base": base_score,
                "market_evidence_adjustment": market_adjustment,
                "macro_adjustment": macro_adjustment,
                "donor_context_adjustment": donor_context_adjustment,
                "donor_final_rank_score": final_score,
            },
            "market_evidence": market_evidence,
            "pricing_confidence": lane.get("pricing_confidence"),
            "fundability_status": lane.get("fundability_status"),
            "desired_direction": direction,
            "target_weight_range_pct": None,
            "evidence_summary": lane.get("evidence_summary"),
            "why_now": lane.get("why_now"),
            "rejection_reason": lane.get("non_promotion_reason") or lane.get("rejection_reason"),
            "what_would_change": lane.get("what_would_change"),
            "invalidation": lane.get("invalidation"),
            "macro_policy_reason": lane.get("macro_policy_reason"),
            "freshness_note": lane.get("freshness_note"),
        }
        lanes.append(row)
        if is_promoted:
            promoted.append(
                {
                    "rank": len(promoted) + 1,
                    "exposure_id": exposure_id,
                    "lane_name": row["lane_name"],
                    "desired_direction": direction,
                    "target_weight_range_pct": None,
                }
            )

    duplicates = sorted({value for value in exposure_ids if exposure_ids.count(value) > 1})
    source_run_id = _runtime_run_id(runtime, runtime_path)

    return {
        "schema_version": "etf_shared_strategy_state_v1",
        "artifact_type": "etf_shared_strategy_decision_state",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": report_date,
        "requested_close_date": runtime.get("requested_close_date") or report_date,
        "source_repository": "market-predictions/weekly-etf",
        "source_run_id": source_run_id,
        "authority": {
            "strategy_research_authority": True,
            "portfolio_mutation": False,
            "funding_authority": False,
            "execution_authority": False,
            "broker_execution_authority": False,
            "consumer_must_apply_local_implementation_constraints": True,
        },
        "source_files": {
            "lane_assessment": str(lane_path),
            "runtime_state": str(runtime_path),
            "portfolio_state": str(portfolio_path),
            "macro_policy_pack": str(macro_path) if macro_path and macro_path.is_file() else None,
        },
        "regime": _regime(macro),
        "portfolio_context": {
            "base_currency": portfolio.get("base_currency"),
            "cash_pct": cash_pct,
            "nav_eur": nav or None,
            "active_tickers": sorted(held_tickers),
            "position_count": len(held_tickers),
            "context_is_not_consumer_instruction": True,
        },
        "lanes": lanes,
        "promoted_exposures": promoted,
        "validation": {
            "lane_count": len(lanes),
            "promoted_count": len(promoted),
            "duplicate_exposure_ids": duplicates,
            "portfolio_context_separation_status": "partial_v1",
            "note": "V1 exposes the donor-context residual explicitly. A later donor refactor may separate pricing, novelty and portfolio-gap adjustments into individual fields without changing the final donor rank.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build read-only shared ETF strategy decision state")
    parser.add_argument("--lane-assessment", type=Path)
    parser.add_argument("--runtime-state", type=Path)
    parser.add_argument("--portfolio-state", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--macro-policy-pack", type=Path, default=DEFAULT_MACRO)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    lane_path = args.lane_assessment or _latest(DEFAULT_LANE_DIR, "etf_lane_assessment_*.json")
    runtime_path = args.runtime_state or _latest(DEFAULT_RUNTIME_DIR, "etf_report_state_*.json")
    state = build_shared_strategy_state(
        lane_path=lane_path,
        runtime_path=runtime_path,
        portfolio_path=args.portfolio_state,
        macro_path=args.macro_policy_pack,
    )

    output = args.output
    if output is None:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = DEFAULT_OUTPUT_DIR / (
            f"etf_shared_strategy_state_{state['report_date']}_{state['source_run_id']}.json"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
