#!/usr/bin/env python3
"""Validate Stage-2 promotion review checklist readiness.

WP32 is review-checklist validation only. It validates whether a future
Stage-2 promotion review artifact has complete review evidence while preserving
not-promoted status and no production authority.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_schema as schema_validator

DEFAULT_SCHEMA_PATH = Path("schemas/stage2_promotion_review.schema.json")

CHECKLIST_STATUS_BY_REVIEW_STATUS = {
    "eligible_for_promotion_review_not_promoted": "checklist_ready_for_review_not_promoted",
    "not_ready_missing_evidence": "checklist_not_ready_missing_evidence",
    "blocked_by_authority_boundary": "checklist_blocked_by_authority_boundary",
    "rejected_by_review_not_promoted": "checklist_rejected_not_promoted",
}

REQUIRED_AUTHORITY = schema_validator.REQUIRED_AUTHORITY
REQUIRED_SOURCE_ARTIFACTS = schema_validator.REQUIRED_SOURCE_ARTIFACTS
ALLOWED_REVIEW_STATUSES = schema_validator.ALLOWED_REVIEW_STATUSES
FORBIDDEN_STATUSES = schema_validator.FORBIDDEN_STATUSES | {
    "trade_ready",
}

FORBIDDEN_REVIEW_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (reason, re.compile(pattern, re.IGNORECASE))
    for reason, pattern in [
        (
            "forbidden promotional or readiness claim",
            r"\b(promoted|fundable|recommended|client[-_ ]?facing|portfolio[-_ ]?action[-_ ]?ready|production[-_ ]?ready|delivery[-_ ]?ready|execution[-_ ]?ready|trade[-_ ]?ready|buy|sell|allocate)\b",
        ),
        (
            "raw Stage-1/Stage-2 status label",
            r"\bstage[_ -]?[12][a-z0-9_ -]*(?:candidate|fundable|confirmation|confirmed)\b",
        ),
        (
            "raw driver plumbing label",
            r"\b(driver_id|driver_ids|active_drivers|driver_catalog|driver_beneficiary_map)\b",
        ),
        (
            "raw shadow/internal label",
            r"\b(shadow_only|internal_only)\b",
        ),
    ]
)


@dataclass(frozen=True)
class ChecklistFinding:
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


def _finding(field: str, value: Any, reason: str) -> ChecklistFinding:
    return ChecklistFinding(field=field, value=str(value), reason=reason)


def _raise_if_findings(findings: list[ChecklistFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_CHECKLIST_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review checklist validation failed: findings={len(findings)}")


def valid_artifact() -> dict[str, Any]:
    payload = copy.deepcopy(schema_validator.valid_artifact())
    payload["non_goals"] = [
        "review-only validation",
        "no production report change",
        "no scoring change",
        "no position action",
        "no delivery or execution change",
    ]
    return payload


def validate_checklist(payload: dict[str, Any], *, schema_path: Path = DEFAULT_SCHEMA_PATH) -> str:
    findings: list[ChecklistFinding] = []

    try:
        schema_validator.validate_schema_file(schema_path)
        schema_validator.validate_artifact(payload)
    except Exception as exc:  # noqa: BLE001 - convert schema detail into checklist finding output.
        findings.append(_finding("schema_validation", "<invalid>", str(exc)))

    if payload.get("artifact_type") != "stage2_promotion_review":
        findings.append(_finding("artifact_type", payload.get("artifact_type"), "artifact_type must be stage2_promotion_review"))

    if payload.get("promotion_status") != "not_promoted":
        findings.append(_finding("promotion_status", payload.get("promotion_status"), "promotion_status must remain not_promoted"))

    review_status = payload.get("review_status")
    if review_status in FORBIDDEN_STATUSES:
        findings.append(_finding("review_status", review_status, "forbidden promotional status"))
    elif review_status not in ALLOWED_REVIEW_STATUSES:
        findings.append(_finding("review_status", review_status, "unknown or non-review status"))

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

    missing_requirements = payload.get("missing_requirements")
    if review_status == "eligible_for_promotion_review_not_promoted" and missing_requirements not in ([], None):
        findings.append(_finding("missing_requirements", missing_requirements, "eligible review artifacts must not list missing requirements"))
    if review_status == "not_ready_missing_evidence" and missing_requirements == []:
        findings.append(_finding("missing_requirements", missing_requirements, "not-ready review artifacts must explain missing evidence"))

    _validate_review_text(payload, findings)
    _raise_if_findings(findings)
    return CHECKLIST_STATUS_BY_REVIEW_STATUS.get(str(review_status), "checklist_rejected_not_promoted")


def _validate_review_text(payload: dict[str, Any], findings: list[ChecklistFinding]) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--artifact", type=Path, default=None)
    args = parser.parse_args()

    artifact_label = str(args.artifact) if args.artifact else "self_test"
    payload = _load_json(args.artifact) if args.artifact else valid_artifact()
    checklist_status = validate_checklist(payload, schema_path=args.schema)
    print(f"STAGE2_PROMOTION_REVIEW_CHECKLIST_OK | artifact={artifact_label} | checklist_status={checklist_status}")


if __name__ == "__main__":
    main()
