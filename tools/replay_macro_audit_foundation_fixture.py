from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from macro_sources.build_macro_data_audit import build_macro_data_audit
from tools.validate_macro_data_audit import validate as validate_macro_data_audit

DEFAULT_FIXTURE = Path("tests/fixtures/macro_data_audit_fixture.json")
DEFAULT_CONFIG = Path("config/macro_data_sources.yml")
DEFAULT_CB_CALENDAR = Path("config/cb_calendar.yml")
DEFAULT_OUTPUT_DIR = Path("output/macro/validation")


def _safe_token(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip()) or "unknown"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def replay(args: argparse.Namespace) -> dict[str, Any]:
    payload = build_macro_data_audit(
        config_path=args.config,
        cb_calendar_path=args.cb_calendar,
        reference_date=args.reference_date,
        run_id=args.run_id,
        fixture_path=args.fixture,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}_{args.run_id}")
    audit_path = args.output_dir / f"wp18_macro_data_audit_fixture_{run_token}.json"
    _write_json(audit_path, payload)
    validation = validate_macro_data_audit(audit_path)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence = {
        "schema_version": "1.0",
        "artifact_type": "wp18_macro_audit_foundation_validation",
        "status": "passed",
        "generated_at_utc": generated_at,
        "repository": "market-predictions/weekly-etf",
        "workflow": {
            "name": args.workflow_name,
            "run_id": args.workflow_run_id,
            "run_number": args.workflow_run_number,
            "run_attempt": args.workflow_attempt,
            "commit_sha": args.commit_sha,
            "source_ref": args.source_ref,
        },
        "source_files": {
            "fixture": str(args.fixture),
            "macro_data_sources": str(args.config),
            "central_bank_calendar": str(args.cb_calendar),
            "audit_artifact": str(audit_path),
        },
        "validated_markers": ["ETF_MACRO_DATA_AUDIT_VALID_OK", "ETF_MACRO_AUDIT_FOUNDATION_FIXTURE_OK"],
        "macro_data_audit_summary": validation,
        "authority": {
            "shadow_only": True,
            "client_facing_authority": False,
            "decision_impact": "none_phase2_audit_only",
            "production_report_path_changed": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
            "portfolio_mutation": False,
        },
    }
    evidence_path = args.output_dir / f"wp18_macro_audit_foundation_validation_{run_token}.json"
    latest_path = args.output_dir / "latest_wp18_macro_audit_foundation_validation.json"
    _write_json(evidence_path, evidence)
    _write_json(latest_path, evidence)
    print(
        "ETF_MACRO_AUDIT_FOUNDATION_FIXTURE_OK | "
        f"mode={validation['mode']} | reference_date={validation['reference_date']} | "
        f"observations={validation['observations']} | groups={','.join(validation['groups'])} | "
        f"audit={audit_path} | evidence={evidence_path}"
    )
    return {"audit": str(audit_path), "evidence": str(evidence_path), "latest": str(latest_path), "summary": validation}


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay the WP18 macro-audit foundation fixture and write shadow-only validation evidence.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cb-calendar", type=Path, default=DEFAULT_CB_CALENDAR)
    parser.add_argument("--reference-date", default="2026-05-31")
    parser.add_argument("--run-id", default="wp18_macro_audit_foundation_fixture")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--workflow-name", default="local")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()
    replay(args)


if __name__ == "__main__":
    main()
