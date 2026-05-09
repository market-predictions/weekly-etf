from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .close_resolver import CloseResolver
from .models import PriceRequest

PRICING_DIR = Path("output/pricing")
LANE_DIR = Path("output/lane_reviews")
PORTFOLIO_STATE_PATH = Path("output/etf_portfolio_state.json")
MACRO_CONTEXT_PATH = Path("config/etf_macro_fundamental_context.yml")

DEFAULT_TARGET_MAP: dict[str, list[str]] = {
    "SPY": ["QUAL", "IEFA", "EFA", "IWM"],
    "PPA": ["ITA", "DFEN", "NATO"],
    "PAVE": ["GRID", "XLU", "VPU"],
    "GLD": ["GSG", "DBC", "BIL"],
    "URNM": ["URA", "NLR", "NUCL"],
    "SMH": ["SOXX", "IRBO", "BOTZ", "ROBO"],
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


def _symbol(value: Any) -> str:
    raw = str(value or "").strip().upper()
    if raw in {"", "NONE", "NAN", "NULL", "N/A", "-"}:
        return ""
    return raw


def already_priced_symbols(audit: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for row in audit.get("prices", []) or []:
        symbol = _symbol(row.get("symbol"))
        if symbol and row.get("price") is not None:
            out.add(symbol)
    for row in audit.get("holdings", []) or []:
        symbol = _symbol(row.get("ticker"))
        if symbol and row.get("previous_price_local") is not None:
            out.add(symbol)
    return out


def held_tickers(path: Path = PORTFOLIO_STATE_PATH) -> set[str]:
    if not path.exists():
        return set()
    payload = load_json(path)
    return {
        _symbol(row.get("ticker"))
        for row in payload.get("positions", []) or []
        if _symbol(row.get("ticker")) and _symbol(row.get("ticker")) != "CASH"
    }


def replacement_target_map(macro_path: Path = MACRO_CONTEXT_PATH) -> dict[str, list[str]]:
    macro = load_yaml(macro_path)
    configured = ((macro.get("replacement_duel_policy") or {}).get("target_map") or {})
    if not configured:
        return DEFAULT_TARGET_MAP

    out: dict[str, list[str]] = {}
    for holding, payload in configured.items():
        holding_symbol = _symbol(holding)
        if not holding_symbol:
            continue
        challengers = payload.get("challengers", []) if isinstance(payload, dict) else payload
        out[holding_symbol] = [_symbol(item) for item in (challengers or []) if _symbol(item)]
    return out or DEFAULT_TARGET_MAP


def replacement_duel_symbols(held: set[str], macro_path: Path = MACRO_CONTEXT_PATH) -> list[str]:
    """Symbols required by Replacement Duel Table v2.

    The old two-pass augmenter only priced symbols discovered in the lane artifact.
    Replacement Duel Table v2 is driven by the replacement target map, so symbols
    such as IWM, QUAL, EFA, ITA, GRID or BIL can appear in the report even when
    they are not promoted live-radar lanes. These must be priced first, otherwise
    the table shows direct RS edges but says close pricing is missing.
    """
    symbols: list[str] = []
    target_map = replacement_target_map(macro_path)
    for holding, challengers in target_map.items():
        if holding not in held:
            continue
        for challenger in challengers:
            if challenger and challenger not in symbols:
                symbols.append(challenger)
    return symbols


def discovery_candidate_symbols(lane_artifact: dict[str, Any], max_symbols: int) -> list[str]:
    lanes = sorted(
        lane_artifact.get("assessed_lanes", []) or [],
        key=lambda lane: float(lane.get("total_score", 0.0) or 0.0),
        reverse=True,
    )
    symbols: list[str] = []

    prioritized = [lane for lane in lanes if lane.get("promoted_to_live_radar") is True]
    prioritized += [lane for lane in lanes if lane.get("challenger") is True]
    prioritized += lanes

    for lane in prioritized:
        for key in ("primary_etf", "alternative_etf"):
            symbol = _symbol(lane.get(key))
            if not symbol or symbol == "CASH":
                continue
            if symbol not in symbols:
                symbols.append(symbol)
            if len(symbols) >= max_symbols:
                return symbols
    return symbols


def ordered_unique(symbols: list[str]) -> list[str]:
    out: list[str] = []
    for symbol in symbols:
        symbol = _symbol(symbol)
        if symbol and symbol not in out:
            out.append(symbol)
    return out


def merge_price_results(audit: dict[str, Any], new_results: list[dict[str, Any]]) -> dict[str, Any]:
    merged = dict(audit)
    existing = {str(row.get("symbol", "")).upper(): row for row in merged.get("prices", []) or []}
    for row in new_results:
        symbol = str(row.get("symbol", "")).upper()
        if not symbol:
            continue
        old = existing.get(symbol)
        if old is None or (old.get("price") is None and row.get("price") is not None) or row.get("status") in {"fresh_close", "fresh_fallback_source"}:
            existing[symbol] = row
    merged["prices"] = list(existing.values())
    merged["price_results"] = merged["prices"]
    merged["two_pass_challenger_pricing"] = {
        "enabled": True,
        "added_or_refreshed_symbols": [row.get("symbol") for row in new_results],
        "priced_count": sum(1 for row in new_results if row.get("price") is not None),
        "selection_policy": "replacement_duel_targets_first_then_lane_candidates",
    }
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--lane-artifact", default=None)
    parser.add_argument("--max-symbols", type=int, default=24)
    parser.add_argument("--source-registry", default="pricing/source_registry.yaml")
    parser.add_argument("--rate-limit-file", default="pricing/rate_limits.yaml")
    parser.add_argument("--portfolio-state", default=str(PORTFOLIO_STATE_PATH))
    parser.add_argument("--macro-context", default=str(MACRO_CONTEXT_PATH))
    args = parser.parse_args()

    audit_path = Path(args.pricing_audit) if args.pricing_audit else latest_file(PRICING_DIR, "price_audit_*.json")
    lane_path = Path(args.lane_artifact) if args.lane_artifact else latest_file(LANE_DIR, "etf_lane_assessment_*.json")

    audit = load_json(audit_path)
    lane_artifact = load_json(lane_path)
    requested_close_date = str(audit.get("requested_close_date") or date.today().isoformat())
    run_date = str(audit.get("run_date") or date.today().isoformat())

    existing = already_priced_symbols(audit)
    held = held_tickers(Path(args.portfolio_state))
    duel_symbols = replacement_duel_symbols(held, Path(args.macro_context))
    lane_symbols = discovery_candidate_symbols(lane_artifact, args.max_symbols * 2)
    selected = [s for s in ordered_unique(duel_symbols + lane_symbols) if s not in existing]
    candidates = selected[: args.max_symbols]

    if not candidates:
        audit["two_pass_challenger_pricing"] = {
            "enabled": True,
            "added_or_refreshed_symbols": [],
            "priced_count": 0,
            "note": "No unpriced replacement-duel or lane challenger symbols selected.",
            "selection_policy": "replacement_duel_targets_first_then_lane_candidates",
        }
        audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
        print(f"TWO_PASS_CHALLENGER_PRICING_SKIPPED | audit={audit_path} | reason=no_unpriced_candidates")
        return

    resolver = CloseResolver(args.source_registry, args.rate_limit_file, run_date)
    new_results = []
    for symbol in candidates:
        result = resolver.resolve(
            PriceRequest(symbol=symbol, requested_close_date=requested_close_date, kind="challenger")
        )
        new_results.append(result.to_dict())

    augmented = merge_price_results(audit, new_results)
    audit_path.write_text(json.dumps(augmented, indent=2, sort_keys=True), encoding="utf-8")
    priced_count = sum(1 for row in new_results if row.get("price") is not None)
    print(
        "TWO_PASS_CHALLENGER_PRICING_OK | "
        f"selected={len(candidates)} | priced={priced_count} | duel_targets={len([s for s in duel_symbols if s not in existing])} | audit={audit_path}"
    )


if __name__ == "__main__":
    main()
