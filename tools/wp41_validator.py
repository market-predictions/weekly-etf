#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_decision_schema as schema_validator
from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_sample_gate as sample_gate
from tools import validate_stage2_promotion_review_decision_dry_run as dry_run_validator
from tools import validate_stage2_promotion_review_explicit_decision_design_review as design_review_validator
from tools import wp41_builder as builder


@dataclass(frozen=True)
class Finding:
    field: str
    value: str
    reason: str


def _finding(field: str, value: Any, reason: str) -> Finding:
    return Finding(field, str(value), reason)


def _raise_if_findings(findings: list[Finding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_DECISION_NON_PRODUCTION_FIXTURE_GATE_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 decision artifact non-production fixture gate failed: findings={len(findings)}")


def validate_fixture_candidate(artifact: dict[str, Any]) -> None:
    findings: list[Finding] = []
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            schema_validator.validate_artifact(artifact, require_expected_sources=True)
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("schema", "artifact", f"schema validation failed: {exc}"))
        try:
            hardening._validate_hardened_artifact(artifact)
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("hardening", "artifact", f"hardening validation failed: {exc}"))
        try:
            sample_gate.validate_sample(artifact)
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("sample_gate", "artifact", f"sample gate validation failed: {exc}"))
        try:
            dry_run_validator.validate_dry_run_artifact(artifact)
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("dry_run", "artifact", f"dry-run validation failed: {exc}"))
        try:
            design_review_validator.validate_file()
        except Exception as exc:  # noqa: BLE001
            findings.append(_finding("design_review", "document", f"design review validation failed: {exc}"))

    if artifact.get("generated_at_utc") != builder.DETERMINISTIC_GENERATED_AT_UTC:
        findings.append(_finding("generated_at_utc", artifact.get("generated_at_utc"), "must be deterministic timestamp"))
    if artifact.get("decision_status") != "not_promoted":
        findings.append(_finding("decision_status", artifact.get("decision_status"), "must be not_promoted"))
    if artifact.get("authority") != schema_validator.REQUIRED_AUTHORITY:
        findings.append(_finding("authority", artifact.get("authority"), "must exactly match required authority block"))
    if artifact.get("source_evidence") != schema_validator.EXPECTED_SOURCE_EVIDENCE:
        findings.append(_finding("source_evidence", artifact.get("source_evidence"), "must exactly match expected source evidence"))
    allowed_top = set(schema_validator.REQUIRED_TOP_LEVEL)
    for key in artifact:
        if key not in allowed_top:
            findings.append(_finding(key, artifact.get(key), "unexpected top-level field"))
    _raise_if_findings(findings)


def validate_no_default_write() -> None:
    root = builder.APPROVED_ROOT
    before = set(root.glob("*.json")) if root.exists() else set()
    _ = builder.build_fixture_candidate()
    after = set(root.glob("*.json")) if root.exists() else set()
    if before != after:
        raise RuntimeError("fixture builder wrote a file by default")


def validate_unsafe_paths() -> None:
    for path in [
        Path("output/non-production.json"),
        Path("runtime/non-production.json"),
        Path("portfolio/non-production.json"),
        Path("reports/non-production.json"),
        Path("delivery/non-production.json"),
        Path("../non-production.json"),
        Path("/tmp/non-production.json"),
    ]:
        try:
            builder.validate_write_path(path)
        except ValueError:
            continue
        raise RuntimeError(f"unsafe write path was accepted: {path}")


def validate_written_fixture(path: Path) -> None:
    expected = builder.build_fixture_candidate()
    actual = json.loads(path.read_text(encoding="utf-8"))
    if actual != expected:
        raise RuntimeError(f"written fixture does not match in-memory candidate: {path}")


def run_fixture_gate() -> None:
    validate_no_default_write()
    validate_unsafe_paths()
    validate_fixture_candidate(builder.build_fixture_candidate())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    run_fixture_gate()
    print("STAGE2_PROMOTION_REVIEW_DECISION_NON_PRODUCTION_FIXTURE_GATE_OK")


if __name__ == "__main__":
    main()
