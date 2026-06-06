from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.map_challenger_to_current_holding import (
    ReplacementMapping,
    map_challenger_to_current_holding,
)

LANE_DIR = Path("output/lane_reviews")
RS_PATH = Path("output/market_history/etf_relative_strength.json")
PORTFOLIO_STATE_PATH = Path("output/etf_portfolio_state.json")
OUTPUT_DIR = Path("output/replacement_edges")
SCHEMA_VERSION = "replacement_edge_scoring_v1"
ARTIFACT_TYPE = "direct_challenger_vs_current_holding_scoring"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def _metrics_by_symbol(relative_strength_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    metrics = relative_strength_payload.get("metrics") or {}
    if not isinstance(metrics, dict):
        return {}
    return {str(symbol).upper(): dict(payload or {}) for symbol, payload in metrics.items()}


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _edge(challenger_value: Any, current_value: Any) -> float | None:
    challenger = _num(challenger_value)
    current = _num(current_value)
    if challenger is None or current is None:
        return None
    return round(challenger - current, 2)


def _volatility_edge(challenger_value: Any, current_value: Any) -> float | None:
    challenger = _num(challenger_value)
    current = _num(current_value)
    if challenger is None or current is None:
        return None
    return round(current - challenger, 2)


def replacement_edge_score(
    one_month_edge: float | None,
    three_month_edge: float | None,
    drawdown_edge: float | None,
    volatility_edge: float | None,
) -> float:
    weighted_terms: list[tuple[float, float, float]] = []
    if one_month_edge is not None:
        weighted_terms.append((one_month_edge, 10.0, 0.30))
    if three_month_edge is not None:
        weighted_terms.append((three_month_edge, 20.0, 0.45))
    if drawdown_edge is not None:
        weighted_terms.append((drawdown_edge, 15.0, 0.15))
    if volatility_edge is not None:
        weighted_terms.append((volatility_edge, 20.0, 0.10))

    if not weighted_terms:
        return 0.0

    score = 0.0
    total_weight = 0.0
    for value, scale, weight in weighted_terms:
        normalized = max(min(value / scale, 1.0), -1.0)
        score += normalized * weight
        total_weight += weight
    if total_weight < 1.0:
        score = score / total_weight
    return round(max(min(score, 1.0), -1.0), 2)


def _source_field(metrics: dict[str, Any], key: str) -> Any:
    return metrics.get(key)


def score_replacement_edge(mapping: ReplacementMapping, metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    challenger_metrics = metrics.get(mapping.challenger, {})
    current_metrics = metrics.get(mapping.current_holding, {})

    one_month = _edge(
        _source_field(challenger_metrics, "return_1m_pct"),
        _source_field(current_metrics, "return_1m_pct"),
    )
    three_month = _edge(
        _source_field(challenger_metrics, "return_3m_pct"),
        _source_field(current_metrics, "return_3m_pct"),
    )
    drawdown = _edge(
        _source_field(challenger_metrics, "max_drawdown_3m_pct"),
        _source_field(current_metrics, "max_drawdown_3m_pct"),
    )
    volatility = _volatility_edge(
        _source_field(challenger_metrics, "volatility_3m_pct"),
        _source_field(current_metrics, "volatility_3m_pct"),
    )
    score = replacement_edge_score(one_month, three_month, drawdown, volatility)
    available = sum(value is not None for value in (one_month, three_month, drawdown, volatility))

    return {
        "current_holding": mapping.current_holding,
        "challenger": mapping.challenger,
        "1m_relative_strength_edge": one_month,
        "3m_relative_strength_edge": three_month,
        "drawdown_edge": drawdown,
        "volatility_edge": volatility,
        "replacement_edge_score": score,
        "diagnostic_only": True,
        "portfolio_action_authority": False,
        "fundability_authority": False,
        "lane_scoring_authority": False,
        "mapping_confidence": mapping.mapping_confidence,
        "mapping_reason": mapping.mapping_reason,
        "scoring_status": "complete" if available == 4 else "partial_or_missing_market_history",
        "available_metric_count": available,
    }


def build_replacement_edge_artifact(
    lane_assessment_path: Path,
    relative_strength_path: Path,
    portfolio_state_path: Path,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lane_assessment = _load_json(lane_assessment_path)
    rs_payload = _load_json(relative_strength_path) if relative_strength_path.exists() else {}
    portfolio_state = _load_json(portfolio_state_path)
    metrics = _metrics_by_symbol(rs_payload)

    edges: list[dict[str, Any]] = []
    for lane in lane_assessment.get("assessed_lanes", []) or []:
        if not isinstance(lane, dict):
            continue
        if lane.get("challenger") is not True and "challenger" not in str(lane.get("prior_run_status", "")):
            continue
        mapping = map_challenger_to_current_holding(lane, portfolio_state)
        if not mapping:
            continue
        edges.append(score_replacement_edge(mapping, metrics))

    edges = sorted(edges, key=lambda item: float(item.get("replacement_edge_score", 0.0)), reverse=True)

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "run_id": run_id,
        "created_at_utc": created_at,
        "report_date": lane_assessment.get("report_date"),
        "inputs": {
            "lane_assessment": str(lane_assessment_path),
            "relative_strength": str(relative_strength_path) if relative_strength_path.exists() else None,
            "portfolio_state": str(portfolio_state_path),
        },
        "diagnostic_only": True,
        "portfolio_action_authority": False,
        "fundability_authority": False,
        "lane_scoring_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_recommendation_authority": False,
        "edges": edges,
    }


def write_replacement_edge_artifact(payload: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(payload.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    out_path = output_dir / f"replacement_edge_{run_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane-assessment", default=None)
    parser.add_argument("--relative-strength", default=str(RS_PATH))
    parser.add_argument("--portfolio-state", default=str(PORTFOLIO_STATE_PATH))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    lane_path = Path(args.lane_assessment) if args.lane_assessment else latest_file(LANE_DIR, "etf_lane_assessment_*.json")
    payload = build_replacement_edge_artifact(
        lane_path,
        Path(args.relative_strength),
        Path(args.portfolio_state),
        run_id=args.run_id,
    )
    out_path = write_replacement_edge_artifact(payload, Path(args.output_dir))
    print(
        "REPLACEMENT_EDGE_SCORING_BUILT | "
        f"edges={len(payload.get('edges', []))} | diagnostic_only=true | "
        "portfolio_action_authority=false | fundability_authority=false | lane_scoring_authority=false | "
        f"artifact={out_path}"
    )


if __name__ == "__main__":
    main()
