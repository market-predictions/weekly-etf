#!/usr/bin/env python3
"""Write repo-visible evidence for the Dutch terminology contract workflow.

This evidence proves the isolated Dutch terminology contract validation passed.
It is a quality/terminology guard only and does not alter investment logic,
macro/thesis authority, portfolio scoring, fundability, or recommendations.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_MARKERS = ["ETF_NL_TERMINOLOGY_CONTRACT_OK"]


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro/validation"))
    parser.add_argument("--workflow-name", default="Validate ETF Dutch terminology contract")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence = {
        "schema_version": "1.0",
        "artifact_type": "nl_terminology_contract_validation_evidence",
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
            "central_terminology_contract": True,
            "localization_overlay_guard": True,
            "native_dutch_safety_overlay_guard": True,
            "bad_token_repair_or_block_guard": True,
            "disclaimer_replacement_guard": True,
        },
        "authority": {
            "quality_guard_only": True,
            "client_facing_investment_logic_changed": False,
            "macro_thesis_promotion": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
            "production_recommendation_authority": False,
        },
        "guardrails": [
            "Evidence proves Dutch terminology contract validation only.",
            "Do not treat this as macro/thesis promotion or investment-logic change.",
            "Dutch terminology remains a quality/alias layer derived from central terminology maps.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}")
    run_path = args.output_dir / f"nl_terminology_contract_validation_{token}.json"
    latest_path = args.output_dir / "latest_nl_terminology_contract_validation.json"
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    print(
        "ETF_NL_TERMINOLOGY_EVIDENCE_OK | "
        f"status={evidence['status']} | run_path={run_path} | latest_path={latest_path}"
    )


if __name__ == "__main__":
    main()
