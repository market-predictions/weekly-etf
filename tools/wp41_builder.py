#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
from typing import Any

from tools import build_stage2_promotion_review_decision_dry_run as dry_run_builder
from tools import validate_stage2_promotion_review_decision_dry_run as dry_run_validator
from tools import validate_stage2_promotion_review_explicit_decision_design_review as design_review_validator
from tools import validate_stage2_promotion_review_decision_schema as schema_validator

APPROVED_ROOT = Path("fixtures/stage2_promotion_review_decision/generated_samples")
APPROVED_PATH = APPROVED_ROOT / "non_production_decision_artifact_fixture.json"
DETERMINISTIC_GENERATED_AT_UTC = dry_run_builder.DETERMINISTIC_GENERATED_AT_UTC
BLOCKED_WRITE_ROOTS = {"output", "runtime", "portfolio", "reports", "delivery"}


def build_fixture_candidate() -> dict[str, Any]:
    artifact = dry_run_builder.build_dry_run()
    artifact["generated_at_utc"] = DETERMINISTIC_GENERATED_AT_UTC
    artifact["decision_status"] = "not_promoted"
    artifact["decision_scope"] = "review_decision_only"
    artifact["authority"] = dict(schema_validator.REQUIRED_AUTHORITY)
    artifact["source_evidence"] = dict(schema_validator.EXPECTED_SOURCE_EVIDENCE)
    artifact["decision_rationale"] = [
        {"code": "control_review_only", "severity": "info", "summary": "Decision record remains control-layer review only."}
    ]
    artifact["blocking_conditions"] = []
    artifact["required_future_work"] = [
        {"code": "future_decision", "severity": "info", "summary": "Non-production fixture generation remains validation-only and requires a future explicit decision package."},
        {"code": "future_work", "severity": "info", "summary": "Separate implementation work remains required before production use."},
    ]
    _validate_before_output(artifact)
    return artifact


def _validate_before_output(artifact: dict[str, Any]) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        dry_run_validator.validate_dry_run_artifact(artifact)
        design_review_validator.validate_file()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_write_path(path: Path, *, allow_tmp: bool = False) -> None:
    if path.is_absolute():
        if allow_tmp and (path == Path("/tmp") or Path("/tmp") in path.parents):
            return
        raise ValueError("write path must not be absolute")
    if any(part == ".." for part in path.parts):
        raise ValueError("write path must not contain traversal")
    if path.parts and path.parts[0] in BLOCKED_WRITE_ROOTS:
        raise ValueError(f"write path may not target {path.parts[0]}/")
    if not _is_relative_to(path, APPROVED_ROOT):
        raise ValueError(f"write path must stay under {APPROVED_ROOT}")


def write_fixture_candidate(path: Path, *, allow_tmp: bool = False) -> None:
    validate_write_path(path, allow_tmp=allow_tmp)
    artifact = build_fixture_candidate()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-to", type=Path)
    args = parser.parse_args()
    if args.write_to is not None:
        write_fixture_candidate(args.write_to)
        return
    print(json.dumps(build_fixture_candidate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
