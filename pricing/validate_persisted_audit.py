from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
TITLE_DATE_RE = re.compile(r"^#\s+.*?(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def latest_pro_report(output_dir: Path) -> Path:
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        match = PRO_REPORT_RE.match(path.name)
        if not match:
            continue
        day = match.group(1)
        version = int(match.group(2) or "1")
        candidates.append((day, version, path))
    if not candidates:
        raise RuntimeError(f"No canonical English ETF pro reports found in {output_dir}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def parse_report_date(report_path: Path) -> str:
    text = report_path.read_text(encoding="utf-8")
    match = TITLE_DATE_RE.search(text)
    if not match:
        raise RuntimeError(f"Could not parse report date from title in {report_path}.")
    return match.group(1)


def load_audits(pricing_dir: Path) -> list[tuple[str, Path, dict[str, Any]]]:
    audits: list[tuple[str, Path, dict[str, Any]]] = []
    for path in sorted(pricing_dir.glob("price_audit_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid pricing audit JSON: {path}") from exc
        run_date = str(payload.get("run_date") or "")
        if not run_date:
            raise RuntimeError(f"Pricing audit is missing run_date: {path}")
        audits.append((run_date, path, payload))
    return audits


def validate_payload(path: Path, payload: dict[str, Any]) -> None:
    required = [
        "run_date",
        "requested_close_date",
        "holdings_count",
        "fresh_holdings_count",
        "coverage_count_pct",
        "invested_weight_coverage_pct",
        "decision",
        "prices",
        "holdings",
    ]
    missing = [key for key in required if key not in payload]
    if missing:
        raise RuntimeError(f"Pricing audit {path} is missing required field(s): {', '.join(missing)}")

    holdings_count = int(payload.get("holdings_count") or 0)
    if holdings_count <= 0:
        raise RuntimeError(f"Pricing audit {path} has no holdings_count.")

    prices = payload.get("prices") or []
    if not isinstance(prices, list) or not prices:
        raise RuntimeError(f"Pricing audit {path} has no price result rows.")

    holdings = payload.get("holdings") or []
    if not isinstance(holdings, list) or not holdings:
        raise RuntimeError(f"Pricing audit {path} has no holdings snapshot rows.")

    decision = str(payload.get("decision") or "")
    if decision not in {"update_covered_holdings_carry_unresolved", "blocked_or_partial"}:
        raise RuntimeError(f"Pricing audit {path} has unsupported decision: {decision}")


def iso_date(value: str, field: str, path: Path) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise RuntimeError(f"Pricing audit {path} has invalid {field}: {value}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate that a persisted ETF pricing audit exists before render/send.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--pricing-dir", default="output/pricing")
    parser.add_argument("--allow-prior-run-date", action="store_true", help="Allow the latest prior audit if no same-report-date audit exists.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    pricing_dir = Path(args.pricing_dir)
    report_path = latest_pro_report(output_dir)
    report_date = parse_report_date(report_path)

    audits = load_audits(pricing_dir)
    if not audits:
        raise RuntimeError(
            f"No persisted pricing audit found in {pricing_dir}. "
            "Run the persistent ETF pricing workflow before writing or sending the report."
        )

    exact_matches = [(path, payload) for run_date, path, payload in audits if run_date == report_date]
    if exact_matches:
        audit_path, payload = exact_matches[-1]
    elif args.allow_prior_run_date:
        report_dt = datetime.strptime(report_date, "%Y-%m-%d")
        prior = []
        for run_date, path, payload in audits:
            run_dt = iso_date(run_date, "run_date", path)
            if run_dt <= report_dt:
                prior.append((run_dt, path, payload))
        if not prior:
            raise RuntimeError(f"No persisted pricing audit on or before report date {report_date}.")
        prior.sort(key=lambda item: item[0])
        _, audit_path, payload = prior[-1]
    else:
        available = ", ".join(path.name for _, path, _ in audits) or "none"
        raise RuntimeError(
            f"No persisted pricing audit with run_date={report_date} for report {report_path.name}. "
            f"Available audits: {available}"
        )

    validate_payload(audit_path, payload)
    requested_close = str(payload.get("requested_close_date"))
    run_date = str(payload.get("run_date"))
    requested_dt = iso_date(requested_close, "requested_close_date", audit_path)
    report_dt = datetime.strptime(report_date, "%Y-%m-%d")
    if requested_dt > report_dt:
        raise RuntimeError(
            f"Pricing audit {audit_path.name} requested_close_date={requested_close} is after report_date={report_date}."
        )

    print(
        "PRICING_AUDIT_OK | "
        f"report={report_path.name} | audit={audit_path.name} | run_date={run_date} | "
        f"requested_close={requested_close} | decision={payload.get('decision')} | "
        f"fresh_holdings={payload.get('fresh_holdings_count')}/{payload.get('holdings_count')} | "
        f"coverage_count_pct={payload.get('coverage_count_pct')} | "
        f"invested_weight_coverage_pct={payload.get('invested_weight_coverage_pct')}"
    )


if __name__ == "__main__":
    main()
