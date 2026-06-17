#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools import validate_stage2_promotion_review_decision_schema as schema_validator

DETERMINISTIC_GENERATED_AT_UTC = "2026-06-17T00:00:00Z"
ALLOWED_WRITE_ROOT = Path("fixtures/stage2_promotion_review_decision/generated_samples")
BLOCKED_WRITE_ROOTS = {"output", "runtime", "portfolio", "reports", "delivery"}


def build_sample() -> dict[str, Any]:
    sample = schema_validator.valid_artifact()
    sample["generated_at_utc"] = DETERMINISTIC_GENERATED_AT_UTC
    sample["decision_status"] = "not_promoted"
    sample["decision_scope"] = "review_decision_only"
    sample["authority"] = dict(schema_validator.REQUIRED_AUTHORITY)
    sample["source_evidence"] = dict(schema_validator.EXPECTED_SOURCE_EVIDENCE)
    sample["decision_rationale"] = [
        {"code": "control_review_only", "severity": "info", "summary": "Decision record remains control-layer review only."}
    ]
    sample["blocking_conditions"] = []
    sample["required_future_work"] = [
        {"code": "future_decision", "severity": "info", "summary": "Sample generation remains non-production and requires a future explicit decision package."},
        {"code": "future_work", "severity": "info", "summary": "Separate implementation work remains required before production use."},
    ]
    sample["non_goals"] = [
        "no report change",
        "no scoring change",
        "no capital action",
        "no delivery or run change",
        "no historical artifact change",
    ]
    return sample


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
    if not _is_relative_to(path, ALLOWED_WRITE_ROOT):
        raise ValueError(f"write path must stay under {ALLOWED_WRITE_ROOT}")


def write_sample(path: Path, *, allow_tmp: bool = False) -> None:
    validate_write_path(path, allow_tmp=allow_tmp)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_sample(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-to", type=Path)
    args = parser.parse_args()
    if args.write_to is not None:
        write_sample(args.write_to)
        return
    print(json.dumps(build_sample(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
