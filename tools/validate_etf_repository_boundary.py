#!/usr/bin/env python3
"""Fail closed when FX production assets leak into the Weekly ETF repository."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROHIBITED_ROOT_PATHS = ("prediction.py", "daily_outputs", "mt5_output", "gpt.txt")
PROHIBITED_WORKFLOW_TOKENS = (
    "TWELVEDATA_API_KEY",
    "python prediction.py",
    "daily_outputs/latest",
    "FX_BACKTEST",
    "DailyTradeBias",
    "market-predictions/daily-fx",
)


def validate(root: Path) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    for relative in PROHIBITED_ROOT_PATHS:
        if (root / relative).exists():
            blockers.append({"type": "misplaced_product_asset", "path": relative})
    workflow_dir = root / ".github" / "workflows"
    if workflow_dir.is_dir():
        for path in sorted(workflow_dir.iterdir()):
            if path.suffix.lower() not in {".yml", ".yaml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for token in PROHIBITED_WORKFLOW_TOKENS:
                if token.lower() in text.lower():
                    blockers.append({"type": "fx_token_in_active_workflow", "path": str(path.relative_to(root)), "token": token})
    return {
        "schema_version": "weekly_etf_repository_boundary_validation_v1",
        "product": "weekly_etf",
        "valid": not blockers,
        "verdict": "PASS" if not blockers else "FAIL",
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
