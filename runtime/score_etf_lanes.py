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

EXACT_CLOSE_STATUSES = {"fresh_close", "fresh_exact_close", "fresh_exact_unverified"}
PRICED_CLOSE_STATUSES = EXACT_CLOSE_STATUSES | {"fresh_fallback_source", "prior_valid_close"}
VALUATION_GRADE = "valuation_grade"
RESEARCH_GRADE = "research_grade"


@dataclass(frozen=True)
class LaneContext:
    held_tickers: set[str]
    prior_promoted_tickers: set[str]
    price_status_by_symbol: dict[str, str]
    priced_symbols: set[str]
    portfolio_gap_themes: dict[str, int]
    price_tier_by_symbol: dict[str, str] = field(default_factory=dict)
    price_source_by_symbol: dict[str, str] = field(default_factory=dict)
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
