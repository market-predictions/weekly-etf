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
    return apply_rotation_policy_constraints(raw_plan, constraints)


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
