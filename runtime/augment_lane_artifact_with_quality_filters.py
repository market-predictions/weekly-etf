from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

LANE_DIR = Path("output/lane_reviews")
RS_PATH = Path("output/market_history/etf_relative_strength.json")
MACRO_PATH = Path("config/etf_macro_fundamental_context.yml")

REPLACEMENT_MAP = {
    "SPY": ["QUAL", "IEFA"],
    "PPA": ["ITA"],
    "PAVE": ["GRID"],
    "GLD": ["GSG", "BIL"],
}


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def metric(symbol: str, metrics: dict[str, Any], key: str) -> Any:
    return (metrics.get(symbol.upper(), {}) or {}).get(key)


def liquidity_adjustment(symbol: str, metrics: dict[str, Any], policy: dict[str, Any]) -> tuple[float, str]:
    avg_dv = metric(symbol, metrics, "avg_dollar_volume_3m")
    liq_score = metric(symbol, metrics, "liquidity_score")
    status = metric(symbol, metrics, "tradability_status") or "unknown"
    if avg_dv is None or liq_score is None:
        return -0.10, "Liquidity unknown; promoted only if other evidence is strong."
    min_promote = fnum(policy.get("min_avg_dollar_volume_promote"), 5_000_000)
    preferred = fnum(policy.get("preferred_avg_dollar_volume"), 20_000_000)
    if fnum(avg_dv) >= preferred:
        return 0.08, "Liquidity/tradability passes preferred threshold."
    if fnum(avg_dv) >= min_promote:
        return 0.02, "Liquidity/tradability passes minimum promotion threshold."
    return -0.35, "Liquidity/tradability below preferred promotion threshold."


def direct_holding_rs(symbol: str, metrics: dict[str, Any]) -> dict[str, Any]:
    symbol = symbol.upper()
    out: dict[str, Any] = {}
    symbol_r3 = metric(symbol, metrics, "return_3m_pct")
    for holding, challengers in REPLACEMENT_MAP.items():
        if symbol in challengers:
            holding_r3 = metric(holding, metrics, "return_3m_pct")
            if symbol_r3 is not None and holding_r3 is not None:
                out["direct_rs_vs_holding"] = holding
                out["direct_rs_vs_holding_3m_pct"] = round(fnum(symbol_r3) - fnum(holding_r3), 2)
                return out
    return out


def augment_lane(lane: dict[str, Any], metrics: dict[str, Any], macro: dict[str, Any]) -> dict[str, Any]:
    lane = dict(lane)
    primary = str(lane.get("primary_etf", "")).upper()
    bucket = str(lane.get("bucket", ""))
    bucket_context = (macro.get("bucket_adjustments", {}) or {}).get(bucket, {}) or {}
    liquidity_policy = macro.get("liquidity_policy", {}) or {}

    liq_adj, liq_note = liquidity_adjustment(primary, metrics, liquidity_policy)
    macro_adj = fnum(bucket_context.get("score_adjustment"), 0.0)
    direct = direct_holding_rs(primary, metrics)
    direct_adj = 0.0
    if direct.get("direct_rs_vs_holding_3m_pct") is not None:
        edge = fnum(direct.get("direct_rs_vs_holding_3m_pct"))
        direct_adj = max(min(edge / 20.0, 0.20), -0.20)

    lane["avg_dollar_volume_3m"] = metric(primary, metrics, "avg_dollar_volume_3m")
    lane["liquidity_score"] = metric(primary, metrics, "liquidity_score")
    lane["tradability_status"] = metric(primary, metrics, "tradability_status") or "unknown"
    lane["liquidity_note"] = liq_note
    lane["macro_freshness_note"] = bucket_context.get("freshness_note", "No specific macro freshness override.")
    lane.update(direct)
    lane["quality_filter_adjustment"] = round(liq_adj + macro_adj + direct_adj, 2)
    lane["total_score"] = round(fnum(lane.get("total_score")) + lane["quality_filter_adjustment"], 2)

    if lane["tradability_status"] == "fail_or_unknown" and lane.get("promoted_to_live_radar") is True:
        lane["rejection_reason"] = "Blocked from live radar because liquidity/tradability evidence is too weak."
        lane["promoted_to_live_radar"] = False
    elif lane.get("rejection_reason") and lane.get("direct_rs_vs_holding_3m_pct") is not None:
        lane["rejection_reason"] = f"{lane['rejection_reason']} Direct 3m RS versus {lane.get('direct_rs_vs_holding')} is {lane.get('direct_rs_vs_holding_3m_pct')}%."
    return lane


def repromote(lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for lane in lanes:
        lane["promoted_to_live_radar"] = False
    sorted_lanes = sorted(lanes, key=lambda row: fnum(row.get("total_score")), reverse=True)
    promoted = 0
    for lane in sorted_lanes:
        if promoted >= 6:
            break
        if lane.get("tradability_status") == "fail_or_unknown":
            continue
        lane["promoted_to_live_radar"] = True
        lane["rejection_reason"] = ""
        promoted += 1
    if promoted < 5:
        for lane in sorted_lanes:
            if promoted >= 5:
                break
            if lane.get("promoted_to_live_radar"):
                continue
            lane["promoted_to_live_radar"] = True
            lane["rejection_reason"] = ""
            promoted += 1
    return sorted_lanes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane-artifact", default=None)
    parser.add_argument("--relative-strength", default=str(RS_PATH))
    parser.add_argument("--macro-context", default=str(MACRO_PATH))
    args = parser.parse_args()

    lane_path = Path(args.lane_artifact) if args.lane_artifact else latest_file(LANE_DIR, "etf_lane_assessment_*.json")
    artifact = load_json(lane_path)
    rs_payload = load_json(Path(args.relative_strength)) if Path(args.relative_strength).exists() else {"metrics": {}}
    metrics = rs_payload.get("metrics", {}) or {}
    macro = load_yaml(Path(args.macro_context))

    artifact["discovery_engine_version"] = str(artifact.get("discovery_engine_version", "lane_discovery")) + "+quality_filters_v1"
    artifact.setdefault("discovery_inputs", {})["quality_filter_macro_context"] = str(args.macro_context)
    artifact.setdefault("quality_filter_summary", {})["enabled"] = True
    lanes = [augment_lane(lane, metrics, macro) for lane in artifact.get("assessed_lanes", [])]
    artifact["assessed_lanes"] = repromote(lanes)
    artifact["quality_filter_summary"]["promoted_count"] = sum(1 for lane in artifact["assessed_lanes"] if lane.get("promoted_to_live_radar"))
    artifact["quality_filter_summary"]["liquidity_checked"] = True
    artifact["quality_filter_summary"]["direct_holding_rs_checked"] = True
    lane_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"ETF_LANE_QUALITY_FILTERS_OK | artifact={lane_path} | promoted={artifact['quality_filter_summary']['promoted_count']}")


if __name__ == "__main__":
    main()
