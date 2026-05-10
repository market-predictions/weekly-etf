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
MACRO_DIR = Path("output/macro")


@dataclass
class RuntimeSources:
    portfolio_state: Path
    pricing_audit: Path
    lane_assessment: Path
    recommendation_scorecard: Path
    macro_policy_pack: Path | None = None


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return load_json(path)


def load_scorecard(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
    return rows


def _clean_symbol(value: Any) -> str:
    raw = str(value or "").strip().upper()
    if raw in {"", "NONE", "NAN", "NULL", "N/A", "-"}:
        return ""
    return raw


def _lane_artifact_has_etf_contract(payload: dict[str, Any]) -> bool:
    lanes = payload.get("assessed_lanes", []) or []
    if not lanes:
        return False
    for lane in lanes:
        if not _clean_symbol(lane.get("primary_etf")):
            return False
    return True


def latest_lane_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern), reverse=True)
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    rejected: list[str] = []
    for path in files:
        try:
            payload = load_json(path)
        except Exception:
            rejected.append(path.name)
            continue
        if _lane_artifact_has_etf_contract(payload):
            return path
        rejected.append(path.name)
    raise RuntimeError(
        "No ETF lane artifact satisfies the runtime ETF contract; rejected: "
        + ", ".join(rejected)
    )


def latest_macro_policy_pack() -> Path | None:
    latest = MACRO_DIR / "latest.json"
    if latest.exists():
        return latest
    files = sorted(MACRO_DIR.glob("etf_macro_policy_pack_*.json")) if MACRO_DIR.exists() else []
    return files[-1] if files else None


def discover_sources() -> RuntimeSources:
    return RuntimeSources(
        portfolio_state=Path("output/etf_portfolio_state.json"),
        pricing_audit=latest_file(PRICING_DIR, "price_audit_*.json"),
        lane_assessment=latest_lane_file(LANE_DIR, "etf_lane_assessment_*.json"),
        recommendation_scorecard=Path("output/etf_recommendation_scorecard.csv"),
        macro_policy_pack=latest_macro_policy_pack(),
    )


def _fx_rate(pricing_audit: dict[str, Any]) -> float | None:
    fx_basis = pricing_audit.get("fx_basis") or {}
    raw = fx_basis.get("rate")
    try:
        return None if raw is None else float(raw)
    except (TypeError, ValueError):
        return None


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _index_by_ticker(rows: list[dict[str, Any]], ticker_key: str = "ticker") -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        ticker = _ticker(row.get(ticker_key))
        if ticker:
            indexed[ticker] = row
    return indexed


def _semantic_defaults(ticker: str) -> dict[str, Any]:
    defaults = {
        "SPY": {
            "suggested_action": "Hold under review",
            "conviction_tier": "Tier 2",
            "portfolio_role": "Core beta",
            "better_alternative_exists": "Yes",
            "short_reason": "Useful core beta, but overlap with SMH limits diversification value.",
            "required_next_action": "Review overlap versus SMH and compare with QUAL / IEFA.",
            "fresh_cash_test": "Smaller / under review",
        },
        "SMH": {
            "suggested_action": "Hold / preferred add candidate",
            "conviction_tier": "Tier 1",
            "portfolio_role": "Growth engine",
            "better_alternative_exists": "No",
            "short_reason": "Best earned position; add only if the 25% max-position rule leaves room.",
            "required_next_action": "Respect max-position discipline before any fresh add.",
            "fresh_cash_test": "Yes, but size-limited",
        },
        "PPA": {
            "suggested_action": "Hold under review",
            "conviction_tier": "Tier 3",
            "portfolio_role": "Resilience",
            "better_alternative_exists": "Yes",
            "short_reason": "Defense thesis remains valid, but ITA must be compared before new capital.",
            "required_next_action": "Complete PPA-versus-ITA replacement duel.",
            "fresh_cash_test": "No / reduce unless duel improves",
        },
        "PAVE": {
            "suggested_action": "Hold under review",
            "conviction_tier": "Tier 2",
            "portfolio_role": "Real-asset capex",
            "better_alternative_exists": "Yes",
            "short_reason": "Infrastructure thesis remains attractive, but GRID is the clean challenger.",
            "required_next_action": "Complete PAVE-versus-GRID implementation duel.",
            "fresh_cash_test": "Smaller / under review",
        },
        "URNM": {
            "suggested_action": "Hold",
            "conviction_tier": "Tier 2",
            "portfolio_role": "Strategic energy",
            "better_alternative_exists": "No",
            "short_reason": "Strategic nuclear exposure remains valid, but it is not the first use of fresh cash.",
            "required_next_action": "Hold unless relative strength confirms add status.",
            "fresh_cash_test": "Hold / wait for confirmation",
        },
        "GLD": {
            "suggested_action": "Hold under review",
            "conviction_tier": "Tier 3",
            "portfolio_role": "Hedge ballast",
            "better_alternative_exists": "Yes",
            "short_reason": "Hedge role is not automatic after drawdown; ballast behavior must be proven.",
            "required_next_action": "Run hedge-validity test versus GSG / BIL.",
            "fresh_cash_test": "No / hedge review",
        },
    }
    return defaults.get(ticker, {})


