from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

LANE_DIR = Path("output/lane_reviews")
RS_PATH = Path("output/market_history/etf_relative_strength.json")
MACRO_PATH = Path("config/etf_macro_fundamental_context.yml")

DEFAULT_REPLACEMENT_MAP = {
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


def replacement_target_map(macro: dict[str, Any]) -> dict[str, list[str]]:
    policy = macro.get("replacement_duel_policy", {}) or {}
    target_map = policy.get("target_map", {}) or {}
    if not target_map:
        return DEFAULT_REPLACEMENT_MAP
    out: dict[str, list[str]] = {}
    for holding, payload in target_map.items():
        if isinstance(payload, dict):
            challengers = payload.get("challengers", []) or []
        else:
            challengers = payload or []
        out[str(holding).upper()] = [str(item).upper() for item in challengers]
    return out


def target_map_reason(macro: dict[str, Any], holding: str) -> str:
    policy = macro.get("replacement_duel_policy", {}) or {}
    payload = (policy.get("target_map", {}) or {}).get(holding, {}) or {}
    if isinstance(payload, dict):
        return str(payload.get("reason", ""))
    return ""


def liquidity_adjustment(symbol: str, metrics: dict[str, Any], policy: dict[str, Any]) -> tuple[float, str]:
    avg_dv = metric(symbol, metrics, "avg_dollar_volume_3m")
    liq_score = metric(symbol, metrics, "liquidity_score")
    if avg_dv is None or liq_score is None:
        return -0.10, "Liquidity unknown; promoted only if other evidence is strong."
    min_promote = fnum(policy.get("min_avg_dollar_volume_promote"), 5_000_000)
    preferred = fnum(policy.get("preferred_avg_dollar_volume"), 20_000_000)
    if fnum(avg_dv) >= preferred:
        return 0.08, "Liquidity/tradability passes preferred threshold."
    if fnum(avg_dv) >= min_promote:
        return 0.02, "Liquidity/tradability passes minimum promotion threshold."
    return -0.35, "Liquidity/tradability below preferred promotion threshold."


def _return_edge(symbol: str, holding: str, metrics: dict[str, Any], key: str) -> float | None:
    symbol_return = metric(symbol, metrics, key)
    holding_return = metric(holding, metrics, key)
    if symbol_return is None or holding_return is None:
        return None
    return round(fnum(symbol_return) - fnum(holding_return), 2)


def direct_holding_rs(symbol: str, metrics: dict[str, Any], macro: dict[str, Any]) -> dict[str, Any]:
    symbol = symbol.upper()
    out: dict[str, Any] = {}
    for holding, challengers in replacement_target_map(macro).items():
        if symbol not in challengers:
            continue
        edge_1m = _return_edge(symbol, holding, metrics, "return_1m_pct")
        edge_3m = _return_edge(symbol, holding, metrics, "return_3m_pct")
        if edge_1m is None and edge_3m is None:
            return out
        out["direct_rs_vs_holding"] = holding
        out["direct_rs_vs_holding_1m_pct"] = edge_1m
        out["direct_rs_vs_holding_3m_pct"] = edge_3m
        out["direct_rs_vs_holding_reason"] = target_map_reason(macro, holding)
        return out
    return out


def direct_rs_adjustment(direct: dict[str, Any], macro: dict[str, Any]) -> float:
    policy = macro.get("replacement_duel_policy", {}) or {}
    max_bonus = fnum(policy.get("direct_edge_max_bonus"), 0.25)
    max_penalty = fnum(policy.get("direct_edge_max_penalty"), -0.25)
    edge_1m = direct.get("direct_rs_vs_holding_1m_pct")
    edge_3m = direct.get("direct_rs_vs_holding_3m_pct")
    if edge_1m is None and edge_3m is None:
        return 0.0
    weighted = 0.0
    weight_total = 0.0
    if edge_1m is not None:
        weighted += fnum(edge_1m) * 0.35
        weight_total += 0.35
    if edge_3m is not None:
        weighted += fnum(edge_3m) * 0.65
        weight_total += 0.65
    edge = weighted / weight_total if weight_total else 0.0
    return round(max(min(edge / 20.0, max_bonus), max_penalty), 2)


def direct_rs_note(direct: dict[str, Any]) -> str:
    holding = direct.get("direct_rs_vs_holding")
    if not holding:
        return "No direct replacement-duel target mapped."
    e1 = direct.get("direct_rs_vs_holding_1m_pct")
    e3 = direct.get("direct_rs_vs_holding_3m_pct")
    edge_parts = []
    if e1 is not None:
        edge_parts.append(f"1m {e1}%")
    if e3 is not None:
        edge_parts.append(f"3m {e3}%")
    return f"Direct replacement duel versus {holding}: {'; '.join(edge_parts) if edge_parts else 'insufficient history'}."


def augment_lane(lane: dict[str, Any], metrics: dict[str, Any], macro: dict[str, Any]) -> dict[str, Any]:
    lane = dict(lane)
    primary = str(lane.get("primary_etf", "")).upper()
    bucket = str(lane.get("bucket", ""))
    bucket_context = (macro.get("bucket_adjustments", {}) or {}).get(bucket, {}) or {}
    liquidity_policy = macro.get("liquidity_policy", {}) or {}

    liq_adj, liq_note = liquidity_adjustment(primary, metrics, liquidity_policy)
    macro_adj = fnum(bucket_context.get("score_adjustment"), 0.0)
    direct = direct_holding_rs(primary, metrics, macro)
    direct_adj = direct_rs_adjustment(direct, macro)

    lane["avg_dollar_volume_3m"] = metric(primary, metrics, "avg_dollar_volume_3m")
    lane["liquidity_score"] = metric(primary, metrics, "liquidity_score")
    lane["tradability_status"] = metric(primary, metrics, "tradability_status") or "unknown"
    lane["liquidity_note"] = liq_note
    lane["macro_freshness_note"] = bucket_context.get("freshness_note", "No specific macro freshness override.")
    lane.update(direct)
    lane["direct_rs_adjustment"] = direct_adj
    lane["direct_rs_note"] = direct_rs_note(direct)
    lane["quality_filter_adjustment"] = round(liq_adj + macro_adj + direct_adj, 2)
    lane["total_score"] = round(fnum(lane.get("total_score")) + lane["quality_filter_adjustment"], 2)

    if lane["tradability_status"] == "fail_or_unknown" and lane.get("promoted_to_live_radar") is True:
        lane["rejection_reason"] = "Blocked from live radar because liquidity/tradability evidence is too weak."
        lane["promoted_to_live_radar"] = False
    elif lane.get("rejection_reason") and lane.get("direct_rs_vs_holding"):
        lane["rejection_reason"] = f"{lane['rejection_reason']} {lane['direct_rs_note']}"
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

    artifact["discovery_engine_version"] = str(artifact.get("discovery_engine_version", "lane_discovery")) + "+direct_replacement_rs_v1"
    artifact.setdefault("discovery_inputs", {})["quality_filter_macro_context"] = str(args.macro_context)
    artifact.setdefault("quality_filter_summary", {})["enabled"] = True
    lanes = [augment_lane(lane, metrics, macro) for lane in artifact.get("assessed_lanes", [])]
    artifact["assessed_lanes"] = repromote(lanes)
    artifact["quality_filter_summary"]["promoted_count"] = sum(1 for lane in artifact["assessed_lanes"] if lane.get("promoted_to_live_radar"))
    artifact["quality_filter_summary"]["liquidity_checked"] = True
    artifact["quality_filter_summary"]["direct_holding_rs_checked"] = True
    artifact["quality_filter_summary"]["direct_holding_rs_version"] = "v1_1m_3m_weighted"
    lane_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"ETF_LANE_QUALITY_FILTERS_OK | artifact={lane_path} | promoted={artifact['quality_filter_summary']['promoted_count']}")


if __name__ == "__main__":
    main()
