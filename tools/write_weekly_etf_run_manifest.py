from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _text(value: Any) -> str | None:
    raw = str(value or "").strip()
    return raw or None


def _load_json(path_value: str | None) -> dict[str, Any]:
    if not path_value:
        return {}
    path = Path(path_value)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _report_token(close_date: str | None) -> str | None:
    if not close_date:
        return None
    try:
        return datetime.strptime(close_date, "%Y-%m-%d").strftime("%y%m%d")
    except ValueError:
        token = close_date.replace("-", "")
        return token[-6:] if len(token) >= 6 else token


def _manifest_path(output_dir: Path, requested_close_date: str, run_id: str) -> Path:
    return output_dir / "run_manifests" / f"weekly_etf_run_manifest_{requested_close_date}_{run_id}.json"


def _pricing_lineage_status(existing: dict[str, Any], incoming_status: str | None) -> str:
    """Keep pricing-lineage status separate from generic workflow status.

    The final workflow manifest write runs with a generic status such as
    `workflow_success`. Once the hard pricing-lineage validator has marked the
    manifest as `passed`, that final always-run step must not downgrade the
    contract status back to a workflow lifecycle label.
    """
    existing_status = str(existing.get("pricing_lineage_status") or "").strip()
    incoming = str(incoming_status or "").strip()
    if existing_status == "passed" and incoming.startswith("workflow_"):
        return existing_status
    return incoming or existing_status or "pending"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write or update the Weekly ETF run manifest.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--manifest-path", default=None)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--requested-close-date", required=True)
    parser.add_argument("--report-token", default=None)
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--runtime-state", default=None)
    parser.add_argument("--english-report", default=None)
    parser.add_argument("--dutch-report", default=None)
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_valuation_history.csv")
    parser.add_argument("--delivery-manifest", default=None)
    parser.add_argument("--status", default="pending")
    parser.add_argument("--conclusion", default=None)
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest_path) if args.manifest_path else _manifest_path(output_dir, args.requested_close_date, args.run_id)
    existing = _load_json(str(manifest_path))
    audit = _load_json(args.pricing_audit)
    runtime = _load_json(args.runtime_state)

    manifest: dict[str, Any] = dict(existing)
    manifest.update(
        {
            "schema_version": "1.0",
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": args.run_id,
            "requested_close_date": args.requested_close_date,
            "report_token": args.report_token or _report_token(args.requested_close_date),
            "pricing_audit_path": _text(args.pricing_audit) or existing.get("pricing_audit_path"),
            "runtime_state_path": _text(args.runtime_state) or existing.get("runtime_state_path"),
            "english_report_path": _text(args.english_report) or existing.get("english_report_path"),
            "dutch_report_path": _text(args.dutch_report) or existing.get("dutch_report_path"),
            "portfolio_state_path": _text(args.portfolio_state) or existing.get("portfolio_state_path"),
            "valuation_history_path": _text(args.valuation_history) or existing.get("valuation_history_path"),
            "delivery_manifest_path": _text(args.delivery_manifest) or existing.get("delivery_manifest_path"),
            "pricing_lineage_status": _pricing_lineage_status(existing, args.status),
            "workflow_status": args.status or existing.get("workflow_status"),
            "workflow_conclusion": args.conclusion or existing.get("workflow_conclusion"),
            "notes": args.notes or existing.get("notes"),
        }
    )

    if audit:
        manifest["pricing_summary"] = {
            "decision": audit.get("decision"),
            "holdings_count": audit.get("holdings_count"),
            "fresh_holdings_count": audit.get("fresh_holdings_count"),
            "carried_forward_holdings_count": audit.get("carried_forward_holdings_count"),
            "coverage_count_pct": audit.get("coverage_count_pct"),
            "invested_weight_coverage_pct": audit.get("invested_weight_coverage_pct"),
            "unresolved_tickers": audit.get("unresolved_tickers"),
        }
    if runtime:
        portfolio = runtime.get("portfolio") or {}
        sources = runtime.get("source_files") or {}
        manifest["runtime_summary"] = {
            "report_date": runtime.get("report_date"),
            "total_portfolio_value_eur": portfolio.get("total_portfolio_value_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "pricing_audit_source": sources.get("pricing_audit"),
            "lane_assessment_source": sources.get("lane_assessment"),
        }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (manifest_path.parent / "latest_weekly_etf_run_manifest_path.txt").write_text(str(manifest_path) + "\n", encoding="utf-8")
    print(
        "ETF_RUN_MANIFEST_OK | "
        f"run_id={manifest.get('run_id')} | requested_close={manifest.get('requested_close_date')} | "
        f"status={manifest.get('pricing_lineage_status')} | manifest={manifest_path}"
    )


if __name__ == "__main__":
    main()
