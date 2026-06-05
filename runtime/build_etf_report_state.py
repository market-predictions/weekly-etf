from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

RUNTIME_DIR = Path("output/runtime")
PRICING_DIR = Path("output/pricing")
LANE_DIR = Path("output/lane_reviews")
MACRO_DIR = Path("output/macro")
PRICED_CLOSE_STATUSES = {"fresh_close", "fresh_fallback_source", "fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}

# Scorecard/report memory may enrich commentary, but it must never overwrite
# the official portfolio-state quantity/valuation contract.
POSITION_AUTHORITY_FIELDS = {
    "shares",
    "current_price_local",
    "previous_price_local",
    "continuity_current_price_local",
    "currency",
    "market_value_local",
    "previous_market_value_local",
    "market_value_eur",
    "previous_market_value_eur",
    "current_weight_pct",
    "previous_weight_pct",
    "weight_inherited_pct",
    "weight_pct",
    "target_weight_pct",
    "shares_delta_this_run",
    "weight_change_pct",
    "action_executed_this_run",
    "funding_source_note",
    "pricing_source",
    "pricing_status",
    "pricing_tier",
    "pricing_close_type",
    "price_date",
    "selected_close",
}


@dataclass
class RuntimeSources:
    portfolio_state: Path
    pricing_audit: Path
    lane_assessment: Path
    recommendation_scorecard: Path
    macro_policy_pack: Path | None = None
    rotation_plan: Path | None = None


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
    raise RuntimeError("No ETF lane artifact satisfies the runtime ETF contract; rejected: " + ", ".join(rejected))


def latest_macro_policy_pack() -> Path | None:
    latest = MACRO_DIR / "latest.json"
    if latest.exists():
        return latest
    files = sorted(MACRO_DIR.glob("etf_macro_policy_pack_*.json")) if MACRO_DIR.exists() else []
    return files[-1] if files else None


def latest_rotation_plan_file() -> Path | None:
    pointer = RUNTIME_DIR / "latest_etf_rotation_plan_path.txt"
    if pointer.exists():
        raw = pointer.read_text(encoding="utf-8").strip()
        if raw:
            path = Path(raw)
            if path.exists():
                return path
            candidate = RUNTIME_DIR / path.name
            if candidate.exists():
                return candidate
    files = sorted(RUNTIME_DIR.glob("etf_rotation_plan_*.json")) if RUNTIME_DIR.exists() else []
    return files[-1] if files else None


def _explicit_path(value: str | None, *, description: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.exists():
        raise RuntimeError(f"Explicit {description} does not exist: {path}")
    return path


def discover_sources(
    pricing_audit_path: str | None = None,
    lane_assessment_path: str | None = None,
    rotation_plan_path: str | None = None,
    disable_rotation_plan: bool = False,
) -> RuntimeSources:
    explicit_pricing = _explicit_path(
        pricing_audit_path or os.environ.get("ETF_PRICING_AUDIT_PATH") or os.environ.get("MRKT_RPRTS_PRICING_AUDIT_PATH"),
        description="ETF pricing audit path",
    )
    explicit_lane = _explicit_path(
        lane_assessment_path or os.environ.get("ETF_LANE_ARTIFACT_PATH") or os.environ.get("MRKT_RPRTS_LANE_ARTIFACT_PATH"),
        description="ETF lane artifact path",
    )
    if disable_rotation_plan:
        explicit_rotation = None
    else:
        explicit_rotation = _explicit_path(
            rotation_plan_path or os.environ.get("ETF_ROTATION_PLAN_PATH") or os.environ.get("MRKT_RPRTS_ROTATION_PLAN_PATH"),
            description="ETF rotation plan path",
        )
    return RuntimeSources(
        portfolio_state=Path("output/etf_portfolio_state.json"),
        pricing_audit=explicit_pricing or latest_file(PRICING_DIR, "price_audit_*.json"),
        lane_assessment=explicit_lane or latest_lane_file(LANE_DIR, "etf_lane_assessment_*.json"),
        recommendation_scorecard=Path("output/etf_recommendation_scorecard.csv"),
        macro_policy_pack=latest_macro_policy_pack(),
        rotation_plan=None if disable_rotation_plan else (explicit_rotation or latest_rotation_plan_file()),
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


def _selected_price(row: dict[str, Any]) -> float | None:
    selected = _to_float(row.get("selected_close"))
    if selected is not None:
        return selected
    return _to_float(row.get("price"))


def _index_by_ticker(rows: list[dict[str, Any]], ticker_key: str = "ticker") -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        ticker = _ticker(row.get(ticker_key))
        if ticker:
            indexed[ticker] = row
    return indexed


def _index_price_results(pricing_audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in pricing_audit.get("price_results", []) or pricing_audit.get("prices", []) or []:
        symbol = _ticker(row.get("symbol"))
        if symbol:
            indexed[symbol] = row
    return indexed


def _index_lanes_by_ticker(lane_assessment: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index live lane scores by ETF ticker without giving alternatives authority over primaries.

    Primary ETF lanes are the preferred score source. Alternative ETF lanes are only
    used when the ticker has no primary lane. This keeps score enrichment
    deterministic while avoiding a raw n/a score surface for active holdings.
    """
    primary: dict[str, dict[str, Any]] = {}
    alternative: dict[str, dict[str, Any]] = {}
    for lane in lane_assessment.get("assessed_lanes", []) or []:
        primary_ticker = _ticker(lane.get("primary_etf"))
        alternative_ticker = _ticker(lane.get("alternative_etf"))
        if primary_ticker and primary_ticker not in primary:
            primary[primary_ticker] = lane
        if alternative_ticker and alternative_ticker not in alternative:
            alternative[alternative_ticker] = lane
    indexed = dict(alternative)
    indexed.update(primary)
    return indexed


def _semantic_defaults(ticker: str) -> dict[str, Any]:
    defaults = {
        "SPY": {"suggested_action": "Hold under review", "conviction_tier": "Tier 2", "portfolio_role": "Core beta", "better_alternative_exists": "Yes", "short_reason": "Useful core beta, but overlap with SMH limits diversification value.", "required_next_action": "Review overlap versus SMH and compare with QUAL / IEFA.", "fresh_cash_test": "Smaller / under review"},
        "SMH": {"suggested_action": "Hold / preferred add candidate", "conviction_tier": "Tier 1", "portfolio_role": "Growth engine", "better_alternative_exists": "No", "short_reason": "Best earned position; add only if the 25% max-position rule leaves room.", "required_next_action": "Respect max-position discipline before any fresh add.", "fresh_cash_test": "Yes, but size-limited"},
        "PPA": {"suggested_action": "Hold under review", "conviction_tier": "Tier 3", "portfolio_role": "Resilience", "better_alternative_exists": "Yes", "short_reason": "Defense thesis remains valid, but ITA must be compared before new capital.", "required_next_action": "Complete PPA-versus-ITA replacement duel.", "fresh_cash_test": "No / reduce unless duel improves"},
        "PAVE": {"suggested_action": "Hold under review", "conviction_tier": "Tier 2", "portfolio_role": "Real-asset capex", "better_alternative_exists": "Yes", "short_reason": "Infrastructure thesis remains attractive, but GRID is the clean challenger.", "required_next_action": "Complete PAVE-versus-GRID implementation duel.", "fresh_cash_test": "Smaller / under review"},
        "URNM": {"suggested_action": "Hold", "conviction_tier": "Tier 2", "portfolio_role": "Strategic energy", "better_alternative_exists": "No", "short_reason": "Strategic nuclear exposure remains valid, but it is not the first use of fresh cash.", "required_next_action": "Hold unless relative strength confirms add status.", "fresh_cash_test": "Hold / wait for confirmation"},
        "GLD": {"suggested_action": "Hold under review", "conviction_tier": "Tier 3", "portfolio_role": "Hedge ballast", "better_alternative_exists": "Yes", "short_reason": "Hedge role is not automatic after drawdown; ballast behavior must be proven.", "required_next_action": "Run hedge-validity test versus GSG / BIL.", "fresh_cash_test": "No / hedge review"},
        "GSG": {"suggested_action": "Hold", "conviction_tier": "Tier 2", "portfolio_role": "Commodity inflation hedge", "better_alternative_exists": "No", "short_reason": "Added through guarded model rotation as commodity-breadth replacement for part of GLD.", "required_next_action": "Monitor commodity breadth and hedge contribution after execution.", "fresh_cash_test": "Hold / monitor"},
        "CIBR": {"suggested_action": "Hold", "conviction_tier": "Tier 2", "portfolio_role": "Cybersecurity resilience", "better_alternative_exists": "No", "short_reason": "Cybersecurity exposure remains structurally supported by AI, cloud and resilience spending.", "required_next_action": "Monitor relative strength and portfolio concentration.", "fresh_cash_test": "Hold / monitor", "total_score": "4.97", "score_source": "semantic_fallback_until_position_score"},
        "DFEN": {"suggested_action": "Hold under review", "conviction_tier": "Tier 3", "portfolio_role": "Defense tactical beta", "better_alternative_exists": "Yes", "short_reason": "Defense thesis remains relevant, but vehicle risk and implementation quality require review.", "required_next_action": "Review defense vehicle fit versus ITA/PPA and leverage constraints.", "fresh_cash_test": "No / under review", "total_score": "3.10", "score_source": "semantic_fallback_until_position_score"},
        "IEFA": {"suggested_action": "Hold", "conviction_tier": "Tier 3", "portfolio_role": "Non-U.S. developed diversification", "better_alternative_exists": "No", "short_reason": "Diversifies U.S. factor concentration but still needs relative-strength confirmation.", "required_next_action": "Monitor non-U.S. breadth and SPY-relative performance.", "fresh_cash_test": "Hold / monitor", "total_score": "3.52", "score_source": "semantic_fallback_until_position_score"},
        "XLU": {"suggested_action": "Hold under review", "conviction_tier": "Tier 3", "portfolio_role": "Defensive utilities ballast", "better_alternative_exists": "Yes", "short_reason": "Defensive utility exposure must justify its role versus cash and broader ballast alternatives.", "required_next_action": "Review defensive ballast role versus BIL/SHV and opportunity cost.", "fresh_cash_test": "No / under review", "total_score": "3.00", "score_source": "semantic_fallback_until_position_score"},
    }
    return defaults.get(ticker, {})


def _revalue_holding_from_price(holding: dict[str, Any], price_row: dict[str, Any] | None, pricing_audit: dict[str, Any]) -> dict[str, Any]:
    ticker = _ticker(holding.get("ticker"))
    if not ticker or not price_row:
        return holding
    price = _selected_price(price_row)
    if price is None:
        return holding
    status = str(price_row.get("status") or "")
    if status not in PRICED_CLOSE_STATUSES:
        return holding

    shares = _to_float(holding.get("shares"))
    if shares is None:
        return holding
    currency = str(price_row.get("currency") or holding.get("currency") or "USD")
    market_value_local = round(shares * price, 2)
    fx = _fx_rate(pricing_audit)
    if currency.upper() == "EUR":
        market_value_eur = market_value_local
    elif fx:
        market_value_eur = round(market_value_local / fx, 2)
    else:
        market_value_eur = _to_float(holding.get("previous_market_value_eur"))
    holding = dict(holding)
    holding.update(
        {
            "previous_price_local": price,
            "current_price_local": price,
            "previous_market_value_local": market_value_local,
            "previous_market_value_eur": market_value_eur,
            "market_value_local": market_value_local,
            "market_value_eur": market_value_eur,
            "currency": currency,
            "pricing_source": price_row.get("source"),
            "pricing_status": status,
            "pricing_tier": price_row.get("pricing_tier"),
            "pricing_close_type": price_row.get("selected_close_type"),
            "price_date": price_row.get("returned_close_date"),
            "selected_close": price,
        }
    )
    return holding


def _apply_lane_score_if_missing(row: dict[str, Any], lane_by_ticker: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ticker = _ticker(row.get("ticker"))
    if _to_float(row.get("total_score")) is not None:
        row.setdefault("score_source", "position_scorecard_or_semantic_default")
        return row
    lane = lane_by_ticker.get(ticker, {})
    lane_score = _to_float(lane.get("total_score"))
    if lane_score is None:
        return row
    row["total_score"] = f"{lane_score:.2f}"
    row["score_source"] = "lane_assessment_primary_or_alternative"
    row.setdefault("conviction_tier", "Tier 2" if lane_score >= 3.5 else "Tier 3")
    row.setdefault("short_reason", lane.get("evidence_summary") or lane.get("why_now") or "Live lane score supplied by lane assessment.")
    row.setdefault("required_next_action", lane.get("why_now") or "Monitor live lane score and position fit next run.")
    row.setdefault("fresh_cash_test", "Hold / monitor")
    return row


def _enrich_positions(
    portfolio_state: dict[str, Any],
    pricing_audit: dict[str, Any],
    scorecard: list[dict[str, str]],
    lane_assessment: dict[str, Any],
    rotation_plan: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    price_results = _index_price_results(pricing_audit)
    score_by_ticker = _index_by_ticker(scorecard)
    lane_by_ticker = _index_lanes_by_ticker(lane_assessment)
    rotation_by_ticker = {str(r.get("ticker", "")).upper(): r for r in (rotation_plan or {}).get("rotation_decisions", []) or []}
    target_by_ticker = {str(r.get("ticker", "")).upper(): r for r in (rotation_plan or {}).get("target_weights", []) or []}
    holdings = []
    total_value = 0.0
    for raw in portfolio_state.get("positions", []):
        ticker = _ticker(raw.get("ticker"))
        if not ticker:
            continue
        row = dict(_semantic_defaults(ticker))
        row.update(raw)
        row = _revalue_holding_from_price(row, price_results.get(ticker), pricing_audit)
        score = score_by_ticker.get(ticker, {})
        if score:
            row.update({k: v for k, v in score.items() if k not in POSITION_AUTHORITY_FIELDS and v not in (None, "")})
            if _to_float(row.get("total_score")) is not None:
                row["score_source"] = "position_scorecard"
        row = _apply_lane_score_if_missing(row, lane_by_ticker)
        rotation = rotation_by_ticker.get(ticker, {})
        if rotation:
            row.update(
                {
                    "rotation_action_code": rotation.get("action_code"),
                    "suggested_action": rotation.get("action_label") or rotation.get("action_code") or row.get("suggested_action"),
                    "rotation_release_score": rotation.get("release_score"),
                    "rotation_destination_ticker": rotation.get("destination_ticker"),
                    "rotation_override_status": rotation.get("override_status"),
                    "rotation_override_reason_code": rotation.get("override_reason_code"),
                    "rotation_reason_codes": rotation.get("reason_codes"),
                }
            )
        target = target_by_ticker.get(ticker, {})
        if target:
            row["target_weight_pct"] = target.get("target_weight_pct")
        mv = _to_float(row.get("previous_market_value_eur")) or 0.0
        total_value += mv
        holdings.append(row)
    cash = _to_float(portfolio_state.get("cash_eur")) or 0.0
    nav = total_value + cash
    for row in holdings:
        mv = _to_float(row.get("previous_market_value_eur")) or 0.0
        row["current_weight_pct"] = round(mv / nav * 100.0, 2) if nav else 0.0
        row.setdefault("previous_weight_pct", row["current_weight_pct"])
        row.setdefault("weight_inherited_pct", row["current_weight_pct"])
        row.setdefault("target_weight_pct", row["current_weight_pct"])
    return holdings


def _build_replacement_duels(portfolio_state: dict[str, Any], lane_assessment: dict[str, Any], pricing_audit: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = lane_assessment.get("assessed_lanes", []) or []
    return [lane for lane in lanes if lane.get("challenger") is True][:12]


def build_runtime_state(
    pricing_audit_path: str | None = None,
    lane_assessment_path: str | None = None,
    rotation_plan_path: str | None = None,
    disable_rotation_plan: bool = False,
) -> dict[str, Any]:
    sources = discover_sources(pricing_audit_path, lane_assessment_path, rotation_plan_path, disable_rotation_plan=disable_rotation_plan)
    portfolio_state = load_json(sources.portfolio_state)
    pricing_audit = load_json(sources.pricing_audit)
    lane_assessment = load_json(sources.lane_assessment)
    recommendation_scorecard = load_scorecard(sources.recommendation_scorecard)
    macro_policy_pack = load_json_if_exists(sources.macro_policy_pack)
    rotation_plan = load_json_if_exists(sources.rotation_plan) if sources.rotation_plan else {}

    holdings = _enrich_positions(portfolio_state, pricing_audit, recommendation_scorecard, lane_assessment, rotation_plan)
    total_market_value = round(sum((_to_float(p.get("previous_market_value_eur")) or 0.0) for p in holdings), 2)
    total_portfolio_value_eur = round(total_market_value + (_to_float(portfolio_state.get("cash_eur")) or 0.0), 2)
    prices = list(_index_price_results(pricing_audit).values())
    fx_basis = pricing_audit.get("fx_basis") or {}
    duel_candidates = _build_replacement_duels(portfolio_state, lane_assessment, pricing_audit)

    resolved_report_date = lane_assessment.get("report_date") or pricing_audit.get("requested_close_date") or datetime.utcnow().strftime("%Y-%m-%d")
    validation_flags = {
        "pricing_audit_valid": bool(pricing_audit.get("holdings")),
        "pricing_revalued_from_price_results": True,
        "pricing_status_semantics": "exact_or_prior_v1",
        "lane_assessment_present": bool(lane_assessment.get("assessed_lanes")),
        "lane_assessment_source": str(sources.lane_assessment),
        "lane_assessment_has_primary_etfs": _lane_artifact_has_etf_contract(lane_assessment),
        "macro_policy_pack_present": bool(macro_policy_pack.get("regime")),
        "scorecard_present": len(recommendation_scorecard) > 0,
        "scorecard_authority_limited_to_commentary": True,
        "lane_score_fallback_enabled": True,
        "semantic_score_fallback_enabled": True,
        "positions_enriched": any(p.get("short_reason") for p in holdings),
        "positions_without_total_score": [p.get("ticker") for p in holdings if _to_float(p.get("total_score")) is None],
        "fx_rate_present": _fx_rate(pricing_audit) is not None,
        "rotation_plan_present": bool(rotation_plan),
        "rotation_plan_source": str(sources.rotation_plan) if sources.rotation_plan else None,
        "rotation_warning_mode": bool(rotation_plan),
    }

    return {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "run_id": pricing_audit.get("run_id") or os.environ.get("ETF_PRICING_RUN_ID") or os.environ.get("MRKT_RPRTS_RUN_ID"),
        "report_date": resolved_report_date,
        "requested_close_date": pricing_audit.get("requested_close_date"),
        "source_files": {
            "portfolio_state": str(sources.portfolio_state),
            "pricing_audit": str(sources.pricing_audit),
            "lane_assessment": str(sources.lane_assessment),
            "recommendation_scorecard": str(sources.recommendation_scorecard),
            "macro_policy_pack": str(sources.macro_policy_pack) if sources.macro_policy_pack else None,
            "rotation_plan": str(sources.rotation_plan) if sources.rotation_plan else None,
        },
        "portfolio": {"cash_eur": portfolio_state.get("cash_eur"), "total_portfolio_value_eur": round(total_portfolio_value_eur, 2), "base_currency": "EUR"},
        "fx_basis": {"pair": fx_basis.get("pair", "EUR/USD"), "rate": _fx_rate(pricing_audit), "requested_date": fx_basis.get("requested_date"), "returned_date": fx_basis.get("returned_date"), "source": fx_basis.get("source"), "status": fx_basis.get("status")},
        "positions": holdings,
        "pricing": prices,
        "lane_assessment": lane_assessment,
        "macro_policy_pack": macro_policy_pack,
        "recommendation_scorecard": recommendation_scorecard,
        "replacement_duels": duel_candidates,
        "rotation_plan": rotation_plan,
        "rotation_decisions": rotation_plan.get("rotation_decisions", []) if rotation_plan else [],
        "target_weights": rotation_plan.get("target_weights", []) if rotation_plan else [],
        "trade_intents": rotation_plan.get("trade_intents", []) if rotation_plan else [],
        "validation_flags": validation_flags,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--lane-artifact", default=None)
    parser.add_argument("--rotation-plan", default=None)
    parser.add_argument("--no-rotation-plan", action="store_true")
    parser.add_argument("--output-path", default=None)
    args = parser.parse_args()

    runtime_state = build_runtime_state(
        pricing_audit_path=args.pricing_audit,
        lane_assessment_path=args.lane_artifact,
        rotation_plan_path=args.rotation_plan,
        disable_rotation_plan=args.no_rotation_plan,
    )
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    report_date = str(runtime_state.get("report_date") or "unknown").replace("-", "")
    run_id = str(runtime_state.get("run_id") or "").strip()
    if args.output_path:
        out_path = Path(args.output_path)
    elif run_id:
        suffix = "_executed" if args.no_rotation_plan else ""
        out_path = RUNTIME_DIR / f"etf_report_state_{report_date}_{run_id}{suffix}.json"
    else:
        out_path = RUNTIME_DIR / f"etf_report_state_{report_date}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")
    (RUNTIME_DIR / "latest_etf_report_state_path.txt").write_text(str(out_path) + "\n", encoding="utf-8")
    print(
        f"ETF_RUNTIME_STATE_OK | report_date={runtime_state.get('report_date')} | "
        f"run_id={runtime_state.get('run_id')} | output={out_path} | "
        f"pricing={runtime_state.get('source_files', {}).get('pricing_audit')} | "
        f"lane_source={runtime_state.get('source_files', {}).get('lane_assessment')} | "
        f"macro_source={runtime_state.get('source_files', {}).get('macro_policy_pack')} | "
        f"rotation_plan={runtime_state.get('source_files', {}).get('rotation_plan') or 'none'} | "
        f"rotation_warning_mode={runtime_state.get('validation_flags', {}).get('rotation_warning_mode')}"
    )


if __name__ == "__main__":
    main()
