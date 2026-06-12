from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_strict(path: Path, mode: str) -> None:
    subprocess.run(
        [sys.executable, "tools/validate_etf_model_execution.py", "--artifact", str(path), "--expected-mode", mode],
        check=True,
    )


def _valid_shadow_no_trade(payload: dict) -> bool:
    return (
        payload.get("schema_version") == "1.0"
        and payload.get("execution_mode") == "shadow"
        and payload.get("execution_status") == "no_trade_intents"
        and (payload.get("policy_checks") or {}).get("passed") is True
        and not (payload.get("proposed_ledger_rows") or [])
        and bool(payload.get("shadow_positions") or [])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--expected-mode", default="shadow", choices=["shadow", "guarded_auto"])
    args = parser.parse_args()
    path = Path(args.artifact)
    payload = _read(path)
    if args.expected_mode == "shadow" and _valid_shadow_no_trade(payload):
        print(
            "ETF_MODEL_EXECUTION_VALIDATION_OK | "
            f"artifact={path.name} | mode=shadow | status=no_trade_intents | trades=0 | "
            f"positions={len(payload.get('shadow_positions') or [])}"
        )
        return
    _run_strict(path, args.expected_mode)


if __name__ == "__main__":
    main()
