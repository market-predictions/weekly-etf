from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from runtime.position_count_contract import (
    DEFAULT_MAX_ACTIVE_POSITIONS,
    assess_position_count_transition,
)

DEFAULT_CONSTRAINTS_PATH = Path("config/etf_instrument_constraints.yml")
WEIGHT_EPSILON = 1e-9


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_instrument_constraints(path: Path = DEFAULT_CONSTRAINTS_PATH) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": "1.0",
            "portfolio_policy": {"max_active_positions": DEFAULT_MAX_ACTIVE_POSITIONS},
            "instruments": {},
        }
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    payload.setdefault("portfolio_policy", {})
    payload.setdefault("instruments", {})
    return payload


def instrument_rule(symbol: str, constraints: dict[str, Any]) -> dict[str, Any]:
    return dict((constraints.get("instruments") or {}).get(_ticker(symbol)) or {})


def instrument_eligibility(symbol: str, constraints: dict[str, Any]) -> tuple[bool, str]:
    rule = instrument_rule(symbol, constraints)
    eligible = bool(rule.get("portfolio_eligible", True))
    reason = str(rule.get("reason") or "")
    return eligible, reason


def _eligible_research_replacement(
    symbol: str, constraints: dict[str, Any]
) -> str:
    rule = instrument_rule(symbol, constraints)
    replacement = _ticker(rule.get("eligible_research_replacement"))
    if not replacement:
        return ""
    eligible, _ = instrument_eligibility(replacement, constraints)
    return replacement if eligible else ""


def normalize_lane_instruments(
    lane: dict[str, Any], constraints: dict[str, Any]
) -> dict[str, Any]:
    """Lead with eligible vehicles and remove ineligible client-facing alternatives."""
    item = dict(lane)
    primary = _ticker(item.get("primary_etf"))
    alternative = _ticker(item.get("alternative_etf"))
    original_primary = primary
    original_alternative = alternative
    primary_eligible, primary_reason = instrument_eligibility(primary, constraints)
    alternative_eligible, alternative_reason = instrument_eligibility(
        alternative, constraints
    )

    if primary and not primary_eligible and alternative and alternative_eligible:
        primary, alternative = alternative, primary
        primary_eligible, alternative_eligible = (
            alternative_eligible,
            primary_eligible,
        )
        primary_reason, alternative_reason = alternative_reason, primary_reason
        item["instrument_order_adjusted"] = True
        item[
            "instrument_order_adjustment_reason"
        ] = "eligible_vehicle_promoted_over_ineligible_vehicle"

    if alternative and not alternative_eligible:
        replacement = _eligible_research_replacement(alternative, constraints)
        item["excluded_research_vehicle"] = alternative
        item["excluded_research_vehicle_reason"] = alternative_reason
        if replacement and replacement != primary:
            alternative = replacement
            alternative_eligible, alternative_reason = instrument_eligibility(
                alternative, constraints
            )
            item["eligible_research_replacement_applied"] = True
        else:
            alternative = ""
            alternative_eligible = True
            alternative_reason = ""

    item["primary_etf"] = primary
    item["alternative_etf"] = alternative
    item["primary_portfolio_eligible"] = primary_eligible
    item["primary_ineligibility_reason"] = primary_reason
    item["alternative_portfolio_eligible"] = alternative_eligible
    item["alternative_ineligibility_reason"] = alternative_reason
    item["configured_primary_etf"] = original_primary
    item["configured_alternative_etf"] = original_alternative
    return item


def _current_weight_index(plan: dict[str, Any]) -> dict[str, float]:
    return {
        _ticker(row.get("ticker")): _num(row.get("current_weight_pct"), 0.0)
        for row in plan.get("incumbent_reviews", []) or []
        if _ticker(row.get("ticker"))
    }


def _projected_weight_index(
    plan: dict[str, Any], current: dict[str, float]
) -> dict[str, float]:
    projected = dict(current)
    for row in plan.get("target_weights", []) or []:
        ticker = _ticker(row.get("ticker"))
        if ticker:
            projected[ticker] = _num(row.get("target_weight_pct"), 0.0)
    return projected


def _positions_from_weights(weights: dict[str, float]) -> list[dict[str, Any]]:
    return [
        {"ticker": ticker, "shares": 1.0}
        for ticker, weight in sorted(weights.items())
        if weight > WEIGHT_EPSILON
    ]


