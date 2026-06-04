#!/usr/bin/env python3
"""Validate Stage-2 thesis promotion contract artifacts.

This is a contract validator only. It must not promote thesis candidates to
client-facing, lane-scoring, fundability, portfolio-action, or report authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {
    "not_ready_missing_chain",
    "ready_for_promotion_review_not_promoted",
    "blocked_by_authority_boundary",
}

BLOCKED_STATUSES = {
    "fundable",
    "recommended",
    "portfolio_action_ready",
    "client_facing",
}

REQUIRED_AUTHORITY_FALSE = [
    "client_facing_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "portfolio_action_authority",
    "report_surface_allowed",
    "production_report_path_changed",
]

REQUIRED_TOP_LEVEL = [
    "schema_version",
    "artifact_type",
    "authority",
    "stage_2_chain_status",
    "active_driver_id",
    "taxonomy_tag",
    "lane_name",
    "primary_etf",
    "driver_to_beneficiary_rationale",
    "relative_strength_confirmation",
    "valuation_grade_pricing",
    "portfolio_discipline_clearance",
    "missing_requirements",
    "promotion_status",
]

REQUIRED_RS_FIELDS = [
    "return_1m_pct",
    "return_3m_pct",
    "rs_vs_spy_1m_pct",
    "rs_vs_spy_3m_pct",
    "relative_strength_score",
    "source_artifact",
]

REQUIRED_PRICE_FIELDS = [
    "primary_etf",
    "price_status",
    "pricing_tier",
    "source",
    "requested_close_date",
    "close_date_used",
]

REQUIRED_PORTFOLIO_FIELDS = [
    "current_holding_overlap",
    "cash_policy_sizing_room",
    "capital_reunderwriting_status",
    "recommendation_scorecard_memory",
    "replacement_or_addition_rationale",
    "clearance_status",
]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _require_present(payload: dict[str, Any], fields: list[str], label: str) -> None:
    missing = [field for field in fields if field not in payload]
    if missing:
        raise SystemExit(f"{label} missing required fields: {missing}")


def validate_artifact(payload: dict[str, Any]) -> None:
    _require_present(payload, REQUIRED_TOP_LEVEL, "stage2 artifact")

    if payload.get("artifact_type") != "stage_2_thesis_promotion_chain":
        raise SystemExit("Unexpected artifact_type")

    status = str(payload.get("stage_2_chain_status"))
    if status in BLOCKED_STATUSES:
        raise SystemExit(f"Blocked promotion status is not allowed: {status}")
    if status not in ALLOWED_STATUSES:
        raise SystemExit(f"Unknown stage_2_chain_status: {status}")

    if payload.get("promotion_status") != "not_promoted":
        raise SystemExit("promotion_status must remain not_promoted")

    authority = payload.get("authority") or {}
    if not isinstance(authority, dict):
        raise SystemExit("authority must be an object")
    for field in REQUIRED_AUTHORITY_FALSE:
        if authority.get(field) is not False:
            raise SystemExit(f"authority.{field} must be false")

    if not str(payload.get("active_driver_id") or "").strip():
        raise SystemExit("active_driver_id is required")
    if not str(payload.get("taxonomy_tag") or "").strip():
        raise SystemExit("taxonomy_tag is required")
    if not str(payload.get("driver_to_beneficiary_rationale") or "").strip():
        raise SystemExit("driver_to_beneficiary_rationale is required")

    rs = payload.get("relative_strength_confirmation") or {}
    price = payload.get("valuation_grade_pricing") or {}
    portfolio = payload.get("portfolio_discipline_clearance") or {}
    if not isinstance(rs, dict) or not isinstance(price, dict) or not isinstance(portfolio, dict):
        raise SystemExit("chain sub-objects must be objects")

    if status == "ready_for_promotion_review_not_promoted":
        _require_present(rs, REQUIRED_RS_FIELDS, "relative_strength_confirmation")
        _require_present(price, REQUIRED_PRICE_FIELDS, "valuation_grade_pricing")
        _require_present(portfolio, REQUIRED_PORTFOLIO_FIELDS, "portfolio_discipline_clearance")
        if price.get("pricing_tier") != "valuation_grade":
            raise SystemExit("valuation_grade_pricing.pricing_tier must be valuation_grade")
        if payload.get("missing_requirements") != []:
            raise SystemExit("ready_for_promotion_review_not_promoted requires no missing_requirements")

    print(
        "ETF_STAGE2_THESIS_PROMOTION_CONTRACT_OK | "
        f"status={status} | driver={payload.get('active_driver_id')} | tag={payload.get('taxonomy_tag')}"
    )


def validate_contract_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = [
        "active thesis driver",
        "mapped beneficiary lane",
        "relative-strength confirmation",
        "valuation-grade pricing",
        "portfolio-discipline clearance",
        "explicit control-layer promotion decision",
        "client_facing_authority: false",
        "fundability_authority: false",
        "portfolio_action_authority: false",
        "ready_for_promotion_review_not_promoted",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise SystemExit(f"Contract text missing required phrases: {missing}")
    print("ETF_STAGE2_THESIS_PROMOTION_CONTRACT_TEXT_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=Path("control/STAGE2_THESIS_PROMOTION_CONTRACT.md"))
    parser.add_argument("--artifact", type=Path, action="append", default=[])
    parser.add_argument("--expect-fail", action="store_true")
    args = parser.parse_args()

    try:
        validate_contract_text(args.contract)
        for artifact in args.artifact:
            validate_artifact(_load_json(artifact))
    except SystemExit:
        if args.expect_fail:
            print("ETF_STAGE2_THESIS_PROMOTION_CONTRACT_EXPECTED_FAILURE_OK")
            return
        raise

    if args.expect_fail:
        raise SystemExit("Expected Stage-2 thesis promotion contract failure, but validation passed")


if __name__ == "__main__":
    main()
