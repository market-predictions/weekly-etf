#!/usr/bin/env python3
"""Validate the Stage-2 promotion review decision artifact schema.

WP35/WP36 are schema and fixture validation only. They define and prove a
future decision artifact shape without creating live decision artifacts,
promoting Stage-2 output, or granting production authority.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA_PATH = Path("schemas/stage2_promotion_review_decision.schema.json")

ALLOWED_DECISION_STATUSES = {
    "not_promoted",
    "rejected_not_promoted",
    "blocked_missing_evidence",
    "blocked_by_authority_boundary",
    "ready_for_explicit_promotion_decision_not_promoted",
}

FORBIDDEN_DECISION_STATUSES = {
    "promoted",
    "fundable",
    "recommended",
    "client_facing",
    "production_ready",
    "portfolio_action_ready",
    "delivery_ready",
    "execution_ready",
    "trade_ready",
    "buy",
    "sell",
    "allocate",
}

REQUIRED_TOP_LEVEL = [
    "schema_version",
    "artifact_type",
    "generated_at_utc",
    "decision_status",
    "decision_scope",
    "authority",
    "source_evidence",
    "decision_rationale",
    "blocking_conditions",
    "required_future_work",
    "non_goals",
]

REQUIRED_AUTHORITY = {
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
    "decision_artifact_only": True,
    "implementation_required_before_production_use": True,
    "explicit_control_layer_decision_required": True,
}

REQUIRED_SOURCE_EVIDENCE = [
    "promotion_bridge_design",
    "review_schema",
    "review_checklist_validator",
    "fixture_manifest",
    "fixture_validator",
    "decision_artifact_design",
    "decision_artifact_design_validator",
    "stage2_shadow_status",
    "stage2_shadow_validation",
    "leakage_validator",
    "bilingual_aliases",
    "macro_report_surface_validator",
    "latest_verified_production_baseline",
]

EXPECTED_SOURCE_EVIDENCE = {
    "promotion_bridge_design": "control/STAGE2_PROMOTION_BRIDGE_DESIGN.md",
    "review_schema": "schemas/stage2_promotion_review.schema.json",
    "review_checklist_validator": "tools/validate_stage2_promotion_review_checklist.py",
    "fixture_manifest": "fixtures/stage2_promotion_review/manifest.json",
    "fixture_validator": "tools/validate_stage2_promotion_review_fixtures.py",
    "decision_artifact_design": "control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md",
    "decision_artifact_design_validator": "tools/validate_stage2_promotion_review_decision_artifact_design.py",
    "stage2_shadow_status": "control/MACRO_STAGE2_CONFIRMATION_STATUS.md",
    "stage2_shadow_validation": "output/macro/validation/latest_stage2_confirmation_validation.json",
    "leakage_validator": "tools/validate_etf_macro_thesis_surface_leakage.py",
    "bilingual_aliases": "config/macro_thesis_bilingual_aliases.yml",
    "macro_report_surface_validator": "tools/validate_macro_report_surface.py",
    "latest_verified_production_baseline": "control/CURRENT_STATE.md",
}

FORBIDDEN_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (reason, re.compile(pattern, re.IGNORECASE))
    for reason, pattern in [
        ("raw Stage-1/Stage-2 status label", r"\bstage[_ -]?[12][a-z0-9_ -]*(?:candidate|fundable|confirmation|confirmed|status)\b"),
        ("raw driver plumbing label", r"\b(driver_id|driver_ids|active_drivers|driver_catalog|driver_beneficiary_map)\b"),
        ("raw shadow/internal label", r"\b(shadow_only|internal_only)\b"),
        (
            "forbidden promotional or readiness claim",
            r"\b(promoted|fundable|recommended|production[-_ ]?ready|client[-_ ]?facing|portfolio[-_ ]?action[-_ ]?ready|delivery[-_ ]?ready|execution[-_ ]?ready|trade[-_ ]?ready|buy|sell|allocate)\b",
        ),
    ]
)


@dataclass(frozen=True)
class DecisionSchemaFinding:
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


def _finding(field: str, value: Any, reason: str) -> DecisionSchemaFinding:
    return DecisionSchemaFinding(field=field, value=str(value), reason=reason)


def _raise_if_findings(findings: list[DecisionSchemaFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_DECISION_SCHEMA_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review decision schema validation failed: findings={len(findings)}")


def validate_schema_definition(schema: dict[str, Any]) -> None:
    findings: list[DecisionSchemaFinding] = []

    if schema.get("type") != "object":
        findings.append(_finding("schema.type", schema.get("type"), "schema root must be object"))
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
        findings.append(_finding("schema.properties", properties, "properties must be object"))
        _raise_if_findings(findings)
        return

    _validate_const(properties, findings, "schema_version", "1.0")
    _validate_const(properties, findings, "artifact_type", "stage2_promotion_review_decision")
    _validate_const(properties, findings, "decision_scope", "review_decision_only")

    decision_status = properties.get("decision_status") or {}
    enum = set(decision_status.get("enum") or []) if isinstance(decision_status, dict) else set()
    if enum != ALLOWED_DECISION_STATUSES:
        findings.append(_finding("schema.properties.decision_status.enum", sorted(enum), "decision_status enum must match allowed non-promotional statuses"))
    blocked = sorted(enum & FORBIDDEN_DECISION_STATUSES)
    if blocked:
        findings.append(_finding("schema.properties.decision_status.enum", blocked, "decision_status enum includes forbidden status"))

    _validate_object_required_consts(properties, findings, "authority", REQUIRED_AUTHORITY)
    _validate_object_required_strings(properties, findings, "source_evidence", REQUIRED_SOURCE_EVIDENCE)
    _validate_note_array(properties, findings, "decision_rationale")
    _validate_note_array(properties, findings, "blocking_conditions")
    _validate_note_array(properties, findings, "required_future_work")

    _raise_if_findings(findings)


def _validate_const(properties: dict[str, Any], findings: list[DecisionSchemaFinding], field: str, expected: Any) -> None:
    field_schema = properties.get(field) or {}
    if not isinstance(field_schema, dict) or field_schema.get("const") != expected:
        findings.append(_finding(f"schema.properties.{field}.const", field_schema, f"{field} must be const {expected!r}"))


def _validate_object_required_consts(properties: dict[str, Any], findings: list[DecisionSchemaFinding], field: str, required_consts: dict[str, Any]) -> None:
    obj = properties.get(field) or {}
    if not isinstance(obj, dict):
        findings.append(_finding(f"schema.properties.{field}", obj, f"{field} schema is required"))
        return
    if obj.get("additionalProperties") is not False:
        findings.append(_finding(f"schema.properties.{field}.additionalProperties", obj.get("additionalProperties"), f"{field} must be closed"))
    required = obj.get("required") or []
    props = obj.get("properties") or {}
    for key, expected in required_consts.items():
        if key not in required:
            findings.append(_finding(f"schema.{field}.required.{key}", required, f"{field}.{key} is not required"))
        key_schema = props.get(key) if isinstance(props, dict) else None
        if not isinstance(key_schema, dict) or key_schema.get("const") is not expected:
            findings.append(_finding(f"schema.{field}.{key}.const", key_schema, f"{field}.{key} must be const {expected!r}"))


def _validate_object_required_strings(properties: dict[str, Any], findings: list[DecisionSchemaFinding], field: str, required_strings: list[str]) -> None:
    obj = properties.get(field) or {}
    if not isinstance(obj, dict):
        findings.append(_finding(f"schema.properties.{field}", obj, f"{field} schema is required"))
        return
    if obj.get("additionalProperties") is not False:
        findings.append(_finding(f"schema.properties.{field}.additionalProperties", obj.get("additionalProperties"), f"{field} must be closed"))
    required = obj.get("required") or []
    props = obj.get("properties") or {}
    for key in required_strings:
        if key not in required:
            findings.append(_finding(f"schema.{field}.required.{key}", required, f"{field}.{key} is not required"))
        key_schema = props.get(key) if isinstance(props, dict) else None
        if not isinstance(key_schema, dict) or key_schema.get("type") != "string":
            findings.append(_finding(f"schema.{field}.{key}.type", key_schema, f"{field}.{key} must be string"))


def _validate_note_array(properties: dict[str, Any], findings: list[DecisionSchemaFinding], field: str) -> None:
    field_schema = properties.get(field) or {}
    if not isinstance(field_schema, dict) or field_schema.get("type") != "array":
        findings.append(_finding(f"schema.properties.{field}.type", field_schema, f"{field} must be array"))


def valid_artifact() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "stage2_promotion_review_decision",
        "generated_at_utc": "2026-06-17T00:00:00Z",
        "decision_status": "not_promoted",
        "decision_scope": "review_decision_only",
        "authority": dict(REQUIRED_AUTHORITY),
        "source_evidence": dict(EXPECTED_SOURCE_EVIDENCE),
        "decision_rationale": [
            {"code": "review_boundary", "severity": "info", "summary": "Decision record remains control-layer review only."}
        ],
        "blocking_conditions": [],
        "required_future_work": [
            {"code": "future_package", "severity": "info", "summary": "Separate schema, validator, and implementation work remain required before production use."}
        ],
        "non_goals": [
            "no report change",
            "no scoring change",
            "no capital action",
            "no delivery or run change",
            "no historical artifact change",
        ],
    }


def validate_artifact(payload: dict[str, Any], *, require_expected_sources: bool = False) -> None:
    findings: list[DecisionSchemaFinding] = []
    _validate_closed_object("", payload, REQUIRED_TOP_LEVEL, findings)

    if payload.get("schema_version") != "1.0":
        findings.append(_finding("schema_version", payload.get("schema_version"), "schema_version must be 1.0"))
    if payload.get("artifact_type") != "stage2_promotion_review_decision":
        findings.append(_finding("artifact_type", payload.get("artifact_type"), "artifact_type must be stage2_promotion_review_decision"))
    if payload.get("decision_scope") != "review_decision_only":
        findings.append(_finding("decision_scope", payload.get("decision_scope"), "decision_scope must be review_decision_only"))

    decision_status = payload.get("decision_status")
    if decision_status in FORBIDDEN_DECISION_STATUSES:
        findings.append(_finding("decision_status", decision_status, "forbidden promotional or action status"))
    elif decision_status not in ALLOWED_DECISION_STATUSES:
        findings.append(_finding("decision_status", decision_status, "unknown or non-review decision status"))

    authority = payload.get("authority")
    if not isinstance(authority, dict):
        findings.append(_finding("authority", authority, "authority block is required"))
    else:
        _validate_closed_object("authority", authority, list(REQUIRED_AUTHORITY), findings)
        for field, expected in REQUIRED_AUTHORITY.items():
            if authority.get(field) is not expected:
                findings.append(_finding(f"authority.{field}", authority.get(field), f"must be {expected!r}"))

    source_evidence = payload.get("source_evidence")
    if not isinstance(source_evidence, dict):
        findings.append(_finding("source_evidence", source_evidence, "source_evidence block is required"))
    else:
        _validate_closed_object("source_evidence", source_evidence, REQUIRED_SOURCE_EVIDENCE, findings)
        for field in REQUIRED_SOURCE_EVIDENCE:
            value = source_evidence.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(_finding(f"source_evidence.{field}", value, "source evidence reference must be a non-empty string"))
        if require_expected_sources:
            for field, expected in EXPECTED_SOURCE_EVIDENCE.items():
                if source_evidence.get(field) != expected:
                    findings.append(_finding(f"source_evidence.{field}", source_evidence.get(field), f"must be {expected!r}"))

    for list_field in ["decision_rationale", "blocking_conditions", "required_future_work"]:
        values = payload.get(list_field)
        if not isinstance(values, list):
            findings.append(_finding(list_field, values, "must be a list"))
            continue
        for idx, item in enumerate(values):
            if not isinstance(item, dict):
                findings.append(_finding(f"{list_field}[{idx}]", item, "must be an object"))
                continue
            _validate_closed_object(f"{list_field}[{idx}]", item, ["code", "severity", "summary"], findings)
            if item.get("severity") not in {"info", "warning", "blocker"}:
                findings.append(_finding(f"{list_field}[{idx}].severity", item.get("severity"), "severity must be info, warning, or blocker"))

    if not isinstance(payload.get("non_goals"), list):
        findings.append(_finding("non_goals", payload.get("non_goals"), "must be a list"))

    _validate_text_fields(payload, findings)
    _raise_if_findings(findings)


def _validate_closed_object(prefix: str, obj: dict[str, Any], allowed_fields: list[str], findings: list[DecisionSchemaFinding]) -> None:
    allowed = set(allowed_fields)
    for field in allowed_fields:
        if field not in obj:
            dotted = f"{prefix}.{field}" if prefix else field
            findings.append(_finding(dotted, "<missing>", "missing required field"))
    for field in obj:
        if field not in allowed:
            dotted = f"{prefix}.{field}" if prefix else field
            findings.append(_finding(dotted, obj.get(field), "additional property not allowed by closed schema"))


def _validate_text_fields(payload: dict[str, Any], findings: list[DecisionSchemaFinding]) -> None:
    text_buckets: list[tuple[str, str]] = []
    for list_field in ["decision_rationale", "blocking_conditions", "required_future_work"]:
        for idx, item in enumerate(payload.get(list_field) or []):
            if isinstance(item, dict):
                for field in ["code", "summary"]:
                    value = item.get(field)
                    if isinstance(value, str):
                        text_buckets.append((f"{list_field}[{idx}].{field}", value))
    for field, value in text_buckets:
        for reason, pattern in FORBIDDEN_TEXT_PATTERNS:
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
    validate_artifact(valid_artifact(), require_expected_sources=True)
    for artifact in args.artifact:
        validate_artifact(_load_json(artifact))
    print(f"STAGE2_PROMOTION_REVIEW_DECISION_SCHEMA_OK | schema={args.schema}")


if __name__ == "__main__":
    main()