def _reset_invalid_trade_intents(
    plan: dict[str, Any], *, reason_code: str
) -> None:
    current = _current_weight_index(plan)
    for decision in plan.get("rotation_decisions", []) or []:
        ticker = _ticker(decision.get("ticker"))
        if not ticker:
            continue
        if (
            _num(decision.get("delta_weight_pct"), 0.0) != 0.0
            or _ticker(decision.get("destination_ticker"))
            or str(decision.get("action_code") or "")
            in {
                "replace_partial",
                "replace_full",
                "reduce",
                "close",
                "add_from_cash",
            }
        ):
            decision["action_code"] = "hold_with_override"
            decision["target_weight_pct"] = round(
                current.get(ticker, 0.0), 2
            )
            decision["delta_weight_pct"] = 0.0
            decision["destination_ticker"] = ""
            decision["override_status"] = "engine"
            decision["override_reason_code"] = "portfolio_constraint_blocked"
            reasons = list(decision.get("reason_codes") or [])
            if reason_code not in reasons:
                reasons.append(reason_code)
            decision["reason_codes"] = reasons

    plan["target_weights"] = [
        {"ticker": ticker, "target_weight_pct": round(weight, 2)}
        for ticker, weight in sorted(current.items())
    ]
    plan["trade_intents"] = []


def apply_rotation_policy_constraints(
    raw_plan: dict[str, Any], constraints: dict[str, Any]
) -> dict[str, Any]:
    plan = deepcopy(raw_plan)
    policy = dict(constraints.get("portfolio_policy") or {})
    max_active = int(
        policy.get("max_active_positions", DEFAULT_MAX_ACTIVE_POSITIONS)
    )
    instrument_rules = dict(constraints.get("instruments") or {})

    blocked_candidates: list[str] = []
    for candidate in plan.get("candidate_reviews", []) or []:
        ticker = _ticker(candidate.get("candidate"))
        eligible, reason = instrument_eligibility(ticker, constraints)
        candidate["portfolio_eligible"] = eligible
        candidate["portfolio_ineligibility_reason"] = reason
        if not eligible:
            blocked_candidates.append(ticker)
            candidate["is_fundable_candidate"] = False
            candidate["funding_scope"] = "not_fundable"
            reasons = list(candidate.get("destination_reasons") or [])
            marker = f"portfolio_ineligible_{reason or 'instrument_constraint'}"
            if marker not in reasons:
                reasons.append(marker)
            candidate["destination_reasons"] = reasons

    blocked_set = set(blocked_candidates)
    invalid_destinations = sorted(
        {
            _ticker(intent.get("destination_ticker"))
            for intent in plan.get("trade_intents", []) or []
            if _ticker(intent.get("destination_ticker")) in blocked_set
        }
    )

    current = _current_weight_index(plan)
    projected = _projected_weight_index(plan, current)
    initial_assessment = assess_position_count_transition(
        _positions_from_weights(current),
        _positions_from_weights(projected),
        max_active_positions=max_active,
        trade_intents_present=bool(plan.get("trade_intents")),
    )

    block_reason = ""
    if invalid_destinations:
        block_reason = "portfolio_ineligible_destination"
    elif not initial_assessment.passed:
        block_reason = "position_count_close_first"

    if block_reason:
        _reset_invalid_trade_intents(plan, reason_code=block_reason)

    final_current = _current_weight_index(plan)
    final_projected = _projected_weight_index(plan, final_current)
    final_assessment = assess_position_count_transition(
        _positions_from_weights(final_current),
        _positions_from_weights(final_projected),
        max_active_positions=max_active,
        trade_intents_present=bool(plan.get("trade_intents")),
    )

    plan.setdefault("policy", {})["max_active_positions"] = max_active
    plan["policy"]["leveraged_etfs_allowed"] = bool(
        policy.get("leveraged_etfs_allowed", False)
    )
    plan["portfolio_constraint_validation"] = {
        "constraint_schema_version": constraints.get("schema_version"),
        "instrument_constraint_count": len(instrument_rules),
        "blocked_candidates": sorted(set(blocked_candidates)),
        "invalid_trade_destinations": invalid_destinations,
        "block_reason": block_reason or None,
        "initial_position_count_assessment": initial_assessment.to_dict(),
        "final_position_count_assessment": final_assessment.to_dict(),
        "trade_intents_after_constraints": len(
            plan.get("trade_intents", []) or []
        ),
    }
    plan.setdefault("validation_flags", {}).update(
        {
            "instrument_eligibility_enforced": True,
            "leveraged_etf_constraint_enforced": True,
            "position_count_transition_enforced": True,
            "portfolio_constraint_validation_passed": final_assessment.passed,
        }
    )
    return plan
