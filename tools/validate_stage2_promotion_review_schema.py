#!/usr/bin/env python3
"""Validate the Stage-2 promotion review artifact schema.

WP31 is schema/review-artifact design and validation only. It defines a future
review artifact shape without granting Stage-2 client-facing, production report,
lane-scoring, fundability, portfolio-action, delivery, execution, or historical
output mutation authority.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA_PATH = Path("schemas/stage2_promotion_review.schema.json")

ALLOWED_REVIEW_STATUSES = {
    "not_ready_missing_evidence",
    "eligible_for_promotion_review_not_promoted",
    "blocked_by_authority_boundary",
    "rejected_by_review_not_promoted",
}

FORBIDDEN_STATUSES = {
    "promoted",
    "fundable",
    "recommended",
    "client_facing",
    "portfolio_action_ready",
    "production_ready",
    "delivery_ready",
    "execution_ready",
}

REQUIRED_TOP_LEVEL = [
    "schema_version",
    "artifact_type",
    "generated_at_utc",
    "review_status",
    "promotion_status",
    "authority",
    "source_artifacts",
    "review_findings",
    "missing_requirements",
    "non_goals",
]

REQUIRED_AUTHORITY = {
    "shadow_only": True,
    "client_facing_authority": False,
    "production_report_narrative_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
    "portfolio_action_authority": False,
    "portfolio_mutation": False,
    "historical_output_mutation": False,
    "delivery_authority": False,
    "execution_authority": False,
    "report_surface_allowed": False,
    "production_report_path_changed": False,
}

REQUIRED_SOURCE_ARTIFACTS = [
    "stage2_confirmation_validation",
    "stage2_confirmation",
    "thesis_candidates",
    "relative_strength",
    "pricing_audit",
    "portfolio_state",
    "portfolio_discipline_clearance",
    "bilingual_aliases",
    "leakage_validation",
    "macro_report_surface_validation",
]

FORBIDDEN_REVIEW_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (reason, re.compile(pattern, re.IGNORECASE))
    for reason, pattern in [
        ("raw Stage-1/Stage-2 status label", r"\bstage[_ -]?[12][a-z0-9_ -]*(?:candidate|fundable|confirmation|confirmed)\b"),
        ("raw driver plumbing label", r"\b(driver_id|driver_ids|active_drivers|driver_catalog|driver_beneficiary_map)\b"),
        ("raw shadow/internal label", r"\b(shadow_only|internal_only)\b"),
    ]
)


@dataclass(frozen=True)
class ReviewSchemaFinding:
    field: str
    value: str
    reason: str


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"JSON file does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON file must contain an object: {path}")
    return payload


def _finding(field: str, value: Any, reason: str) -> ReviewSchemaFinding:
    return ReviewSchemaFinding(field=field, value=str(value), reason=reason)


def _raise_if_findings(findings: list[ReviewSchemaFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_SCHEMA_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review schema validation failed: findings={len(findings)}")


def validate_schema_definition(schema: dict[str, Any]) -> None:
    findings: list[ReviewSchemaFinding] = []

    if schema.get("type") != "object":
        findings.append(_finding("schema.type", schema.get("type"), "schema root must be an object"))
    if schema.get("additionalProperties") is not False:
        findings.append(_finding("schema.additionalProperties", schema.get("additionalProperties"), "schema must be closed/deterministic"))

    required = schema.get("required")
    if not isinstance(required, list):
        findings.append(_finding("schema.required", required, "required must be a list"))
        required = []
    for field in REQUIRED_TOP_LEVEL:
        if field not in required:
            findings.append(_finding(f"schema.required.{field}", required, "top-level field is not required"))

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        findings.append(_finding("schema.properties", properties, "properties must be an object"))
        _raise_if_findings(findings)
        return

    review_status = properties.get("review_status") or {}
    enum = set(review_status.get("enum") or []) if isinstance(review_status, dict) else set()
    if enum != ALLOWED_REVIEW_STATUSES:
        findings.append(_finding("schema.properties.review_status.enum", sorted(enum), "review_status enum must match allowed non-promotional statuses"))
    blocked = sorted(enum & FORBIDDEN_STATUSES)
    if blocked:
        findings.append(_finding("schema.properties.review_status.enum", blocked, "review_status enum includes forbidden promotional status"))

    promotion_status = properties.get("promotion_status") or {}
    if not isinstance(promotion_status, dict) or promotion_status.get("const") != "not_promoted":
        findings.append(_finding("schema.properties.promotion_status.const", promotion_status.get("const") if isinstance(promotion_status, dict) else promotion_status, "promotion_status must be const not_promoted"))

    artifact_type = properties.get("artifact_type") or {}
    if not isinstance(artifact_type, dict) or artifact_type.get("const") != "stage2_promotion_review":
        findings.append(_finding("schema.properties.artifact_type.const", artifact_type.get("const") if isinstance(artifact_type, dict) else artifact_type, "artifact_type must be const stage2_promotion_review"))

    authority = properties.get("authority") or {}
    if not isinstance(authority, dict):
        findings.append(_finding("schema.properties.authority", authority, "authority schema is required"))
    else:
        authority_required = authority.get("required") or []
        authority_props = authority.get("properties") or {}
        for field, expected in REQUIRED_AUTHORITY.items():
            if field not in authority_required:
                findings.append(_finding(f"schema.authority.required.{field}", authority_required, "authority field is not required"))
            field_schema = authority_props.get(field) if isinstance(authority_props, dict) else None
            if not isinstance(field_schema, dict) or field_schema.get("const") is not expected:
                findings.append(_finding(f"schema.authority.{field}.const", field_schema, f"authority.{field} must be const {expected!r}"))

    source_artifacts = properties.get("source_artifacts") or {}
    if not isinstance(source_artifacts, dict):
        findings.append(_finding("schema.properties.source_artifacts", source_artifacts, "source_artifacts schema is required"))
    else:
        source_required = source_artifacts.get("required") or []
        for field in REQUIRED_SOURCE_ARTIFACTS:
            if field not in source_required:
                findings.append(_finding(f"schema.source_artifacts.required.{field}", source_required, "source artifact field is not required"))

    _raise_if_findings(findings)


def valid_artifact() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "stage2_promotion_review",
        "generated_at_utc": "2026-06-17T00:00:00Z",
        "review_status": "eligible_for_promotion_review_not_promoted",
        "promotion_status": "not_promoted",
        "authority": dict(REQUIRED_AUTHORITY),
        "source_artifacts": {
            "stage2_confirmation_validation": "output/macro/validation/latest_stage2_confirmation_validation.json",
            "stage2_confirmation": "output/macro/latest_stage2_confirmation.json",
            "thesis_candidates": "output/macro/latest_thesis_candidates.json",
            "relative_strength": "output/market_history/etf_relative_strength.json",
            "pricing_audit": "output/pricing/price_audit_<requested_close_date>_<run_id>.json",
            "portfolio_state": "output/etf_portfolio_state.json",
            "portfolio_discipline_clearance": "output/etf_recommendation_scorecard.csv",
            "bilingual_aliases": "config/macro_thesis_bilingual_aliases.yml",
            "leakage_validation": "tools/validate_etf_macro_thesis_surface_leakage.py",
            "macro_report_surface_validation": "tools/validate_macro_report_surface.py",
        },
        "review_findings": [],
        "missing_requirements": [],
        "non_goals": [
            "no production report change",
            "no lane scoring change",
            "no fundability change",
            "no portfolio action",
            "no delivery or execution change",
        ],
    }


def validate_artifact(payload: dict[str, Any]) -> None:
    findings: list[ReviewSchemaFinding] = []

    for field in REQUIRED_TOP_LEVEL:
        if field not in payload:
            findings.append(_finding(field, "<missing>", "missing required top-level field"))

    if payload.get("schema_version") != "1.0":
        findings.append(_finding("schema_version", payload.get("schema_version"), "schema_version must be 1.0"))
    if payload.get("artifact_type") != "stage2_promotion_review":
        findings.append(_finding("artifact_type", payload.get("artifact_type"), "artifact_type must be stage2_promotion_review"))

    review_status = payload.get("review_status")
    if review_status in FORBIDDEN_STATUSES:
        findings.append(_finding("review_status", review_status, "forbidden promotional status"))
    elif review_status not in ALLOWED_REVIEW_STATUSES:
        findings.append(_finding("review_status", review_status, "unknown or non-review status"))

    if payload.get("promotion_status") != "not_promoted":
        findings.append(_finding("promotion_status", payload.get("promotion_status"), "promotion_status must remain not_promoted"))

    authority = payload.get("authority")
    if not isinstance(authority, dict):
        findings.append(_finding("authority", authority, "authority block is required"))
    else:
        for field, expected in REQUIRED_AUTHORITY.items():
            if authority.get(field) is not expected:
                findings.append(_finding(f"authority.{field}", authority.get(field), f"must be {expected!r}"))

    source_artifacts = payload.get("source_artifacts")
    if not isinstance(source_artifacts, dict):
        findings.append(_finding("source_artifacts", source_artifacts, "source_artifacts object is required"))
    else:
        for field in REQUIRED_SOURCE_ARTIFACTS:
            value = source_artifacts.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(_finding(f"source_artifacts.{field}", value, "source artifact reference must be a non-empty string"))

    for list_field in ["review_findings", "missing_requirements", "non_goals"]:
        if not isinstance(payload.get(list_field), list):
            findings.append(_finding(list_field, payload.get(list_field), "must be a list"))

    _validate_review_text(payload, findings)
    _raise_if_findings(findings)


def _validate_review_text(payload: dict[str, Any], findings: list[ReviewSchemaFinding]) -> None:
    text_buckets: list[tuple[str, str]] = []
    for idx, finding in enumerate(payload.get("review_findings") or []):
        if isinstance(finding, dict):
            for field in ["code", "summary"]:
                value = finding.get(field)
                if isinstance(value, str):
                    text_buckets.append((f"review_findings[{idx}].{field}", value))
    for list_field in ["missing_requirements", "non_goals"]:
        for idx, value in enumerate(payload.get(list_field) or []):
            if isinstance(value, str):
                text_buckets.append((f"{list_field}[{idx}]", value))
    for field, value in text_buckets:
        for reason, pattern in FORBIDDEN_REVIEW_TEXT_PATTERNS:
            match = pattern.search(value)
            if match:
                findings.append(_finding(field, value, f"{reason}: {match.group(0)}"))


def validate_schema_file(path: Path = DEFAULT_SCHEMA_PATH) -> None:
    validate_schema_definition(_load_json(path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--artifact", type=Path, action="append", default=[])
    args = parser.parse_args()

    validate_schema_file(args.schema)
    validate_artifact(valid_artifact())
    for artifact in args.artifact:
        validate_artifact(_load_json(artifact))
    print(f"STAGE2_PROMOTION_REVIEW_SCHEMA_OK | schema={args.schema}")


if __name__ == "__main__":
    main()
