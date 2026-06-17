#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import contextlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import build_stage2_promotion_review_decision_sample as builder
from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_schema as schema_validator

EXPECTED_TIMESTAMP = builder.DETERMINISTIC_GENERATED_AT_UTC


@dataclass(frozen=True)
class SampleGateFinding:
    field: str
    value: str
    reason: str


def _finding(field: str, value: Any, reason: str) -> SampleGateFinding:
    return SampleGateFinding(field, str(value), reason)


def _raise_if_findings(findings: list[SampleGateFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_DECISION_SAMPLE_GATE_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review decision sample gate failed: findings={len(findings)}")


def validate_sample(sample: dict[str, Any]) -> None:
    findings: list[SampleGateFinding] = []
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            schema_validator.validate_artifact(sample, require_expected_sources=True)
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("schema", "sample", f"schema validation failed: {exc}"))
        try:
            hardening._validate_hardened_artifact(sample)
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("hardening", "sample", f"hardening validation failed: {exc}"))

    if sample.get("generated_at_utc") != EXPECTED_TIMESTAMP:
        findings.append(_finding("generated_at_utc", sample.get("generated_at_utc"), f"must be {EXPECTED_TIMESTAMP}"))
    if sample.get("decision_status") != "not_promoted":
        findings.append(_finding("decision_status", sample.get("decision_status"), "must be not_promoted"))
    if sample.get("decision_scope") != "review_decision_only":
        findings.append(_finding("decision_scope", sample.get("decision_scope"), "must be review_decision_only"))
    if sample.get("authority") != schema_validator.REQUIRED_AUTHORITY:
        findings.append(_finding("authority", sample.get("authority"), "must exactly match required authority block"))
    if sample.get("source_evidence") != schema_validator.EXPECTED_SOURCE_EVIDENCE:
        findings.append(_finding("source_evidence", sample.get("source_evidence"), "must exactly match expected source evidence"))

    allowed_top = set(schema_validator.REQUIRED_TOP_LEVEL)
    for key in sample:
        if key not in allowed_top:
            findings.append(_finding(key, sample.get(key), "unexpected top-level field"))

    _raise_if_findings(findings)


def validate_no_default_write() -> None:
    before = set(builder.ALLOWED_WRITE_ROOT.glob("*.json")) if builder.ALLOWED_WRITE_ROOT.exists() else set()
    _ = builder.build_sample()
    after = set(builder.ALLOWED_WRITE_ROOT.glob("*.json")) if builder.ALLOWED_WRITE_ROOT.exists() else set()
    if before != after:
        raise RuntimeError("sample builder wrote a file by default")


def validate_unsafe_paths() -> None:
    for path in [Path("output/sample.json"), Path("../sample.json"), Path("/tmp/sample.json")]:
        try:
            builder.validate_write_path(path)
        except ValueError:
            continue
        raise RuntimeError(f"unsafe write path was accepted: {path}")


def run_sample_gate() -> None:
    validate_no_default_write()
    validate_unsafe_paths()
    validate_sample(builder.build_sample())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    run_sample_gate()
    print("STAGE2_PROMOTION_REVIEW_DECISION_SAMPLE_GATE_OK")


if __name__ == "__main__":
    main()
