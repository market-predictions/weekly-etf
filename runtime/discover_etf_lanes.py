from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from runtime.score_etf_lanes import (
    LaneContext,
    apply_promotion_flags,
    score_lane,
    select_promoted_lanes,
)

PRICING_DIR = Path("output/pricing")
LANE_DIR = Path("output/lane_reviews")
RS_PATH = Path("output/market_history/etf_relative_strength.json")
REPORT_RE = re.compile(r"weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def report_suffix_from_date(report_date: str) -> str:
    return report_date.replace("-", "")[2:]


def report_date_from_pricing(pricing_audit: dict[str, Any]) -> str:
    requested = pricing_audit.get("requested_close_date")
    if requested:
        return str(requested)
    return date.today().isoformat()


def prior_lane_artifact(current_report_suffix: str | None = None) -> dict[str, Any] | None:
    artifacts = sorted(LANE_DIR.glob("etf_lane_assessment_*.json"))
    if current_report_suffix:
        artifacts = [p for p in artifacts if not p.name.endswith(f"_{current_report_suffix}.json") and current_report_suffix not in p.name]
    if not artifacts:
        return None
    return load_json(artifacts[-1])


def held_tickers_from_portfolio_state(path: Path) -> set[str]:
    if not path.exists():
        return set()
    payload = load_json(path)
    tickers = set()
    for position in payload.get("positions", []) or []:
        ticker = str(position.get("ticker", "")).upper()
        if ticker and ticker != "CASH":
            tickers.add(ticker)
    return tickers


def pricing_context(pricing_audit: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    status_by_symbol: dict[str, str] = {}
    priced: set[str] = set()
    for item in pricing_audit.get("prices", []) or []:
        symbol = str(item.get("symbol", "")).upper()
        if not symbol:
            continue
        status = str(item.get("status", "unknown"))
        status_by_symbol[symbol] = status
        if item.get("price") is not None:
            priced.add(symbol)
    for item in pricing_audit.get("holdings", []) or []:
        symbol = str(item.get("ticker", "")).upper()
        if not symbol:
            continue
        status_by_symbol.setdefault(symbol, "holding_snapshot")
        if item.get("previous_price_local") is not None:
            priced.add(symbol)
    return status_by_symbol, priced


def prior_promoted_tickers(prior: dict[str, Any] | None) -> set[str]:
    if not prior:
        return set()
    out: set[str] = set()
    for lane in prior.get("assessed_lanes", []) or []:
        if lane.get("promoted_to_live_radar") is True:
            for key in ("primary_etf", "alternative_etf"):
                ticker = str(lane.get(key, "")).upper()
                if ticker:
                    out.add(ticker)
    return out


def relative_strength_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = load_json(path)
    return dict(payload.get("metrics", {}) or {})


def validate_discovery_payload(payload: dict[str, Any]) -> None:
    required_buckets = set(payload.get("required_breadth_buckets", []))
    lanes = payload.get("assessed_lanes", [])
    if len(lanes) < len(required_buckets):
        raise RuntimeError("Lane discovery produced too few assessed lanes.")
    buckets = {lane.get("bucket") for lane in lanes}
    missing = required_buckets - buckets
    if missing:
        raise RuntimeError("Lane discovery missing required buckets: " + ", ".join(sorted(missing)))
    challengers = [lane for lane in lanes if lane.get("challenger") is True]
    if len(challengers) < 4:
        raise RuntimeError(f"Lane discovery produced too few challengers: {len(challengers)}")
    promoted = [lane for lane in lanes if lane.get("promoted_to_live_radar") is True]
    if not (5 <= len(promoted) <= 8):
        raise RuntimeError(f"Lane discovery promoted invalid number of lanes: {len(promoted)}")


def build_lane_artifact(
    config_path: Path,
    portfolio_state_path: Path,
    pricing_audit_path: Path,
    relative_strength_path: Path = RS_PATH,
) -> tuple[dict[str, Any], Path]:
    config = load_yaml(config_path)
    pricing_audit = load_json(pricing_audit_path)
    report_date = report_date_from_pricing(pricing_audit)
    suffix = report_suffix_from_date(report_date)
    report_filename = f"weekly_analysis_pro_{suffix}.md"
    prior = prior_lane_artifact(suffix)

    status_by_symbol, priced_symbols = pricing_context(pricing_audit)
    rs_metrics = relative_strength_metrics(relative_strength_path)
    context = LaneContext(
        held_tickers=held_tickers_from_portfolio_state(portfolio_state_path),
        prior_promoted_tickers=prior_promoted_tickers(prior),
        price_status_by_symbol=status_by_symbol,
        priced_symbols=priced_symbols,
        portfolio_gap_themes=dict(config.get("portfolio_gap_themes", {}) or {}),
        relative_strength_metrics=rs_metrics,
    )

    lanes = [score_lane(lane, context) for lane in config.get("lanes", [])]
    lanes = sorted(lanes, key=lambda lane: float(lane.get("total_score", 0.0)), reverse=True)
    promoted = select_promoted_lanes(lanes, list(config.get("required_breadth_buckets", [])))
    lanes = apply_promotion_flags(lanes, promoted)

    payload = {
        "report_date": report_date,
        "report_filename": report_filename,
        "prior_report_filename": (prior or {}).get("report_filename"),
        "discovery_engine_version": "lane_discovery_v2_relative_strength",
        "discovery_inputs": {
            "config": str(config_path),
            "portfolio_state": str(portfolio_state_path),
            "pricing_audit": str(pricing_audit_path),
            "relative_strength": str(relative_strength_path) if relative_strength_path.exists() else None,
            "prior_lane_artifact": "latest_available" if prior else None,
        },
        "required_breadth_buckets": list(config.get("required_breadth_buckets", [])),
        "assessed_lanes": lanes,
    }
    validate_discovery_payload(payload)

    LANE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LANE_DIR / f"etf_lane_assessment_{suffix}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload, out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/etf_discovery_universe.yml")
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--relative-strength", default=str(RS_PATH))
    args = parser.parse_args()

    pricing_audit_path = Path(args.pricing_audit) if args.pricing_audit else latest_file(PRICING_DIR, "price_audit_*.json")
    payload, out_path = build_lane_artifact(
        Path(args.config),
        Path(args.portfolio_state),
        pricing_audit_path,
        Path(args.relative_strength),
    )
    promoted = [lane for lane in payload["assessed_lanes"] if lane.get("promoted_to_live_radar")]
    challengers = [lane for lane in payload["assessed_lanes"] if lane.get("challenger")]
    rs_used = bool(payload.get("discovery_inputs", {}).get("relative_strength"))
    print(
        "ETF_LANE_DISCOVERY_OK | "
        f"report={payload['report_filename']} | lanes={len(payload['assessed_lanes'])} | "
        f"promoted={len(promoted)} | challengers={len(challengers)} | rs_used={rs_used} | artifact={out_path}"
    )


if __name__ == "__main__":
    main()
