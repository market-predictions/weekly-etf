#!/usr/bin/env python3
"""Validate Stage-2 promotion review decision fixture manifest and replay.

WP36 is validator-fixture / sample-fixture validation only. It must not create
live decision artifacts, promote Stage-2 output, or grant production authority.
"""

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

from tools import validate_stage2_promotion_review_decision_schema as decision_validator

DEFAULT_MANIFEST_PATH = Path("fixtures/stage2_promotion_review_decision/manifest.json")
FIXTURE_ROOT = Path("fixtures/stage2_promotion_review_decision")
ALLOWED_EXPECTED = {"pass", "fail"}

REQUIRED_MANIFEST_AUTHORITY = {
    "fixture_only": True,
    "production_artifact": False,
    "client_facing_authority": False,
    "production_report_narrative_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
    "portfolio_action_authority": False,
    "delivery_authority": False,
    "execution_authority": False,
    "historical_output_mutation": False,
}


@dataclass(frozen=True)
class FixtureFinding:
    fixture: str
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


def _finding(fixture: Any, field: str, value: Any, reason: str) -> FixtureFinding:
    return FixtureFinding(str(fixture), field, str(value), reason)


def _raise_if_findings(findings: list[FixtureFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_DECISION_FIXTURE_FINDING | "
            f"fixture={finding.fixture} | field={finding.field} | value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review decision fixture validation failed: findings={len(findings)}")


def _resolve_manifest_base(manifest_path: Path) -> Path:
    if manifest_path == DEFAULT_MANIFEST_PATH:
        return Path(".")
    if manifest_path.parent.name == FIXTURE_ROOT.name:
        return manifest_path.parent.parent.parent
    return manifest_path.parent


def _fixture_path_is_safe(path_value: str) -> bool:
    path = Path(path_value)
    if path.is_absolute():
        return False
    if any(part == ".." for part in path.parts):
        return False
    if path.parts and path.parts[0] == "output":
        return False
    return path == FIXTURE_ROOT or path.is_relative_to(FIXTURE_ROOT)


def validate_manifest_payload(manifest: dict[str, Any], *, manifest_path: Path = DEFAULT_MANIFEST_PATH) -> None:
    findings: list[FixtureFinding] = []

    if manifest.get("schema_version") != "1.0":
        findings.append(_finding("manifest", "schema_version", manifest.get("schema_version"), "schema_version must be 1.0"))
    if manifest.get("fixture_set") != "stage2_promotion_review_decision":
        findings.append(_finding("manifest", "fixture_set", manifest.get("fixture_set"), "fixture_set must be stage2_promotion_review_decision"))

    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        findings.append(_finding("manifest", "authority", authority, "authority block is required"))
    else:
        for field, expected in REQUIRED_MANIFEST_AUTHORITY.items():
            if authority.get(field) is not expected:
                findings.append(_finding("manifest", f"authority.{field}", authority.get(field), f"must be {expected!r}"))

    entries = manifest.get("fixtures")
    if not isinstance(entries, list) or not entries:
        findings.append(_finding("manifest", "fixtures", entries, "fixtures must be a non-empty list"))
        _raise_if_findings(findings)
        return

    seen_paths: set[str] = set()
    base = _resolve_manifest_base(manifest_path)

    for index, entry in enumerate(entries):
        fixture_label = f"manifest.fixtures[{index}]"
        if not isinstance(entry, dict):
            findings.append(_finding(fixture_label, "entry", entry, "fixture entry must be an object"))
            continue

        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            findings.append(_finding(fixture_label, "path", path_value, "fixture path must be a non-empty string"))
            continue
        if path_value in seen_paths:
            findings.append(_finding(path_value, "path", path_value, "duplicate fixture path"))
        seen_paths.add(path_value)
        if not _fixture_path_is_safe(path_value):
            findings.append(_finding(path_value, "path", path_value, "fixture path must stay under fixtures/stage2_promotion_review_decision and not reference output/"))
            continue

        expected = entry.get("expected")
        if expected not in ALLOWED_EXPECTED:
            findings.append(_finding(path_value, "expected", expected, "expected must be pass or fail"))
            continue

        fixture_path = base / path_value
        if not fixture_path.exists():
            findings.append(_finding(path_value, "path", path_value, "fixture file does not exist"))
            continue

        if expected == "pass":
            expected_status = entry.get("expected_decision_status")
            if expected_status not in decision_validator.ALLOWED_DECISION_STATUSES:
                findings.append(_finding(path_value, "expected_decision_status", expected_status, "unknown expected decision status"))
                continue
            findings.extend(_validate_pass_fixture(fixture_path, path_value, expected_status))
        else:
            expected_contains = entry.get("expected_failure_contains")
            if not isinstance(expected_contains, str) or not expected_contains.strip():
                findings.append(_finding(path_value, "expected_failure_contains", expected_contains, "fail fixtures must declare expected failure text"))
                continue
            findings.extend(_validate_fail_fixture(fixture_path, path_value, expected_contains))

    _raise_if_findings(findings)


def _validate_pass_fixture(fixture_path: Path, label: str, expected_status: str) -> list[FixtureFinding]:
    findings: list[FixtureFinding] = []
    try:
        payload = _load_json(fixture_path)
        decision_validator.validate_artifact(payload, require_expected_sources=True)
    except Exception as exc:  # noqa: BLE001
        findings.append(_finding(label, "fixture", "pass", f"expected pass but validation failed: {exc}"))
        return findings
    if payload.get("decision_status") != expected_status:
        findings.append(_finding(label, "decision_status", payload.get("decision_status"), f"expected {expected_status}"))
    return findings


def _validate_fail_fixture(fixture_path: Path, label: str, expected_contains: str) -> list[FixtureFinding]:
    findings: list[FixtureFinding] = []
    try:
        payload = _load_json(fixture_path)
        with contextlib.redirect_stdout(io.StringIO()) as stdout_buffer:
            decision_validator.validate_artifact(payload, require_expected_sources=True)
        output = stdout_buffer.getvalue()
    except Exception as exc:  # noqa: BLE001
        output = stdout_buffer.getvalue() if "stdout_buffer" in locals() else ""
        combined = f"{output}\n{exc}"
        if expected_contains not in combined:
            findings.append(_finding(label, "expected_failure_contains", expected_contains, "expected failure text not found"))
        return findings
    findings.append(_finding(label, "expected", "fail", f"expected fail but validation passed with output {output!r}"))
    return findings


def validate_manifest_file(path: Path = DEFAULT_MANIFEST_PATH) -> None:
    validate_manifest_payload(_load_json(path), manifest_path=path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args()

    validate_manifest_file(args.manifest)
    print(f"STAGE2_PROMOTION_REVIEW_DECISION_FIXTURES_OK | manifest={args.manifest}")


if __name__ == "__main__":
    main()
