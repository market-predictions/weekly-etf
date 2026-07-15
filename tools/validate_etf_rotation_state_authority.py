#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_FLAGS = {
    "current_run_scorecard_refreshed_before_rotation",
    "current_run_pnl_recomputed",
    "current_run_valuation_used",
    "primary_and_alternative_candidates_independently_selectable",
    "stale_scorecard_or_pnl_mismatch_is_blocking",
    "average_entry_history_reconstruction_is_blocking",
    "destination_tie_break_uses_quality_evidence",
}

REQUIRED_AUTHORITY_PROOFS = {
    "scorecard_date_aligned",
    "pnl_consistent_with_current_close_and_avg_entry",
    "average_entry_authority_complete",
    "current_price_consistent",
}


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    flags = dict(plan.get("validation_flags") or {})
    for key in sorted(REQUIRED_FLAGS):
        if flags.get(key) is not True:
            errors.append(f"missing_or_false_validation_flag:{key}")

    authority = dict(plan.get("state_authority_validation") or {})
    for key in sorted(REQUIRED_AUTHORITY_PROOFS):
        if authority.get(key) is not True:
            errors.append(f"missing_or_false_authority_proof:{key}")

    candidate_reviews = plan.get("candidate_reviews", []) or []
    roles = {str(row.get("candidate_role") or "") for row in candidate_reviews}
    if "primary" not in roles:
        errors.append("candidate_role_primary_missing")
    if "alternative" not in roles:
        errors.append("candidate_role_alternative_missing")

    for intent in plan.get("trade_intents", []) or []:
        if not intent.get("source_ticker") or not intent.get("destination_ticker"):
            errors.append("trade_intent_missing_source_or_destination")
        if abs(float(intent.get("delta_weight_pct") or 0.0)) < 2.0:
            errors.append("trade_intent_below_minimum_weight")

    if errors:
        raise RuntimeError(
            "ETF rotation state-authority validation failed: " + "; ".join(errors)
        )
    return {
        "status": "passed",
        "validated_holding_count": authority.get("validated_holding_count"),
        "candidate_review_count": len(candidate_reviews),
        "trade_intent_count": len(plan.get("trade_intents", []) or []),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()
    path = Path(args.plan)
    plan = json.loads(path.read_text(encoding="utf-8"))
    result = validate_plan(plan)
    print(
        "ETF_ROTATION_STATE_AUTHORITY_OK | "
        f"plan={path} | holdings={result.get('validated_holding_count')} | "
        f"candidates={result.get('candidate_review_count')} | "
        f"trade_intents={result.get('trade_intent_count')}"
    )


if __name__ == "__main__":
    main()
