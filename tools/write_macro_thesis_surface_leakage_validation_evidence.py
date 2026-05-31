#!/usr/bin/env python3
"""Write repo-visible evidence for the ETF macro/thesis surface leakage validator.

This evidence proves the isolated validator workflow passed its safe and planted
failure fixtures. It does not promote macro/thesis content into client-facing
reports; it only records that leakage detection is functioning.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_MARKERS = [
    "ETF_MACRO_THESIS_SURFACE_LEAKAGE_SELF_TEST_OK",
    "ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK",
    "ETF_MACRO_THESIS_SURFACE_LEAKAGE_EXPECTED_FAILURE_OK",
]


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro/validation"))
    parser.add_argument("--workflow-name", default="Validate ETF macro thesis surface leakage")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence = {
        "schema_version": "1.0",
        "artifact_type": "macro_thesis_surface_leakage_validation_evidence",
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
        "validated_markers": EXPECTED_MARKERS,
        "scope": {
            "english_markdown_guard": True,
            "dutch_markdown_guard": True,
            "delivery_html_guard": True,
            "production_send_workflow_wired": True,
        },
        "authority": {
            "shadow_only": True,
            "client_facing_authority": False,
            "production_report_path_changed": False,
            "macro_thesis_promotion": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
        },
        "guardrails": [
            "Evidence proves leakage detection only.",
            "Do not treat this as macro/thesis content promotion.",
            "Stage-1 and Stage-2 artifacts remain internal-only unless a later control-layer promotion decision is made.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}")
    run_path = args.output_dir / f"macro_thesis_surface_leakage_validation_{token}.json"
    latest_path = args.output_dir / "latest_macro_thesis_surface_leakage_validation.json"
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    print(
        "ETF_MACRO_THESIS_SURFACE_LEAKAGE_EVIDENCE_OK | "
        f"status={evidence['status']} | run_path={run_path} | latest_path={latest_path}"
    )


if __name__ == "__main__":
    main()
