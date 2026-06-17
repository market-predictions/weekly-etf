#!/usr/bin/env python3
"""Run WP37 hardening checks for Stage-2 promotion review decision validators.

This is validator-hardening only. It creates no live decision artifacts and grants
no production authority.
"""

from __future__ import annotations

import argparse
import copy
import contextlib
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_decision_fixtures as fixture_validator
from tools import validate_stage2_promotion_review_decision_schema as schema_validator

UTC_LIKE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


@dataclass(frozen=True)
class HardeningFinding:
    check: str
    detail: str


def _capture_failure(fn: Callable[[], None]) -> str:
    with contextlib.redirect_stdout(io.StringIO()) as stdout_buffer:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            return f"{stdout_buffer.getvalue()}\n{exc}"
    return stdout_buffer.getvalue()


def _expect_failure(check: str, fn: Callable[[], None], expected_text: str, findings: list[HardeningFinding]) -> None:
    output = _capture_failure(fn)
    if expected_text not in output:
        findings.append(HardeningFinding(check, f"expected failure text not found: {expected_text!r}; output={output!r}"))


def _base_artifact() -> dict[str, Any]:
    return copy.deepcopy(schema_validator.valid_artifact())


def _validate_hardened_artifact(payload: dict[str, Any], *, require_expected_sources: bool = True) -> None:
    extra_findings: list[schema_validator.DecisionSchemaFinding] = []
    generated_at = payload.get("generated_at_utc")
    if not isinstance(generated_at, str) or not UTC_LIKE_PATTERN.fullmatch(generated_at):
        extra_findings.append(schema_validator._finding("generated_at_utc", generated_at, "generated_at_utc must be UTC-like YYYY-MM-DDTHH:MM:SSZ"))

    source_evidence = payload.get("source_evidence")
    if isinstance(source_evidence, dict):
        for field, value in source_evidence.items():
            if isinstance(value, str):
                path = Path(value)
                if path.is_absolute() or any(part == ".." for part in path.parts):
                    extra_findings.append(schema_validator._finding(f"source_evidence.{field}", value, "source evidence path must be relative and must not contain traversal"))
                if path.parts and path.parts[0] == "output" and field != "stage2_shadow_validation":
                    extra_findings.append(schema_validator._finding(f"source_evidence.{field}", value, "source evidence may not reference output for this field"))
    schema_validator.validate_artifact(payload, require_expected_sources=require_expected_sources)
    schema_validator._raise_if_findings(extra_findings)


def _validate_hardened_manifest(manifest: dict[str, Any]) -> None:
    findings: list[fixture_validator.FixtureFinding] = []
    entries = manifest.get("fixtures")
    if isinstance(entries, list):
        for index, entry in enumerate(entries):
            if isinstance(entry, dict):
                allowed = {"path", "expected", "expected_decision_status", "expected_failure_contains"}
                for key in entry:
                    if key not in allowed:
                        findings.append(fixture_validator._finding(f"manifest.fixtures[{index}]", key, entry.get(key), "unexpected manifest entry key"))
    fixture_validator.validate_manifest_payload(manifest)
    fixture_validator._raise_if_findings(findings)


def run_hardening_checks() -> None:
    findings: list[HardeningFinding] = []

    artifact = _base_artifact()
    artifact["authority"]["extra"] = False
    _expect_failure("authority_extra", lambda: _validate_hardened_artifact(artifact), "additional property", findings)

    artifact = _base_artifact()
    artifact["source_evidence"]["extra"] = "control/extra.md"
    _expect_failure("source_extra", lambda: _validate_hardened_artifact(artifact), "additional property", findings)

    artifact = _base_artifact()
    artifact["decision_rationale"][0]["extra"] = "x"
    _expect_failure("note_extra", lambda: _validate_hardened_artifact(artifact), "additional property", findings)

    artifact = _base_artifact()
    artifact["decision_rationale"] = ["not-an-object"]
    _expect_failure("note_non_object", lambda: _validate_hardened_artifact(artifact), "must be an object", findings)

    artifact = _base_artifact()
    artifact["decision_rationale"][0]["severity"] = "critical"
    _expect_failure("bad_severity", lambda: _validate_hardened_artifact(artifact), "severity must be", findings)

    artifact = _base_artifact()
    artifact["authority"]["delivery_authority"] = "false"
    _expect_failure("authority_string", lambda: _validate_hardened_artifact(artifact), "authority.delivery_authority", findings)

    artifact = _base_artifact()
    artifact["decision_status"] = " Not_Promoted "
    _expect_failure("status_case_space", lambda: _validate_hardened_artifact(artifact), "decision_status", findings)

    artifact = _base_artifact()
    artifact["source_evidence"]["review_schema"] = "../schemas/stage2_promotion_review.schema.json"
    _expect_failure("source_traversal", lambda: _validate_hardened_artifact(artifact), "source_evidence.review_schema", findings)

    artifact = _base_artifact()
    artifact["generated_at_utc"] = "2026-06-17 00:00:00"
    _expect_failure("bad_generated_at", lambda: _validate_hardened_artifact(artifact), "generated_at_utc", findings)

    manifest = {
        "schema_version": "1.0",
        "fixture_set": "stage2_promotion_review_decision",
        "authority": dict(fixture_validator.REQUIRED_MANIFEST_AUTHORITY),
        "fixtures": [{"path": "fixtures/stage2_promotion_review_decision/pass_not_promoted.json", "expected": "pass", "expected_decision_status": "not_promoted", "extra": "x"}],
    }
    _expect_failure("manifest_entry_extra", lambda: _validate_hardened_manifest(manifest), "unexpected manifest entry key", findings)

    if findings:
        for finding in findings:
            print(f"STAGE2_PROMOTION_REVIEW_DECISION_HARDENING_FINDING | check={finding.check} | detail={finding.detail}")
        raise RuntimeError(f"Stage-2 promotion review decision hardening failed: findings={len(findings)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    run_hardening_checks()
    print("STAGE2_PROMOTION_REVIEW_DECISION_HARDENING_OK")


if __name__ == "__main__":
    main()
