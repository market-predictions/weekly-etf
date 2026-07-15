from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.rotation_state_authority import (
    PRICED_VALUATION_STATUSES,
    build_current_run_valuation_state,
    refresh_scorecard_rows,
    validate_current_run_authority,
    write_scorecard,
)

OUTPUT_RUNTIME_DIR = Path("output/runtime")
DEFAULT_PORTFOLIO_STATE = Path("output/etf_portfolio_state.json")
DEFAULT_SCORECARD = Path("output/etf_recommendation_scorecard.csv")
DEFAULT_LANE_DIR = Path("output/lane_reviews")
DEFAULT_PRICING_DIR = Path("output/pricing")
DEFAULT_RS = Path("output/market_history/etf_relative_strength.json")

VALUATION_GRADE = "valuation_grade"

POLICY = {
    "min_trade_size_pct_nav": 2.00,
    "max_single_source_reduction_pct_nav": 5.00,
    "max_major_rotations_per_run": 1,
    "review_age_watch": 1,
    "review_age_forced_decision": 2,
    "review_age_block_passive_hold": 3,
    "release_score_reduce_threshold": 65,
    "release_score_replace_threshold": 80,
    "release_score_close_threshold": 90,
    "destination_score_min_fundable": 70,
    "destination_score_preferred": 80,
    "relative_strength_3m_watch": 5,
    "relative_strength_3m_rotation_candidate": 10,
    "relative_strength_3m_strong": 15,
}


