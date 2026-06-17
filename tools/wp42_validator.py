#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_DESIGN_PATH = Path("control/STAGE2_CONTROL_LAYER_PACKAGE_DESIGN.md")

REQUIRED_PHRASES = [
    "design-only",
    "No live decision artifact is created.",
    "No Stage-2 promotion is made.",
    "No production report authority is granted.",
    "No scoring authority is granted.",
    "No fundability authority is granted.",
    "No portfolio-action authority is granted.",
    "No delivery authority is granted.",
    "No execution authority is granted.",
    "No historical-output mutation authority is granted.",
    "A future explicit control-layer decision package is required.",
    "A separate future implementation package is required.",
    "must not rely on chat memory as source evidence",
]

REQUIRED_SECTIONS = [
    "## 1. Decision framework design",
    "## 2. Input/state contract design",
    "## 3. Output contract design",
    "## 4. Operational runbook design",
]

ALLOWED_STATUSES = {
    "not_promoted",
    "rejected_not_promoted",
    "blocked_missing_evidence",
    "blocked_by_authority_boundary",
    "ready_for_future_implementation_package_not_promoted",
}

FORBIDDEN_STATUSES = {
    "promoted_to_production",
    "promoted_to_report",
    "production_ready",
    "client_facing_ready",
    "fundable_ready",
    "portfolio_action_ready",
    "delivery_ready",
    "execution_ready",
    "trade_ready",
}

REQUIRED_EVIDENCE = [
    "control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md",
    "control/STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_ARTIFACT_DESIGN_REVIEW.md",
    "control/decision_records/stage2_promotion_review_decision_artifact_design_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_schema_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_fixtures_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_hardening_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_sample_gate_20260617.md",
    "control/decision_records/stage2_promotion_review_decision_dry_run_20260617.md",
    "control/decision_records/stage2_promotion_review_explicit_decision_design_review_20260617.md",
    "control/decision_records/stage2_decision_non_production_fixture_gate_20260617.md",
    "schemas/stage2_promotion_review_decision.schema.json",
    "fixtures/stage2_promotion_review_decision/manifest.json",
    "tools/validate_stage2_promotion_review_decision_schema.py",
    "tools/validate_stage2_promotion_review_decision_fixtures.py",
    "tools/validate_stage2_promotion_review_decision_hardening.py",
    "tools/validate_stage2_promotion_review_decision_sample_gate.py",
    "tools/validate_stage2_promotion_review_decision_dry_run.py",
    "tools/validate_stage2_promotion_review_explicit_decision_design_review.py",
    "tools/wp41_validator.py",
    "control/CURRENT_STATE.md",
    "control/NEXT_ACTIONS.md",
]

REQUIRED_AUTHORITY_DEFAULTS = [
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
    "decision_artifact_only: true",
    "implementation_required_before_production_use: true",
    "explicit_control_layer_decision_required: true",
]


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
            "STAGE2_PROMOTION_REVIEW_EXPLICIT_CONTROL_LAYER_DECISION_PACKAGE_DESIGN_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 explicit control-layer decision package design failed: findings={len(findings)}")


def _read(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"control-layer design document is missing: {path}")
    return path.read_text(encoding="utf-8")


def _block_text(text: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}:\n\n```text\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else ""


def _iter_lines(block: str) -> Iterable[str]:
    for line in block.splitlines():
        line = line.strip()
        if line:
            yield line


def validate_text(text: str, *, path: Path = DEFAULT_DESIGN_PATH) -> None:
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
    for authority in REQUIRED_AUTHORITY_DEFAULTS:
        if authority not in text:
            findings.append(_finding("authority_default", authority, "missing required authority default"))

    allowed_block = _block_text(text, "Allowed future decision package statuses")
    allowed_lines = set(_iter_lines(allowed_block))
    if allowed_lines != ALLOWED_STATUSES:
        findings.append(_finding("allowed_statuses", sorted(allowed_lines), "allowed statuses must exactly match contract"))
    forbidden_block = _block_text(text, "Forbidden future decision package statuses")
    forbidden_lines = set(_iter_lines(forbidden_block))
    if forbidden_lines != FORBIDDEN_STATUSES:
        findings.append(_finding("forbidden_statuses", sorted(forbidden_lines), "forbidden statuses must exactly match contract"))
    overlap = allowed_lines & FORBIDDEN_STATUSES
    if overlap:
        findings.append(_finding("allowed_statuses", sorted(overlap), "forbidden status used as allowed status"))

    if "write target" in text and "output/" in text:
        findings.append(_finding("output_write_target", "output/", "must not reference output as a write target"))
    lower = text.lower()
    if "inbox receipt" in lower and "not inbox receipt" not in lower and "no delivery or inbox receipt is claimed" not in lower:
        findings.append(_finding("delivery_receipt", "inbox receipt", "must not claim inbox receipt"))
    if "rely on chat memory" in lower and "must not rely on chat memory" not in lower:
        findings.append(_finding("chat_memory", "chat memory", "must not rely on chat memory"))

    _raise_if_findings(findings)


def validate_file(path: Path = DEFAULT_DESIGN_PATH) -> None:
    validate_text(_read(path), path=path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=DEFAULT_DESIGN_PATH)
    args = parser.parse_args()
    validate_file(args.file)
    print(f"STAGE2_PROMOTION_REVIEW_EXPLICIT_CONTROL_LAYER_DECISION_PACKAGE_DESIGN_OK | file={args.file}")


if __name__ == "__main__":
    main()
