from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

LATEST_RUN_POINTER = Path("output/run_manifests/latest_weekly_etf_run_manifest_path.txt")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_run_manifest(path_arg: str | None) -> Path:
    if path_arg:
        path = Path(path_arg)
        if not path.exists():
            raise RuntimeError(f"Manifest evidence validation failed: explicit run manifest does not exist: {path}")
        return path
    if not LATEST_RUN_POINTER.exists():
        raise RuntimeError("Manifest evidence validation failed: latest run-manifest pointer is missing.")
    raw = LATEST_RUN_POINTER.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError("Manifest evidence validation failed: latest run-manifest pointer is empty.")
    candidates = [Path(raw), LATEST_RUN_POINTER.parent / Path(raw).name]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError(f"Manifest evidence validation failed: pointed run manifest does not exist: {raw}")


def _require_path(path_value: str | None, label: str) -> Path:
    if not path_value:
        raise RuntimeError(f"Manifest evidence validation failed: missing {label}.")
    path = Path(path_value)
    if not path.exists():
        raise RuntimeError(f"Manifest evidence validation failed: {label} does not exist: {path}")
    return path


def validate(run_manifest_path: Path) -> None:
    run = _read_json(run_manifest_path)
    errors: list[str] = []
    if run.get("workflow_status") != "workflow_success":
        errors.append(f"workflow_status={run.get('workflow_status')}")
    if run.get("workflow_conclusion") not in {"success", None}:
        errors.append(f"workflow_conclusion={run.get('workflow_conclusion')}")
    if run.get("pricing_lineage_status") != "passed":
        errors.append(f"pricing_lineage_status={run.get('pricing_lineage_status')}")

    required_run_paths = {
        "english_report_path": run.get("english_report_path"),
        "dutch_report_path": run.get("dutch_report_path"),
        "pricing_audit_path": run.get("pricing_audit_path"),
        "runtime_state_path": run.get("runtime_state_path"),
        "portfolio_state_path": run.get("portfolio_state_path"),
        "valuation_history_path": run.get("valuation_history_path"),
        "delivery_manifest_path": run.get("delivery_manifest_path"),
    }
    for label, path_value in required_run_paths.items():
        try:
            _require_path(path_value, label)
        except RuntimeError as exc:
            errors.append(str(exc))

    delivery_path = Path(str(run.get("delivery_manifest_path") or ""))
    delivery = _read_json(delivery_path) if delivery_path.exists() else {}
    if delivery.get("delivery_status") != "smtp_sendmail_returned_no_exception":
        errors.append(f"delivery_status={delivery.get('delivery_status')}")
    if delivery.get("delivery_status_meaning") and "not an end-recipient inbox receipt" not in str(delivery.get("delivery_status_meaning")):
        errors.append("delivery_status_meaning_missing_inbox_receipt_caveat")
    languages = delivery.get("languages") or []
    language_codes = {str(row.get("language")) for row in languages if isinstance(row, dict)}
    if language_codes != {"en", "nl"}:
        errors.append(f"delivery_languages={sorted(language_codes)}")
    for row in languages:
        if not isinstance(row, dict):
            continue
        language = row.get("language")
        if row.get("pdf_attached") != "yes":
            errors.append(f"{language}:pdf_attached={row.get('pdf_attached')}")
        for attachment in row.get("attachments") or []:
            candidate = Path("output") / str(attachment)
            if not candidate.exists():
                errors.append(f"{language}:attachment_missing:{attachment}")
        for pdf_name in row.get("pdf_attachments") or []:
            candidate = Path("output") / str(pdf_name)
            if not candidate.exists():
                errors.append(f"{language}:pdf_attachment_missing:{pdf_name}")

    if errors:
        raise RuntimeError("ETF manifest evidence validation failed for " + run_manifest_path.name + ": " + "; ".join(sorted(set(errors))))
    print(
        "ETF_MANIFEST_EVIDENCE_OK | "
        f"run_id={run.get('run_id')} | requested_close={run.get('requested_close_date')} | "
        f"report_token={run.get('report_token')} | delivery={delivery.get('delivery_status')}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate latest Weekly ETF run/delivery manifest evidence.")
    parser.add_argument("--run-manifest", default=None)
    args = parser.parse_args()
    validate(_resolve_run_manifest(args.run_manifest))


if __name__ == "__main__":
    main()
