from __future__ import annotations

import argparse
from pathlib import Path

import runtime.portfolio_rotation_engine_v2 as _v2
from runtime.etf_instrument_constraints import (
    DEFAULT_CONSTRAINTS_PATH,
    apply_rotation_policy_constraints,
    load_instrument_constraints,
)
from runtime.portfolio_rotation_engine_v2 import *  # noqa: F401,F403


def _normalize_blocked_zero_trade_overrides(plan: dict) -> dict:
    """Remove stale rotation-budget claims after constraints erase all trades.

    The unconstrained engine processes incumbent reviews sequentially and may mark
    later reviews as ``churn_budget_used`` after selecting one provisional
    rotation. Portfolio constraints can subsequently reject that provisional
    transition and clear every trade intent. In that final zero-trade state, a
    consumed-rotation label is no longer true and must inherit the actual
    portfolio block instead.
    """
    trades = plan.get("trade_intents") or []
    validation = plan.get("portfolio_constraint_validation") or {}
    block_reason = str(validation.get("block_reason") or "").strip()
    if trades or not block_reason:
        return plan

    normalized = 0
    for decision in plan.get("rotation_decisions", []) or []:
        if str(decision.get("override_reason_code") or "") != "churn_budget_used":
            continue
        decision["action_code"] = "hold_with_override"
        decision["override_status"] = "engine"
        decision["override_reason_code"] = "portfolio_constraint_blocked"
        decision["destination_ticker"] = ""
        decision["delta_weight_pct"] = 0.0
        decision["target_weight_pct"] = decision.get("current_weight_pct", 0.0)
        reasons = list(decision.get("reason_codes") or [])
        if block_reason not in reasons:
            reasons.append(block_reason)
        decision["reason_codes"] = reasons
        normalized += 1

    plan.setdefault("validation_flags", {})[
        "zero_trade_stale_churn_status_removed"
    ] = True
    plan.setdefault("portfolio_constraint_validation", {})[
        "stale_churn_overrides_normalized"
    ] = normalized
    return plan


def _validate_constrained_plan(plan: dict) -> None:
    validation = plan.get("portfolio_constraint_validation") or {}
    final_assessment = validation.get("final_position_count_assessment") or {}
    if final_assessment.get("passed") is not True:
        raise RuntimeError(
            "ETF rotation plan blocked: final position-count assessment did not pass"
        )
    blocked = set(validation.get("blocked_candidates") or [])
    invalid = sorted(
        {
            str(row.get("destination_ticker") or "").strip().upper()
            for row in plan.get("trade_intents", []) or []
            if str(row.get("destination_ticker") or "").strip().upper() in blocked
        }
    )
    if invalid:
        raise RuntimeError(
            "ETF rotation plan blocked: portfolio-ineligible destination(s): "
            + ",".join(invalid)
        )
    if not (plan.get("trade_intents") or []):
        stale = sorted(
            str(row.get("ticker") or "").strip().upper()
            for row in plan.get("rotation_decisions", []) or []
            if str(row.get("override_reason_code") or "") == "churn_budget_used"
        )
        if stale:
            raise RuntimeError(
                "ETF rotation plan blocked: zero-trade plan retains stale "
                "churn-budget status for " + ",".join(stale)
            )
    flags = plan.get("validation_flags") or {}
    required_flags = (
        "instrument_eligibility_enforced",
        "leveraged_etf_constraint_enforced",
        "position_count_transition_enforced",
        "portfolio_constraint_validation_passed",
    )
    missing = [name for name in required_flags if flags.get(name) is not True]
    if missing:
        raise RuntimeError(
            "ETF rotation plan blocked: missing portfolio-constraint flags: "
            + ",".join(missing)
        )


def build_rotation_plan(
    args: argparse.Namespace, *, persist_scorecard: bool = True
) -> dict:
    raw_plan = _v2.build_rotation_plan(
        args, persist_scorecard=persist_scorecard
    )
    constraints_path = Path(
        getattr(args, "instrument_constraints", "") or DEFAULT_CONSTRAINTS_PATH
    )
    constraints = load_instrument_constraints(constraints_path)
    plan = apply_rotation_policy_constraints(raw_plan, constraints)
    plan = _normalize_blocked_zero_trade_overrides(plan)
    _validate_constrained_plan(plan)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deterministic ETF portfolio rotation plan"
    )
    parser.add_argument(
        "--portfolio-state", default=str(_v2.DEFAULT_PORTFOLIO_STATE)
    )
    parser.add_argument("--scorecard", default=str(_v2.DEFAULT_SCORECARD))
    parser.add_argument("--pricing-audit", default="")
    parser.add_argument("--lane-artifact", default="")
    parser.add_argument("--relative-strength", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-dir", default=str(_v2.OUTPUT_RUNTIME_DIR))
    parser.add_argument(
        "--instrument-constraints", default=str(DEFAULT_CONSTRAINTS_PATH)
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    plan = build_rotation_plan(args, persist_scorecard=not args.dry_run)
    if args.dry_run:
        import json

        print(json.dumps(plan, indent=2))
        return
    out = _v2.write_plan(plan, Path(args.output_dir))
    validation = plan.get("portfolio_constraint_validation") or {}
    print(
        "ETF_ROTATION_PLAN_OK | "
        f"plan={out} | decisions={len(plan.get('rotation_decisions', []))} | "
        f"trade_intents={len(plan.get('trade_intents', []))} | "
        f"requested_close={plan.get('requested_close_date')} | "
        f"constraint_block={validation.get('block_reason') or 'none'} | "
        "state_authority=current_run_validated"
    )


if __name__ == "__main__":
    main()
