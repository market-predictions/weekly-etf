from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

RUNTIME_DIR = Path("output/runtime")
PRICING_DIR = Path("output/pricing")
LANE_DIR = Path("output/lane_reviews")


@dataclass
class RuntimeSources:
    portfolio_state: Path
    pricing_audit: Path
    lane_assessment: Path
    recommendation_scorecard: Path


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_scorecard(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
    return rows


def discover_sources() -> RuntimeSources:
    return RuntimeSources(
        portfolio_state=Path("output/etf_portfolio_state.json"),
        pricing_audit=latest_file(PRICING_DIR, "price_audit_*.json"),
        lane_assessment=latest_file(LANE_DIR, "etf_lane_assessment_*.json"),
        recommendation_scorecard=Path("output/etf_recommendation_scorecard.csv"),
    )


def _fx_rate(pricing_audit: dict[str, Any]) -> float | None:
    fx_basis = pricing_audit.get("fx_basis") or {}
    raw = fx_basis.get("rate")
    try:
        return None if raw is None else float(raw)
    except (TypeError, ValueError):
        return None


def build_runtime_state() -> dict[str, Any]:
    sources = discover_sources()

    portfolio_state = load_json(sources.portfolio_state)
    pricing_audit = load_json(sources.pricing_audit)
    lane_assessment = load_json(sources.lane_assessment)
    recommendation_scorecard = load_scorecard(sources.recommendation_scorecard)

    holdings = pricing_audit.get("holdings", [])
    prices = pricing_audit.get("prices", [])
    fx_basis = pricing_audit.get("fx_basis") or {}

    duel_candidates = []
    challenger_map = {
        "PPA": ["ITA"],
        "PAVE": ["GRID"],
        "GLD": ["GSG", "BIL"],
        "SPY": ["QUAL", "IEFA"],
    }

    for holding in holdings:
        ticker = holding.get("ticker")
        challengers = challenger_map.get(ticker, [])
        for challenger in challengers:
            challenger_price = next((p for p in prices if p.get("symbol") == challenger), None)
            duel_candidates.append(
                {
                    "current_holding": ticker,
                    "challenger": challenger,
                    "challenger_price": challenger_price,
                    "status": (
                        "priced_but_duel_incomplete"
                        if challenger_price
                        else "not_fundable_pricing_missing"
                    ),
                }
            )

    total_portfolio_value_eur = sum(
        float(h.get("previous_market_value_eur", 0.0) or 0.0)
        for h in holdings
    ) + float(portfolio_state.get("cash_eur", 0.0) or 0.0)

    runtime_state = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "report_date": lane_assessment.get("report_date"),
        "requested_close_date": pricing_audit.get("requested_close_date"),
        "source_files": {
            "portfolio_state": str(sources.portfolio_state),
            "pricing_audit": str(sources.pricing_audit),
            "lane_assessment": str(sources.lane_assessment),
            "recommendation_scorecard": str(sources.recommendation_scorecard),
        },
        "portfolio": {
            "cash_eur": portfolio_state.get("cash_eur"),
            "total_portfolio_value_eur": round(total_portfolio_value_eur, 2),
            "base_currency": "EUR",
        },
        "fx_basis": {
            "pair": fx_basis.get("pair", "EUR/USD"),
            "rate": _fx_rate(pricing_audit),
            "requested_date": fx_basis.get("requested_date"),
            "returned_date": fx_basis.get("returned_date"),
            "source": fx_basis.get("source"),
            "status": fx_basis.get("status"),
        },
        "positions": holdings,
        "pricing": prices,
        "lane_assessment": lane_assessment,
        "recommendation_scorecard": recommendation_scorecard,
        "replacement_duels": duel_candidates,
        "validation_flags": {
            "pricing_audit_valid": bool(pricing_audit.get("holdings")),
            "lane_assessment_present": bool(lane_assessment.get("assessed_lanes")),
            "scorecard_present": len(recommendation_scorecard) > 0,
            "fx_rate_present": _fx_rate(pricing_audit) is not None,
        },
    }

    return runtime_state


def main() -> None:
    runtime_state = build_runtime_state()
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    report_date = runtime_state.get("report_date", "unknown").replace("-", "")
    out_path = RUNTIME_DIR / f"etf_report_state_{report_date}.json"

    out_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

    print(
        f"ETF_RUNTIME_STATE_OK | report_date={runtime_state.get('report_date')} | output={out_path}"
    )


if __name__ == "__main__":
    main()
