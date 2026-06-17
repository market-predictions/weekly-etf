#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import build_stage2_promotion_review_decision_dry_run as builder
from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_sample_gate as sample_gate
from tools import validate_stage2_promotion_review_decision_schema as schema_validator


@dataclass(frozen=True)
class DryRunFinding:
    field: str
    value: str
    reason: str


def _finding(field: str, value: Any, reason: str) -> DryRunFinding:
    return DryRunFinding(field, str(value), reason)


def _raise_if_findings(findings: list[DryRunFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_DECISION_DRY_RUN_FINDING | "
            f"field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review decision dry-run validation failed: findings={len(findings)}")


def validate_dry_run_artifact(artifact: dict[str, Any]) -> None:
    findings: list[DryRunFinding] = []
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
    root = builder.ALLOWED_WRITE_ROOT
    before = set(root.glob("*.json")) if root.exists() else set()
    _ = builder.build_dry_run()
    after = set(root.glob("*.json")) if root.exists() else set()
    if before != after:
        raise RuntimeError("dry-run builder wrote a file by default")


def validate_unsafe_paths() -> None:
    for path in [
        Path("output/dry-run.json"),
        Path("runtime/dry-run.json"),
        Path("portfolio/dry-run.json"),
        Path("reports/dry-run.json"),
        Path("delivery/dry-run.json"),
        Path("../dry-run.json"),
        Path("/tmp/dry-run.json"),
    ]:
        try:
            builder.validate_write_path(path)
        except ValueError:
            continue
        raise RuntimeError(f"unsafe write path was accepted: {path}")


def run_dry_run_validator() -> None:
    validate_no_default_write()
    validate_unsafe_paths()
    validate_dry_run_artifact(builder.build_dry_run())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    run_dry_run_validator()
    print("STAGE2_PROMOTION_REVIEW_DECISION_DRY_RUN_OK")


if __name__ == "__main__":
    main()
