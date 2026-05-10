from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class LaneContext:
    held_tickers: set[str]
    prior_promoted_tickers: set[str]
    price_status_by_symbol: dict[str, str]
    priced_symbols: set[str]
    portfolio_gap_themes: dict[str, int]
    relative_strength_metrics: dict[str, dict[str, Any]] = field(default_factory=dict)
    macro_policy_pack: dict[str, Any] = field(default_factory=dict)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def weighted_lane_score(lane: dict[str, Any]) -> float:
    score = 0.0
    for key, weight in LANE_WEIGHTS.items():
        score += _num(lane.get(key), 0.0) * weight
    return round(score, 2)


def rs_metrics(symbol: str, context: LaneContext) -> dict[str, Any]:
    return dict(context.relative_strength_metrics.get(symbol.upper(), {}) or {})


def rs_score(symbol: str, context: LaneContext) -> float:
    metrics = rs_metrics(symbol, context)
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


def portfolio_gap_score(lane: dict[str, Any], context: LaneContext) -> int:
    taxonomy = str(lane.get("taxonomy_tag", ""))
    bucket = str(lane.get("bucket", ""))
    primary = str(lane.get("primary_etf", "")).upper()
    alt = str(lane.get("alternative_etf", "")).upper()

    if primary in context.held_tickers or alt in context.held_tickers:
        return 1
    return int(context.portfolio_gap_themes.get(taxonomy, context.portfolio_gap_themes.get(bucket, 2)))


def pricing_confidence(symbol: str, context: LaneContext) -> str:
    symbol = symbol.upper()
    status = context.price_status_by_symbol.get(symbol)
    if status in {"fresh_close", "fresh_fallback_source"}:
        return "fresh_priced"
    if symbol in context.priced_symbols:
        return "latest_verified_or_challenger_priced"
    return "not_priced_in_current_audit"


def novelty_status(lane: dict[str, Any], context: LaneContext) -> str:
    configured = lane.get("novelty_status")
    primary = str(lane.get("primary_etf", "")).upper()
    alt = str(lane.get("alternative_etf", "")).upper()
    if primary in context.prior_promoted_tickers or alt in context.prior_promoted_tickers:
        if configured and str(configured).startswith("retained"):
            return str(configured)
        return "retained_memory"
    return str(configured or "new_or_rotating_challenger")


def is_challenger(lane: dict[str, Any], context: LaneContext) -> bool:
    primary = str(lane.get("primary_etf", "")).upper()
    alt = str(lane.get("alternative_etf", "")).upper()
    novelty = novelty_status(lane, context)
    return (
        primary not in context.held_tickers
        and alt not in context.held_tickers
    ) or "challenger" in novelty or "near_miss" in novelty


def macro_adjustment(lane: dict[str, Any], context: LaneContext) -> tuple[float, str]:
    pack = dict(context.macro_policy_pack or {})
    adjustments = dict(pack.get("lane_adjustments", {}) or {})

    candidates = [
        str(lane.get("lane_name") or ""),
        str(lane.get("taxonomy_tag") or ""),
        str(lane.get("bucket") or ""),
    ]

    for key in candidates:
        if key in adjustments:
            payload = adjustments[key]
            return (
                max(min(_num(payload.get("score_adjustment"), 0.0), 0.20), -0.20),
                str(payload.get("reason") or "Macro-policy adjustment applied."),
            )

    return 0.0, ""


def adjusted_lane_score(lane: dict[str, Any], context: LaneContext) -> tuple[float, float, str]:
    primary = str(lane.get("primary_etf", "")).upper()
    alt = str(lane.get("alternative_etf", "")).upper()
    base = weighted_lane_score(lane)
    gap_bonus = min(portfolio_gap_score(lane, context), 5) * 0.03
    primary_conf = pricing_confidence(primary, context)
    price_bonus = 0.05 if primary_conf == "fresh_priced" else 0.02 if primary_conf == "latest_verified_or_challenger_priced" else -0.03
    novelty = novelty_status(lane, context)
    novelty_bonus = 0.04 if novelty in {"new_or_rotating_challenger", "rotating_challenger"} else 0.0
    primary_rs = rs_score(primary, context)
    alt_rs = rs_score(alt, context) if alt else 0.0
    market_bonus = max(primary_rs, alt_rs * 0.65)
    macro_bonus, macro_reason = macro_adjustment(lane, context)
    total = round(base + gap_bonus + price_bonus + novelty_bonus + market_bonus + macro_bonus, 2)
    return total, macro_bonus, macro_reason


