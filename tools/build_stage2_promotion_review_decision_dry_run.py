#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
from typing import Any

from tools import build_stage2_promotion_review_decision_sample as sample_builder
from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_sample_gate as sample_gate
from tools import validate_stage2_promotion_review_decision_schema as schema_validator

DETERMINISTIC_GENERATED_AT_UTC = sample_builder.DETERMINISTIC_GENERATED_AT_UTC
ALLOWED_WRITE_ROOT = sample_builder.ALLOWED_WRITE_ROOT


def build_dry_run() -> dict[str, Any]:
    artifact = sample_builder.build_sample()
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
        {"code": "future_decision", "severity": "info", "summary": "Dry-run generation remains non-production and requires a future explicit decision package."},
        {"code": "future_work", "severity": "info", "summary": "Separate implementation work remains required before production use."},
    ]
    _validate_before_output(artifact)
    return artifact


def _validate_before_output(artifact: dict[str, Any]) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        schema_validator.validate_artifact(artifact, require_expected_sources=True)
        hardening._validate_hardened_artifact(artifact)
        sample_gate.validate_sample(artifact)


def validate_write_path(path: Path, *, allow_tmp: bool = False) -> None:
    sample_builder.validate_write_path(path, allow_tmp=allow_tmp)


def write_dry_run(path: Path, *, allow_tmp: bool = False) -> None:
    validate_write_path(path, allow_tmp=allow_tmp)
    artifact = build_dry_run()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-to", type=Path)
    args = parser.parse_args()
    if args.write_to is not None:
        write_dry_run(args.write_to)
        return
    print(json.dumps(build_dry_run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
