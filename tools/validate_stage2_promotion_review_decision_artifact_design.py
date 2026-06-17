#!/usr/bin/env python3
"""Validate the Stage-2 promotion review decision artifact design."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DESIGN_PATH = Path("control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md")

REQUIRED_PHRASES = {
    "design_only": "Design-only.",
    "no_live_decision_artifact": "No live decision artifact is created.",
    "no_stage2_promotion_decision": "No Stage-2 promotion decision is made.",
    "no_production_report_authority": "No production report authority is granted.",
    "no_scoring_authority": "No scoring authority is granted.",
    "no_fundability_authority": "No fundability authority is granted.",
    "no_portfolio_action_authority": "No portfolio-action authority is granted.",
    "no_delivery_execution_authority": "No delivery or execution authority is granted.",
    "no_historical_output_mutation_authority": "No historical-output mutation authority is granted.",
    "separate_future_implementation_package": "separate future implementation package",
    "no_output_artifact": "must not be committed under `output/` by WP34",
    "raw_fields_not_approved_labels": "must not be used as approved decision-facing labels",
}

REQUIRED_AUTHORITY_FIELDS = [
    "client_facing_authority: false",
    "production_report_narrative_authority: false",
    "lane_scoring_authority: false",
    "fundability_authority: false",
    "portfolio_action_authority: false",
    "portfolio_mutation: false",
    "historical_output_mutation: false",
    "delivery_authority: false",
    "execution_authority: false",
    "report_surface_allowed: false",
    "production_report_path_changed: false",
]

REQUIRED_CONTROL_BOOLEANS = [
    "decision_artifact_only: true",
    "implementation_required_before_production_use: true",
    "explicit_control_layer_decision_required: true",
]

REQUIRED_SOURCE_EVIDENCE = [
    "control/STAGE2_PROMOTION_BRIDGE_DESIGN.md",
    "schemas/stage2_promotion_review.schema.json",
    "tools/validate_stage2_promotion_review_checklist.py",
    "fixtures/stage2_promotion_review/manifest.json",
    "tools/validate_stage2_promotion_review_fixtures.py",
    "control/MACRO_STAGE2_CONFIRMATION_STATUS.md",
    "output/macro/validation/latest_stage2_confirmation_validation.json",
    "tools/validate_etf_macro_thesis_surface_leakage.py",
    "config/macro_thesis_bilingual_aliases.yml",
    "tools/validate_macro_report_surface.py",
    "control/CURRENT_STATE.md",
]

REQUIRED_STATUSES = [
    "not_promoted",
    "rejected_not_promoted",
    "blocked_missing_evidence",
    "blocked_by_authority_boundary",
    "ready_for_explicit_promotion_decision_not_promoted",
]

RAW_INTERNAL_FIELDS = [
    "stage_1_candidate",
    "stage_2_confirmed_not_fundable",
    "stage_2_fundable_ready_shadow",
    "stage2_status",
    "confirmation_status",
    "driver_id",
    "driver_ids",
    "active_drivers",
    "driver_catalog",
    "driver_beneficiary_map",
    "shadow_only",
    "internal_only",
]

FORBIDDEN_PATTERNS = tuple(
    (code, re.compile(pattern, re.IGNORECASE))
    for code, pattern in [
        ("claims_stage2_currently_promoted", r"\bstage[- ]?2\s+(?:is\s+now|is|has\s+been)\s+promoted\b"),
        ("claims_stage2_output_promoted", r"\bstage[- ]?2\s+output\s+(?:is\s+now|is|has\s+been)\s+promoted\b"),
        ("claims_stage2_currently_production_ready", r"\bstage[- ]?2\s+(?:is\s+)?production[- ]ready\b"),
        ("claims_stage2_currently_fundable", r"\bstage[- ]?2\s+(?:is\s+)?fundable\b"),
        ("claims_stage2_currently_recommended", r"\bstage[- ]?2\s+(?:is\s+)?recommended\b"),
    ]
)


@dataclass(frozen=True)
class DesignFinding:
    code: str
    detail: str


def _raise_if_findings(findings: list[DesignFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN_FINDING | "
            f"code={finding.code} | detail={finding.detail}"
        )
    raise RuntimeError(f"Stage-2 promotion review decision artifact design validation failed: findings={len(findings)}")


def validate_design_text(text: str) -> None:
    findings: list[DesignFinding] = []

    for code, phrase in REQUIRED_PHRASES.items():
        if phrase not in text:
            findings.append(DesignFinding(code, f"missing required phrase: {phrase}"))
    for field in REQUIRED_AUTHORITY_FIELDS:
        if field not in text:
            findings.append(DesignFinding("missing_authority_false_field", f"missing {field}"))
    for field in REQUIRED_CONTROL_BOOLEANS:
        if field not in text:
            findings.append(DesignFinding("missing_control_boolean", f"missing {field}"))
    for source in REQUIRED_SOURCE_EVIDENCE:
        if source not in text:
            findings.append(DesignFinding("missing_source_evidence", f"missing {source}"))
    for status in REQUIRED_STATUSES:
        if status not in text:
            findings.append(DesignFinding("missing_non_promotional_status", f"missing {status}"))
    for field in RAW_INTERNAL_FIELDS:
        if field not in text:
            findings.append(DesignFinding("missing_raw_internal_blocklist_field", f"missing {field}"))
    for code, pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append(DesignFinding(code, f"forbidden current-status claim: {match.group(0)}"))

    _raise_if_findings(findings)


def validate_design_file(path: Path = DEFAULT_DESIGN_PATH) -> None:
    if not path.exists():
        raise RuntimeError(f"design document does not exist: {path}")
    validate_design_text(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN_PATH)
    args = parser.parse_args()

    validate_design_file(args.design)
    print(f"STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN_OK | file={args.design}")


if __name__ == "__main__":
    main()