def _rejection_reason(lane: dict[str, Any]) -> str:
    timing = _num(lane.get("timing_confirmation"), 0.0)
    macro = _num(lane.get("macro_alignment"), 0.0)
    impl = _num(lane.get("implementation_quality"), 0.0)
    primary_status = str(lane.get("primary_price_status", ""))
    r1 = lane.get("return_1m_pct")
    r3 = lane.get("return_3m_pct")
    rs3 = lane.get("rs_vs_spy_3m_pct")

    if "not_in_current_pricing_audit" in primary_status and r1 is None:
        return "Structurally relevant, but neither current audit pricing nor historical momentum was available; keep as discovery candidate, not fundable replacement."
    if r3 is not None and float(r3) < 0:
        return "Structural case is credible, but 3-month price momentum is still negative."
    if rs3 is not None and float(rs3) < 0:
        return "Not promoted because it still trails SPY on 3-month relative strength."
    if timing <= 2:
        return "Structural case is credible, but timing confirmation still trails higher-ranked lanes."
    if macro <= 2:
        return "Macro alignment is not yet strong enough to displace funded exposures."
    if impl <= 2:
        return "Implementation quality or ETF vehicle confidence is not strong enough yet."
    return "Scored below promoted lanes despite valid thesis; needs stronger relative timing or portfolio-fit evidence."


def _rs_fields(primary: str, context: LaneContext) -> dict[str, Any]:
    metrics = rs_metrics(primary, context)
    return {
        "return_1m_pct": metrics.get("return_1m_pct"),
        "return_3m_pct": metrics.get("return_3m_pct"),
        "trend_quality": metrics.get("trend_quality"),
        "max_drawdown_3m_pct": metrics.get("max_drawdown_3m_pct"),
        "volatility_3m_pct": metrics.get("volatility_3m_pct"),
        "rs_vs_spy_1m_pct": metrics.get("rs_vs_spy_1m_pct"),
        "rs_vs_spy_3m_pct": metrics.get("rs_vs_spy_3m_pct"),
        "relative_strength_score": rs_score(primary, context),
    }


def score_lane(lane: dict[str, Any], context: LaneContext) -> dict[str, Any]:
    primary = str(lane.get("primary_etf", "")).upper()
    alt = str(lane.get("alternative_etf", "")).upper()
    total_score, macro_bonus, macro_reason = adjusted_lane_score(lane, context)
    primary_status = context.price_status_by_symbol.get(primary, "not_in_current_pricing_audit")
    alt_status = context.price_status_by_symbol.get(alt, "not_in_current_pricing_audit") if alt else "not_applicable"
    gap = portfolio_gap_score(lane, context)
    challenger = is_challenger(lane, context)
    novelty = novelty_status(lane, context)
    rs = _rs_fields(primary, context)

    output = dict(lane)
    output.update(
        {
            "primary_etf": primary,
            "alternative_etf": alt,
            "total_score": total_score,
            "prior_run_status": novelty,
            "challenger": challenger,
            "portfolio_gap_score": gap,
            "pricing_confidence": pricing_confidence(primary, context),
            "primary_price_status": primary_status,
            "alternative_price_status": alt_status,
            "macro_policy_adjustment": macro_bonus,
            "macro_policy_reason": macro_reason,
            "freshness_note": (
                "Historical relative strength was available and included in scoring."
                if rs.get("return_1m_pct") is not None or rs.get("return_3m_pct") is not None
                else "Primary ETF was assessed structurally but historical momentum was unavailable."
            ),
        }
    )
    output.update(rs)
    return output


def select_promoted_lanes(scored: list[dict[str, Any]], required_buckets: list[str]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for bucket in required_buckets:
        bucket_lanes = [lane for lane in scored if lane.get("bucket") == bucket]
        if not bucket_lanes:
            continue
        top = sorted(bucket_lanes, key=lambda x: float(x.get("total_score", 0.0)), reverse=True)[0]
        lane_id = str(top.get("taxonomy_tag"))
        if lane_id not in seen_ids and len(selected) < 5:
            selected.append(top)
            seen_ids.add(lane_id)

    for lane in sorted(scored, key=lambda x: float(x.get("total_score", 0.0)), reverse=True):
        lane_id = str(lane.get("taxonomy_tag"))
        if lane_id in seen_ids:
            continue
        selected.append(lane)
        seen_ids.add(lane_id)
        if len(selected) >= 6:
            break

    return selected[:8]


def apply_promotion_flags(scored: list[dict[str, Any]], promoted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    promoted_tags = {lane.get("taxonomy_tag") for lane in promoted}
    output: list[dict[str, Any]] = []
    for lane in scored:
        lane = dict(lane)
        is_promoted = lane.get("taxonomy_tag") in promoted_tags
        lane["promoted_to_live_radar"] = bool(is_promoted)
        if is_promoted:
            lane["rejection_reason"] = ""
        else:
            lane["rejection_reason"] = _rejection_reason(lane)
        output.append(lane)
    return output