@dataclass
class Sources:
    portfolio_state: Path
    scorecard: Path
    pricing_audit: Path
    lane_assessment: Path
    relative_strength: Path | None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _latest(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _index(rows: list[dict[str, Any]], key: str = "ticker") -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = _ticker(row.get(key))
        if symbol:
            out[symbol] = row
    return out


def _discover_sources(args: argparse.Namespace) -> Sources:
    pricing = (
        Path(args.pricing_audit)
        if args.pricing_audit
        else _latest(DEFAULT_PRICING_DIR, "price_audit_*.json")
    )
    lane = (
        Path(args.lane_artifact)
        if args.lane_artifact
        else _latest(DEFAULT_LANE_DIR, "etf_lane_assessment_*.json")
    )
    rs = (
        Path(args.relative_strength)
        if args.relative_strength
        else (DEFAULT_RS if DEFAULT_RS.exists() else None)
    )
    return Sources(
        portfolio_state=Path(args.portfolio_state),
        scorecard=Path(args.scorecard),
        pricing_audit=pricing,
        lane_assessment=lane,
        relative_strength=rs,
    )


def role_validity(
    position: dict[str, Any], scorecard_row: dict[str, Any] | None
) -> str:
    row = scorecard_row or {}
    pnl = _num(
        position.get("pnl_pct")
        if position.get("pnl_pct") not in (None, "")
        else row.get("pnl_pct"),
        0.0,
    )
    implementation = _num(
        row.get("implementation_score") or position.get("implementation_score"),
        3.0,
    )
    hedge_status = str(
        row.get("hedge_validity_status")
        or position.get("hedge_validity_status")
        or ""
    ).lower()
    flags = str(
        row.get("discipline_flags")
        or position.get("discipline_flags")
        or ""
    ).lower()
    fresh_cash = str(
        row.get("fresh_cash_test") or position.get("fresh_cash_test") or ""
    ).lower()
    replaceable = str(
        row.get("replaceable_status")
        or position.get("replaceable_status")
        or ""
    ).lower()

    fail_conditions = [
        implementation < 2.5,
        pnl <= -15.0,
        "fail" in hedge_status,
        "close" in fresh_cash,
    ]
    impaired_conditions = [
        implementation < 3.25,
        pnl <= -7.5,
        "review" in hedge_status,
        "replaceable" in flags,
        "review" in replaceable,
        "reduce" in fresh_cash,
        "no" in fresh_cash,
    ]
    if any(fail_conditions):
        return "fail"
    if any(impaired_conditions):
        return "impaired"
    return "pass"


def capital_release_score(
    position: dict[str, Any], scorecard_row: dict[str, Any] | None
) -> tuple[int, list[str], str]:
    row = scorecard_row or {}
    score = 0
    reasons: list[str] = []
    fresh_cash = str(
        row.get("fresh_cash_test") or position.get("fresh_cash_test") or ""
    ).lower()
    replaceable = str(
        row.get("replaceable_status")
        or position.get("replaceable_status")
        or ""
    ).lower()
    weeks = int(
        _num(row.get("weeks_replaceable") or position.get("weeks_replaceable"), 0.0)
    )
    pnl = _num(
        position.get("pnl_pct")
        if position.get("pnl_pct") not in (None, "")
        else row.get("pnl_pct"),
        0.0,
    )
    total_score = _num(
        position.get("total_score") or row.get("total_score"), 0.0
    )
    better = str(
        position.get("better_alternative_exists")
        or row.get("better_alternative_exists")
        or ""
    ).lower()
    contribution = str(
        row.get("contribution_quality")
        or position.get("contribution_quality")
        or ""
    ).lower()
    factor = str(
        row.get("factor_overlap_flag")
        or position.get("factor_overlap_flag")
        or ""
    ).strip()
    role = role_validity(position, row)

    if "reduce" in fresh_cash or "no" in fresh_cash:
        score += 25
        reasons.append("failed_fresh_cash_test")
    elif "smaller" in fresh_cash or "review" in fresh_cash:
        score += 12
        reasons.append("fresh_cash_smaller_or_review")
    if replaceable and replaceable not in {"none", "0"}:
        score += 20
        reasons.append("replaceable_status")
    if weeks >= 2:
        score += 10
        reasons.append("review_age_ge_2")
    if weeks >= 3:
        score += 10
        reasons.append("review_age_ge_3")
    if pnl < -5:
        score += 10
        reasons.append("negative_pnl_gt_5")
    if pnl < -10:
        score += 15
        reasons.append("negative_pnl_gt_10")
    if pnl <= -20:
        score += 15
        reasons.append("negative_pnl_gt_20")
    if pnl < -10 and 0 < total_score < 4.0:
        score += 20
        reasons.append("loss_and_sub4_forced_reunderwrite")
    if better == "yes":
        score += 15
        reasons.append("better_alternative_exists")
    if "negative" in contribution or "drag" in contribution:
        score += 10
        reasons.append("negative_contribution")
    if role == "impaired":
        score += 10
        reasons.append("role_impaired")
    if role == "fail":
        score += 20
        reasons.append("role_failed")
    if factor:
        score += 8
        reasons.append("factor_or_concentration_flag")

    return min(score, 100), reasons, role


def _rs_score(metrics: dict[str, Any]) -> float:
    if not metrics:
        return 0.0
    r1 = _num(metrics.get("return_1m_pct"), 0.0)
    r3 = _num(metrics.get("return_3m_pct"), 0.0)
    trend = _num(metrics.get("trend_quality"), 0.0)
    rs1 = _num(metrics.get("rs_vs_spy_1m_pct"), 0.0)
    rs3 = _num(metrics.get("rs_vs_spy_3m_pct"), 0.0)
    dd = _num(metrics.get("max_drawdown_3m_pct"), 0.0)
    vol = _num(metrics.get("volatility_3m_pct"), 0.0)
    score = 0.0
    score += max(min(r1 / 10.0, 1.0), -1.0) * 0.35
    score += max(min(r3 / 20.0, 1.0), -1.0) * 0.45
    score += (trend / 5.0) * 0.55
    score += max(min(rs1 / 8.0, 1.0), -1.0) * 0.25
    score += max(min(rs3 / 12.0, 1.0), -1.0) * 0.30
    if dd < -18:
        score -= 0.20
    elif dd > -8:
        score += 0.08
    if vol > 35:
        score -= 0.12
    elif 0 < vol < 20:
        score += 0.05
    return round(max(min(score, 1.25), -0.75), 2)


def _direct_edges(
    candidate: str, holding: str, metrics: dict[str, dict[str, Any]]
) -> tuple[float, float]:
    candidate_metrics = metrics.get(candidate, {})
    holding_metrics = metrics.get(holding, {})
    if not candidate_metrics or not holding_metrics:
        return 0.0, 0.0
    edge_1m = _num(candidate_metrics.get("return_1m_pct"), 0.0) - _num(
        holding_metrics.get("return_1m_pct"), 0.0
    )
    edge_3m = _num(candidate_metrics.get("return_3m_pct"), 0.0) - _num(
        holding_metrics.get("return_3m_pct"), 0.0
    )
    return round(edge_1m, 2), round(edge_3m, 2)


def _candidate_price_ok(candidate: dict[str, Any]) -> bool:
    return (
        str(candidate.get("price_status") or "")
        in PRICED_VALUATION_STATUSES
        and str(candidate.get("pricing_tier") or "") == VALUATION_GRADE
    )


def candidate_score(candidate: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    total = _num(candidate.get("total_score"), 0.0)
    if _candidate_price_ok(candidate):
        score += 20
        reasons.append("valuation_grade_pricing")
    if bool(candidate.get("is_fundable_candidate")):
        score += 20
        reasons.append("fundable_candidate")
    if bool(candidate.get("promoted_to_live_radar")):
        score += 10
        reasons.append("live_radar")
    scaled = max(0, min(50, int(round(total * 8.75))))
    score += scaled
    reasons.append("structural_score_scaled")
    rs = _num(candidate.get("relative_strength_score"), 0.0)
    if rs > 0:
        score += min(15, int(round(rs * 8)))
        reasons.append("positive_relative_strength")
    if str(candidate.get("tradability_status") or "").lower() == "pass":
        score += 10
        reasons.append("liquidity_pass")
    if _num(candidate.get("portfolio_differentiation"), 0.0) >= 4:
        score += 10
        reasons.append("portfolio_differentiation")
    direct3 = _num(candidate.get("direct_rs_vs_holding_3m_pct"), 0.0)
    if direct3 > POLICY["relative_strength_3m_watch"]:
        score += 5
        reasons.append("direct_3m_edge_watch")
    if direct3 >= POLICY["relative_strength_3m_rotation_candidate"]:
        score += 10
        reasons.append("direct_3m_edge_rotation")
    if direct3 > POLICY["relative_strength_3m_strong"]:
        score += 10
        reasons.append("direct_3m_edge_strong")
    return min(score, 100), reasons


def _candidate_view(
    lane: dict[str, Any],
    symbol: str,
    candidate_role: str,
    rs_metrics: dict[str, dict[str, Any]],
    existing_tickers: set[str],
) -> dict[str, Any]:
    primary = _ticker(lane.get("primary_etf"))
    alternative = _ticker(lane.get("alternative_etf"))
    metrics = dict(rs_metrics.get(symbol, {}) or {})

    if candidate_role == "primary":
        price_status = lane.get("primary_price_status")
        pricing_tier = lane.get("primary_pricing_tier")
        pricing_source = lane.get("primary_pricing_source")
        direct_target = _ticker(lane.get("direct_rs_vs_holding"))
    else:
        price_status = lane.get("alternative_price_status")
        pricing_tier = lane.get("alternative_pricing_tier")
        pricing_source = lane.get("alternative_pricing_source")
        direct_target = (
            primary
            if primary in existing_tickers
            else _ticker(lane.get("direct_rs_vs_holding"))
        )

    edge_1m, edge_3m = (
        _direct_edges(symbol, direct_target, rs_metrics)
        if direct_target
        else (0.0, 0.0)
    )
    priced = (
        str(price_status or "") in PRICED_VALUATION_STATUSES
        and str(pricing_tier or "") == VALUATION_GRADE
    )
    general_fundable = bool(lane.get("is_fundable_candidate"))
    replacement_fundable = bool(direct_target) and priced
    is_fundable = priced and (general_fundable or replacement_fundable)

    return {
        "candidate": symbol,
        "candidate_role": candidate_role,
        "paired_primary_etf": primary,
        "paired_alternative_etf": alternative,
        "lane_name": lane.get("lane_name"),
        "total_score": lane.get("total_score"),
        "portfolio_differentiation": lane.get("portfolio_differentiation"),
        "promoted_to_live_radar": bool(lane.get("promoted_to_live_radar")),
        "is_fundable_candidate": is_fundable,
        "funding_scope": (
            "general"
            if general_fundable
            else ("replacement_only" if replacement_fundable else "not_fundable")
        ),
        "direct_rs_vs_holding": direct_target,
        "direct_rs_vs_holding_1m_pct": edge_1m,
        "direct_rs_vs_holding_3m_pct": edge_3m,
        "pricing_tier": pricing_tier,
        "price_status": price_status,
        "pricing_source": pricing_source,
        "relative_strength_score": _rs_score(metrics),
        "return_1m_pct": metrics.get("return_1m_pct"),
        "return_3m_pct": metrics.get("return_3m_pct"),
        "tradability_status": metrics.get("tradability_status"),
        "avg_dollar_volume_3m": metrics.get("avg_dollar_volume_3m"),
    }


def incumbent_reviews(
    positions: list[dict[str, Any]],
    scorecard_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    reviews = []
    for position in positions:
        symbol = _ticker(position.get("ticker"))
        if not symbol:
            continue
        row = scorecard_rows.get(symbol)
        release, reasons, role = capital_release_score(position, row)
        weeks = int(
            _num(
                (row or {}).get("weeks_replaceable")
                or position.get("weeks_replaceable"),
                0.0,
            )
        )
        reviews.append(
            {
                "ticker": symbol,
                "current_weight_pct": round(
                    _num(
                        position.get("current_weight_pct")
                        or position.get("previous_weight_pct")
                    ),
                    2,
                ),
                "current_price_local": _num(
                    position.get("current_price_local"), 0.0
                ),
                "pnl_pct": _num(position.get("pnl_pct"), 0.0),
                "release_score": release,
                "release_reasons": reasons,
                "role_validity": role,
                "weeks_replaceable": weeks,
                "suggested_action_in": str(
                    position.get("suggested_action")
                    or (row or {}).get("suggested_action")
                    or ""
                ),
                "fresh_cash_test": str(
                    (row or {}).get("fresh_cash_test")
                    or position.get("fresh_cash_test")
                    or ""
                ),
            }
        )
    return reviews


def candidate_reviews(
    lanes: list[dict[str, Any]],
    rs_metrics: dict[str, dict[str, Any]],
    existing_tickers: set[str],
) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for lane in lanes:
        primary = _ticker(lane.get("primary_etf"))
        alternative = _ticker(lane.get("alternative_etf"))
        for symbol, role in ((primary, "primary"), (alternative, "alternative")):
            key = (symbol, str(lane.get("lane_name")))
            if not symbol or key in seen:
                continue
            seen.add(key)
            candidate = _candidate_view(
                lane, symbol, role, rs_metrics, existing_tickers
            )
            score, reasons = candidate_score(candidate)
            candidate["destination_score"] = score
            candidate["destination_reasons"] = reasons
            reviews.append(candidate)
    return sorted(
        reviews,
        key=lambda row: (
            -row["destination_score"],
            row["candidate_role"],
            row["candidate"],
        ),
    )


def _choose_destination(
    source: dict[str, Any],
    candidates: list[dict[str, Any]],
    existing_tickers: set[str],
) -> dict[str, Any] | None:
    symbol = source["ticker"]
    role = source["role_validity"]
    eligible: list[tuple[int, dict[str, Any]]] = []
    for candidate in candidates:
        candidate_ticker = candidate["candidate"]
        if candidate_ticker == symbol:
            continue
        if not candidate.get("is_fundable_candidate") or not _candidate_price_ok(
            candidate
        ):
            continue
        if candidate["destination_score"] < POLICY["destination_score_min_fundable"]:
            continue
        direct_target = candidate.get("direct_rs_vs_holding")
        direct3 = _num(candidate.get("direct_rs_vs_holding_3m_pct"), 0.0)
        if (
            direct_target == symbol
            and direct3 >= POLICY["relative_strength_3m_rotation_candidate"]
        ):
            eligible.append((0, candidate))
        elif role == "fail" and candidate.get("funding_scope") == "general":
            eligible.append((2, candidate))
        elif (
            role == "impaired"
            and source.get("weeks_replaceable", 0)
            >= POLICY["review_age_forced_decision"]
            and candidate.get("funding_scope") == "general"
        ):
            eligible.append((3, candidate))
    if not eligible:
        return None
    return sorted(
        eligible,
        key=lambda item: (
            item[0],
            -item[1]["destination_score"],
            item[1]["candidate"],
        ),
    )[0][1]


def build_decisions(
    incumbents: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    nav_eur: float,
    existing_tickers: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    decisions: list[dict[str, Any]] = []
    trade_intents: list[dict[str, Any]] = []
    target_weights: dict[str, float] = {
        row["ticker"]: row.get("current_weight_pct", 0.0) for row in incumbents
    }
    major_rotations = 0

    for source in sorted(
        incumbents,
        key=lambda row: (
            -row["release_score"],
            -row.get("weeks_replaceable", 0),
            row["ticker"],
        ),
    ):
        symbol = source["ticker"]
        release = source["release_score"]
        current_weight = float(source.get("current_weight_pct") or 0.0)
        destination = _choose_destination(source, candidates, existing_tickers)
        action = "hold"
        delta = 0.0
        destination_ticker = ""
        override_status = "none"
        override_reason_code = ""
        reason_codes = list(source.get("release_reasons") or [])

        if (
            release >= POLICY["release_score_replace_threshold"]
            and destination
            and major_rotations < POLICY["max_major_rotations_per_run"]
        ):
            action = "replace_partial"
            delta = -min(
                POLICY["max_single_source_reduction_pct_nav"], current_weight
            )
        elif release >= POLICY["release_score_reduce_threshold"]:
            if (
                destination
                and major_rotations < POLICY["max_major_rotations_per_run"]
            ):
                action = "replace_partial"
                delta = -min(POLICY["min_trade_size_pct_nav"], current_weight)
            else:
                action = "hold_with_override"
                override_status = "engine"
                override_reason_code = (
                    "no_fundable_destination"
                    if not destination
                    else "churn_budget_used"
                )
        elif (
            source.get("weeks_replaceable", 0)
            >= POLICY["review_age_block_passive_hold"]
        ):
            action = "hold_with_override"
            override_status = "engine"
            override_reason_code = "insufficient_confirming_window"

        if (
            action == "replace_partial"
            and abs(delta) < POLICY["min_trade_size_pct_nav"]
        ):
            action = "hold_with_override"
            override_status = "engine"
            override_reason_code = "min_trade_size_not_met"
            delta = 0.0

        if action == "replace_partial" and destination:
            destination_ticker = destination["candidate"]
            major_rotations += 1
            target_weights[symbol] = round(
                max(0.0, target_weights.get(symbol, current_weight) + delta), 2
            )
            target_weights[destination_ticker] = round(
                target_weights.get(destination_ticker, 0.0) + abs(delta), 2
            )
            trade_intents.append(
                {
                    "source_ticker": symbol,
                    "destination_ticker": destination_ticker,
                    "delta_weight_pct": round(delta, 2),
                    "destination_delta_weight_pct": round(abs(delta), 2),
                    "estimated_notional_eur": round(
                        nav_eur * abs(delta) / 100.0, 2
                    ),
                    "action_code": action,
                    "reason_codes": reason_codes
                    + [f"destination_score_{destination.get('destination_score')}"],
                    "destination_candidate_role": destination.get(
                        "candidate_role"
                    ),
                    "direct_rs_vs_holding_1m_pct": destination.get(
                        "direct_rs_vs_holding_1m_pct"
                    ),
                    "direct_rs_vs_holding_3m_pct": destination.get(
                        "direct_rs_vs_holding_3m_pct"
                    ),
                }
            )

        decisions.append(
            {
                "ticker": symbol,
                "action_code": action,
                "current_weight_pct": round(current_weight, 2),
                "target_weight_pct": round(
                    target_weights.get(symbol, current_weight), 2
                ),
                "delta_weight_pct": round(
                    target_weights.get(symbol, current_weight) - current_weight,
                    2,
                ),
                "destination_ticker": destination_ticker,
                "release_score": release,
                "role_validity": source.get("role_validity"),
                "weeks_replaceable": source.get("weeks_replaceable"),
                "reason_codes": reason_codes,
                "override_status": override_status,
                "override_reason_code": override_reason_code,
            }
        )

    target_weight_rows = [
        {"ticker": symbol, "target_weight_pct": round(weight, 2)}
        for symbol, weight in sorted(target_weights.items())
    ]
    return decisions, target_weight_rows, trade_intents


def build_rotation_plan(
    args: argparse.Namespace, *, persist_scorecard: bool = True
) -> dict[str, Any]:
    sources = _discover_sources(args)
    portfolio = _load_json(sources.portfolio_state)
    pricing = _load_json(sources.pricing_audit)
    lanes_payload = _load_json(sources.lane_assessment)
    rs_payload = (
        _load_json(sources.relative_strength)
        if sources.relative_strength and sources.relative_strength.exists()
        else {}
    )
    rs_metrics = {
        str(key).upper(): dict(value or {})
        for key, value in (rs_payload.get("metrics") or {}).items()
    }

    current_state = build_current_run_valuation_state(portfolio, pricing)
    report_date = str(
        current_state.get("report_date")
        or pricing.get("requested_close_date")
        or ""
    )
    previous_scorecard = _load_csv(sources.scorecard)
    refreshed_scorecard = refresh_scorecard_rows(
        previous_scorecard,
        current_state.get("positions", []) or [],
        report_date,
        source=f"current_run:{sources.pricing_audit}",
    )
    authority_validation = validate_current_run_authority(
        refreshed_scorecard,
        current_state.get("positions", []) or [],
        report_date,
    )
    if persist_scorecard:
        write_scorecard(sources.scorecard, refreshed_scorecard)

    scorecard_rows = _index(refreshed_scorecard)
    positions = current_state.get("positions", []) or []
    existing_tickers = {
        _ticker(position.get("ticker")) for position in positions
    }
    nav = _num(
        (current_state.get("portfolio") or {}).get(
            "total_portfolio_value_eur"
        ),
        0.0,
    )
    inc = incumbent_reviews(positions, scorecard_rows)
    cand = candidate_reviews(
        lanes_payload.get("assessed_lanes", []) or [],
        rs_metrics,
        existing_tickers,
    )
    decisions, target_weights, trade_intents = build_decisions(
        inc, cand, nav, existing_tickers
    )
    requested_close = (
        pricing.get("requested_close_date")
        or lanes_payload.get("report_date")
        or report_date
    )
    report_token = (
        str(requested_close or "unknown").replace("-", "")[2:]
        if requested_close
        else "unknown"
    )
    run_id = (
        pricing.get("run_id")
        or args.run_id
        or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )

    return {
        "schema_version": "1.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "report_token": report_token,
        "requested_close_date": requested_close,
        "source_files": {
            "portfolio_state": str(sources.portfolio_state),
            "scorecard": str(sources.scorecard),
            "pricing_audit": str(sources.pricing_audit),
            "lane_assessment": str(sources.lane_assessment),
            "relative_strength": (
                str(sources.relative_strength)
                if sources.relative_strength
                else None
            ),
            "current_run_valuation_state": "derived_in_memory_from_portfolio_state_and_current_pricing_audit",
        },
        "policy": POLICY,
        "portfolio": dict(current_state.get("portfolio") or {}),
        "state_authority_validation": authority_validation,
        "incumbent_reviews": inc,
        "candidate_reviews": cand,
        "rotation_decisions": decisions,
        "target_weights": target_weights,
        "trade_intents": trade_intents,
        "validation_flags": {
            "ticker_agnostic_rules": True,
            "trade_intents_canonical": True,
            "warning_mode_initial": True,
            "current_run_scorecard_refreshed_before_rotation": True,
            "current_run_pnl_recomputed": True,
            "current_run_valuation_used": True,
            "primary_and_alternative_candidates_independently_selectable": True,
            "stale_scorecard_or_pnl_mismatch_is_blocking": True,
        },
    }


def write_plan(plan: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    token = str(plan.get("report_token") or "unknown")
    run_id = str(plan.get("run_id") or "unknown")
    path = output_dir / f"etf_rotation_plan_{token}_{run_id}.json"
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    (output_dir / "latest_etf_rotation_plan_path.txt").write_text(
        str(path) + "\n", encoding="utf-8"
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deterministic ETF portfolio rotation plan"
    )
    parser.add_argument(
        "--portfolio-state", default=str(DEFAULT_PORTFOLIO_STATE)
    )
    parser.add_argument("--scorecard", default=str(DEFAULT_SCORECARD))
    parser.add_argument("--pricing-audit", default="")
    parser.add_argument("--lane-artifact", default="")
    parser.add_argument("--relative-strength", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-dir", default=str(OUTPUT_RUNTIME_DIR))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    plan = build_rotation_plan(args, persist_scorecard=not args.dry_run)
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    out = write_plan(plan, Path(args.output_dir))
    print(
        "ETF_ROTATION_PLAN_OK | "
        f"plan={out} | decisions={len(plan.get('rotation_decisions', []))} | "
        f"trade_intents={len(plan.get('trade_intents', []))} | "
        f"requested_close={plan.get('requested_close_date')} | "
        "state_authority=current_run_validated"
    )


if __name__ == "__main__":
    main()