def enrich_positions(
    pricing_holdings: list[dict[str, Any]],
    portfolio_state: dict[str, Any],
    recommendation_scorecard: list[dict[str, str]],
) -> list[dict[str, Any]]:
    state_by_ticker = _index_by_ticker(portfolio_state.get("positions", []) or [])
    score_by_ticker = _index_by_ticker(recommendation_scorecard)

    enriched: list[dict[str, Any]] = []
    for holding in pricing_holdings:
        ticker = _ticker(holding.get("ticker"))
        if not ticker:
            continue
        merged: dict[str, Any] = {}
        merged.update(_semantic_defaults(ticker))
        merged.update(state_by_ticker.get(ticker, {}))
        merged.update(score_by_ticker.get(ticker, {}))
        merged.update(holding)
        merged["ticker"] = ticker

        merged["current_price_local"] = _to_float(holding.get("previous_price_local")) or _to_float(merged.get("current_price_local"))
        merged["market_value_local"] = _to_float(holding.get("previous_market_value_local")) or _to_float(merged.get("market_value_local"))
        merged["market_value_eur"] = _to_float(holding.get("previous_market_value_eur")) or _to_float(merged.get("market_value_eur"))
        merged["current_weight_pct"] = _to_float(holding.get("previous_weight_pct")) or _to_float(merged.get("current_weight_pct"))
        merged["continuity_current_price_local"] = merged.get("current_price_local")

        merged["previous_price_local"] = merged.get("current_price_local")
        merged["previous_market_value_local"] = merged.get("market_value_local")
        merged["previous_market_value_eur"] = merged.get("market_value_eur")
        merged["previous_weight_pct"] = _to_float(merged.get("current_weight_pct")) or _to_float(merged.get("previous_weight_pct"))

        for key in (
            "shares",
            "total_score",
            "thesis_score",
            "implementation_score",
            "pnl_pct",
            "avg_entry_local",
            "shares_delta_this_run",
            "weight_change_pct",
            "target_weight_pct",
            "weight_inherited_pct",
        ):
            numeric = _to_float(merged.get(key))
            if numeric is not None:
                merged[key] = numeric

        enriched.append(merged)

    return enriched


def build_runtime_state() -> dict[str, Any]:
    sources = discover_sources()

    portfolio_state = load_json(sources.portfolio_state)
    pricing_audit = load_json(sources.pricing_audit)
    lane_assessment = load_json(sources.lane_assessment)
    recommendation_scorecard = load_scorecard(sources.recommendation_scorecard)
    macro_policy_pack = load_json_if_exists(sources.macro_policy_pack)

    pricing_holdings = pricing_audit.get("holdings", [])
    holdings = enrich_positions(pricing_holdings, portfolio_state, recommendation_scorecard)
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

    resolved_report_date = (
        lane_assessment.get("report_date")
        or pricing_audit.get("requested_close_date")
        or datetime.utcnow().strftime("%Y-%m-%d")
    )

    runtime_state = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "report_date": resolved_report_date,
        "requested_close_date": pricing_audit.get("requested_close_date"),
        "source_files": {
            "portfolio_state": str(sources.portfolio_state),
            "pricing_audit": str(sources.pricing_audit),
            "lane_assessment": str(sources.lane_assessment),
            "recommendation_scorecard": str(sources.recommendation_scorecard),
            "macro_policy_pack": str(sources.macro_policy_pack) if sources.macro_policy_pack else None,
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
        "macro_policy_pack": macro_policy_pack,
        "recommendation_scorecard": recommendation_scorecard,
        "replacement_duels": duel_candidates,
        "validation_flags": {
            "pricing_audit_valid": bool(pricing_audit.get("holdings")),
            "lane_assessment_present": bool(lane_assessment.get("assessed_lanes")),
            "lane_assessment_source": str(sources.lane_assessment),
            "lane_assessment_has_primary_etfs": _lane_artifact_has_etf_contract(lane_assessment),
            "macro_policy_pack_present": bool(macro_policy_pack.get("regime")),
            "scorecard_present": len(recommendation_scorecard) > 0,
            "positions_enriched": any(p.get("short_reason") for p in holdings),
            "fx_rate_present": _fx_rate(pricing_audit) is not None,
        },
    }

    return runtime_state


def main() -> None:
    runtime_state = build_runtime_state()
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    report_date = str(runtime_state.get("report_date") or "unknown").replace("-", "")
    out_path = RUNTIME_DIR / f"etf_report_state_{report_date}.json"

    out_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

    print(
        f"ETF_RUNTIME_STATE_OK | report_date={runtime_state.get('report_date')} | output={out_path} | lane_source={runtime_state.get('source_files', {}).get('lane_assessment')} | macro_source={runtime_state.get('source_files', {}).get('macro_policy_pack')}"
    )


if __name__ == "__main__":
    main()
