#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_REVIEW_PATH = Path("control/STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_ARTIFACT_DESIGN_REVIEW.md")

REQUIRED_PHRASES = [
    "review-only",
    "No live decision artifact is created.",
    "No Stage-2 promotion is made.",
    "No production report authority is granted.",
    "No scoring authority is granted.",
    "No fundability authority is granted.",
    "No portfolio-action authority is granted.",
    "No delivery authority is granted.",
    "No execution authority is granted.",
    "No historical-output mutation authority is granted.",
    "future explicit control-layer decision",
    "separate future implementation package",
]

REQUIRED_SECTIONS = [
    "## 1. Decision framework review",
    "## 2. Input/state contract review",
    "## 3. Output contract review",
    "## 4. Operational runbook review",
]

REQUIRED_EVIDENCE = [
    "control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md",
    "schemas/stage2_promotion_review_decision.schema.json",
    "fixtures/stage2_promotion_review_decision/manifest.json",
    "tools/validate_stage2_promotion_review_decision_schema.py",
    "tools/validate_stage2_promotion_review_decision_fixtures.py",
    "tools/validate_stage2_promotion_review_decision_hardening.py",
    "tools/build_stage2_promotion_review_decision_sample.py",
    "tools/validate_stage2_promotion_review_decision_sample_gate.py",
    "tools/build_stage2_promotion_review_decision_dry_run.py",
    "tools/validate_stage2_promotion_review_decision_dry_run.py",
    "control/decision_records/stage2_promotion_review_decision_artifact_design_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_schema_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_fixtures_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_hardening_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_sample_gate_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_dry_run_20260617.md",
    "control/CURRENT_STATE.md",
]

REQUIRED_OUTCOMES = [
    "decision_artifact_design_reviewed: true",
    "schema_reviewed: true",
    "fixture_chain_reviewed: true",
    "hardening_reviewed: true",
    "sample_gate_reviewed: true",
    "dry_run_builder_reviewed: true",
    "production_authority_granted: false",
    "stage2_promoted: false",
    "future_explicit_control_layer_decision_required: true",
    "separate_future_implementation_package_required: true",
]

ALLOWED_REVIEW_STATUSES = {
    "design_review_complete_not_promoted",
    "blocked_missing_evidence",
    "blocked_by_authority_boundary",
    "ready_for_future_explicit_decision_package_not_promoted",
}

FORBIDDEN_REVIEW_STATUSES = {
    "promoted",
    "fundable",
    "recommended",
    "production_ready",
    "client_facing",
    "portfolio_action_ready",
    "delivery_ready",
    "execution_ready",
    "trade_ready",
    "buy",
    "sell",
    "allocate",
}


@dataclass(frozen=True)
class Finding:
    field: str
    value: str
    reason: str


def _finding(field: str, value: object, reason: str) -> Finding:
    return Finding(field, str(value), reason)


def _raise_if_findings(findings: list[Finding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_DESIGN_REVIEW_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review explicit decision design review failed: findings={len(findings)}")


def _read(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"design review document is missing: {path}")
    return path.read_text(encoding="utf-8")


def _review_statuses(text: str) -> Iterable[str]:
    for match in re.finditer(r"^review_status:\s*([^\s]+)\s*$", text, re.MULTILINE):
        yield match.group(1)


def validate_text(text: str, *, path: Path = DEFAULT_REVIEW_PATH) -> None:
    findings: list[Finding] = []
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            findings.append(_finding("required_phrase", phrase, "missing required phrase"))
    for section in REQUIRED_SECTIONS:
        if section not in text:
            findings.append(_finding("section", section, "missing required four-layer section"))
    for evidence in REQUIRED_EVIDENCE:
        if evidence not in text:
            findings.append(_finding("evidence", evidence, "missing required evidence reference"))
    for outcome in REQUIRED_OUTCOMES:
        if outcome not in text:
            findings.append(_finding("review_outcome", outcome, "missing required review outcome"))

    statuses = list(_review_statuses(text))
    if not statuses:
        findings.append(_finding("review_status", "<missing>", "missing review_status outcome"))
    for status in statuses:
        if status not in ALLOWED_REVIEW_STATUSES:
            findings.append(_finding("review_status", status, "status is not an allowed non-promotional review outcome"))
        if status in FORBIDDEN_REVIEW_STATUSES:
            findings.append(_finding("review_status", status, "forbidden status"))

    if "write target" in text and "output/" in text:
        findings.append(_finding("output_write_target", "output/", "must not reference output as a write target"))
    if "inbox receipt" in text.lower() and "not claimed" not in text.lower() and "no delivery or inbox receipt is claimed" not in text.lower():
        findings.append(_finding("delivery_receipt", "inbox receipt", "must not claim inbox receipt"))

    _raise_if_findings(findings)


def validate_file(path: Path = DEFAULT_REVIEW_PATH) -> None:
    validate_text(_read(path), path=path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args()
    validate_file(args.file)
    print(f"STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_DESIGN_REVIEW_OK | file={args.file}")


if __name__ == "__main__":
    main()
