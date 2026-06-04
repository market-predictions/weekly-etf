from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _parse_kv_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        raise SystemExit(f"Per-language delivery manifest not found: {path}")
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def _hash_recipient(value: str | None) -> str | None:
    raw = str(value or "").strip().lower()
    if not raw:
        return None
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _attachments(value: str | None) -> list[str]:
    raw = str(value or "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _language_manifest(report_path: Path, language: str) -> dict[str, Any]:
    manifest_path = report_path.with_name(f"{report_path.stem}_delivery_manifest.txt")
    manifest = _parse_kv_manifest(manifest_path)
    attachments = _attachments(manifest.get("attachments"))
    return {
        "language": language,
        "report_path": str(report_path),
        "source_manifest_path": str(manifest_path),
        "source_manifest_type": "legacy_kv_delivery_manifest",
        "timestamp_utc": manifest.get("timestamp_utc"),
        "mode": manifest.get("mode"),
        "report": manifest.get("report"),
        "recipient_hash": _hash_recipient(manifest.get("recipient")),
        "recipient_redacted": True,
        "html_body": manifest.get("html_body"),
        "pdf_attached": manifest.get("pdf_attached"),
        "attachments": attachments,
        "attachment_count": len(attachments),
        "pdf_attachments": [name for name in attachments if name.lower().endswith(".pdf")],
    }


def _out_path(output_dir: Path, requested_close_date: str, run_id: str) -> Path:
    return output_dir / "delivery" / f"weekly_etf_delivery_manifest_{requested_close_date}_{run_id}.json"


def _validate_summary(summary: dict[str, Any]) -> None:
    if summary.get("delivery_status") != "smtp_sendmail_returned_no_exception":
        raise SystemExit("Delivery summary has invalid delivery_status")
    if summary.get("recipient_data_policy") != "redacted_hash_only":
        raise SystemExit("Delivery summary must use redacted recipient policy")
    languages = summary.get("languages") or []
    if not languages:
        raise SystemExit("Delivery summary has no language entries")
    for item in languages:
        if not item.get("source_manifest_path"):
            raise SystemExit("Language delivery entry missing source_manifest_path")
        if item.get("recipient_redacted") is not True:
            raise SystemExit("Language delivery entry must redact recipient")
        if item.get("recipient_hash") and "@" in str(item.get("recipient_hash")):
            raise SystemExit("Language delivery entry leaked recipient email")
        if item.get("pdf_attached") != "yes":
            raise SystemExit("Language delivery entry does not prove PDF attachment")
        if not item.get("pdf_attachments"):
            raise SystemExit("Language delivery entry has no PDF attachment listed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write redaction-safe Weekly ETF delivery manifest summary after successful SMTP send.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--requested-close-date", required=True)
    parser.add_argument("--report-token", default=None)
    parser.add_argument("--english-report", required=True)
    parser.add_argument("--dutch-report", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    english_report = Path(args.english_report)
    if not english_report.exists():
        raise SystemExit(f"English report not found: {english_report}")

    languages = [_language_manifest(english_report, "en")]
    if args.dutch_report:
        dutch_report = Path(args.dutch_report)
        if dutch_report.exists():
            languages.append(_language_manifest(dutch_report, "nl"))

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "weekly_etf_delivery_manifest_summary",
        "generated_at_utc": generated_at,
        "run_id": args.run_id,
        "requested_close_date": args.requested_close_date,
        "report_token": args.report_token,
        "delivery_status": "smtp_sendmail_returned_no_exception",
        "delivery_status_meaning": "send_report.py returned after smtplib.sendmail without raising and wrote per-language delivery manifest(s); this is not an end-recipient inbox receipt.",
        "recipient_data_policy": "redacted_hash_only",
        "languages": languages,
        "language_count": len(languages),
        "source": {
            "writer": "tools/write_etf_delivery_manifest_summary.py",
            "basis": "per-language delivery manifest(s) written after send_email_with_attachments returned",
        },
    }
    _validate_summary(summary)

    path = _out_path(output_dir, args.requested_close_date, args.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latest = path.parent / "latest_weekly_etf_delivery_manifest_path.txt"
    latest.write_text(str(path) + "\n", encoding="utf-8")

    print(
        "ETF_DELIVERY_MANIFEST_OK | "
        f"run_id={args.run_id} | requested_close={args.requested_close_date} | "
        f"languages={len(languages)} | status={summary['delivery_status']} | manifest={path}"
    )


if __name__ == "__main__":
    main()
