#!/usr/bin/env python3
"""Validate Stage-2 promotion review fixture manifest and fixture replay.

WP33 is fixture-set design and validation only. It must not create live
production promotion artifacts or grant production authority.
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

from tools import validate_stage2_promotion_review_checklist as checklist_validator
from tools import validate_stage2_promotion_review_schema as schema_validator

DEFAULT_MANIFEST_PATH = Path("fixtures/stage2_promotion_review/manifest.json")
FIXTURE_ROOT = Path("fixtures/stage2_promotion_review")
ALLOWED_EXPECTED = {"pass", "fail"}
ALLOWED_CHECKLIST_STATUSES = set(checklist_validator.CHECKLIST_STATUS_BY_REVIEW_STATUS.values())

REQUIRED_AUTHORITY = {
    "fixture_only": True,
    "production_artifact": False,
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


@dataclass(frozen=True)
class FixtureFinding:
    fixture: str
    field: str
    reason: str


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"JSON file does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON file must contain an object: {path}")
    return payload


def _finding(fixture: Any, field: str, reason: str) -> FixtureFinding:
    return FixtureFinding(str(fixture), field, reason)


def _raise_if_findings(findings: list[FixtureFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "STAGE2_PROMOTION_REVIEW_FIXTURE_FINDING | "
            f"fixture={finding.fixture} | field={finding.field} | reason={finding.reason}"
        )
    raise RuntimeError(f"Stage-2 promotion review fixture validation failed: findings={len(findings)}")


def _resolve_manifest_base(manifest_path: Path) -> Path:
    if manifest_path == DEFAULT_MANIFEST_PATH:
        return Path(".")
    return manifest_path.parent.parent.parent if manifest_path.parent.name == FIXTURE_ROOT.name else manifest_path.parent


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
        findings.append(_finding("manifest", "schema_version", "schema_version must be 1.0"))
    if manifest.get("fixture_set") != "stage2_promotion_review":
        findings.append(_finding("manifest", "fixture_set", "fixture_set must be stage2_promotion_review"))

    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        findings.append(_finding("manifest", "authority", "authority block is required"))
    else:
        for field, expected in REQUIRED_AUTHORITY.items():
            if authority.get(field) is not expected:
                findings.append(_finding("manifest", f"authority.{field}", f"must be {expected!r}"))

    entries = manifest.get("fixtures")
    if not isinstance(entries, list) or not entries:
        findings.append(_finding("manifest", "fixtures", "fixtures must be a non-empty list"))
        _raise_if_findings(findings)
        return

    seen_paths: set[str] = set()
    base = _resolve_manifest_base(manifest_path)

    for index, entry in enumerate(entries):
        fixture_label = f"manifest.fixtures[{index}]"
        if not isinstance(entry, dict):
            findings.append(_finding(fixture_label, "entry", "fixture entry must be an object"))
            continue

        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            findings.append(_finding(fixture_label, "path", "fixture path must be a non-empty string"))
            continue
        if path_value in seen_paths:
            findings.append(_finding(path_value, "path", "duplicate fixture path"))
        seen_paths.add(path_value)
        if not _fixture_path_is_safe(path_value):
            findings.append(_finding(path_value, "path", "fixture path must stay under fixtures/stage2_promotion_review and not reference output/"))
            continue

        expected = entry.get("expected")
        if expected not in ALLOWED_EXPECTED:
            findings.append(_finding(path_value, "expected", "expected must be pass or fail"))
            continue

        fixture_path = base / path_value
        if not fixture_path.exists():
            findings.append(_finding(path_value, "path", "fixture file does not exist"))
            continue

        if expected == "pass":
            expected_status = entry.get("expected_checklist_status")
            if expected_status not in ALLOWED_CHECKLIST_STATUSES:
                findings.append(_finding(path_value, "expected_checklist_status", "unknown expected checklist status"))
                continue
            findings.extend(_validate_pass_fixture(fixture_path, path_value, expected_status))
        else:
            expected_contains = entry.get("expected_failure_contains")
            if not isinstance(expected_contains, str) or not expected_contains.strip():
                findings.append(_finding(path_value, "expected_failure_contains", "fail fixtures must declare deterministic expected failure text"))
                continue
            findings.extend(_validate_fail_fixture(fixture_path, path_value, expected_contains))

    _raise_if_findings(findings)


def _validate_pass_fixture(fixture_path: Path, label: str, expected_status: str) -> list[FixtureFinding]:
    findings: list[FixtureFinding] = []
    try:
        payload = _load_json(fixture_path)
        schema_validator.validate_artifact(payload)
        checklist_status = checklist_validator.validate_checklist(payload)
    except Exception as exc:  # noqa: BLE001
        findings.append(_finding(label, "fixture", f"expected pass but validation failed: {exc}"))
        return findings
    if checklist_status != expected_status:
        findings.append(_finding(label, "expected_checklist_status", f"expected {expected_status}, got {checklist_status}"))
    return findings


def _validate_fail_fixture(fixture_path: Path, label: str, expected_contains: str) -> list[FixtureFinding]:
    findings: list[FixtureFinding] = []
    try:
        payload = _load_json(fixture_path)
        with contextlib.redirect_stdout(io.StringIO()) as stdout_buffer:
            checklist_validator.validate_checklist(payload)
        output = stdout_buffer.getvalue()
    except Exception as exc:  # noqa: BLE001
        output = stdout_buffer.getvalue() if "stdout_buffer" in locals() else ""
        combined = f"{output}\n{exc}"
        if expected_contains not in combined:
            findings.append(_finding(label, "expected_failure_contains", f"expected failure text {expected_contains!r} not found"))
        return findings
    findings.append(_finding(label, "expected", f"expected fail but validation passed with output {output!r}"))
    return findings


def validate_manifest_file(path: Path = DEFAULT_MANIFEST_PATH) -> None:
    validate_manifest_payload(_load_json(path), manifest_path=path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args()

    validate_manifest_file(args.manifest)
    print(f"STAGE2_PROMOTION_REVIEW_FIXTURES_OK | manifest={args.manifest}")


if __name__ == "__main__":
    main()
