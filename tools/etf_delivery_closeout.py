#!/usr/bin/env python3
"""Build and validate Weekly ETF post-action delivery closeout evidence.

This module is intentionally read-only with respect to reports, portfolio state,
pricing, and the trade ledger. It consumes an already-passing pre-send release
assurance record, the post-SMTP delivery manifest, and independent receiving-
system receipt evidence for English and Dutch messages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPLEMENTATION_ROLE = "implementation_operations"
ASSURANCE_ROLE = "governance_release_assurance"
LANGUAGES = {"en", "nl"}
SHA256_RE = re.compile(r"[0-9a-f]{64}")
REQUIRED_CHECKS = {
    "pre_send_assurance_passed",
    "identity_consistent",
    "delivery_manifest_consistent",
    "independent_receipts_complete",
    "recipient_hashes_consistent",
    "receipt_timestamps_after_transport",
    "received_artifact_hashes_consistent",
    "roles_separated",
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def parse_time(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def add_check(
    checks: list[dict[str, Any]], blockers: list[str], check_id: str, passed: bool, evidence: Any
) -> None:
    checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
    if not passed:
        blockers.append(check_id)


def basename_hashes(assurance: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in (assurance.get("artifact_hashes") or {}).values():
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "").strip()
        digest = str(item.get("sha256") or "").strip().lower()
        if path and SHA256_RE.fullmatch(digest):
            result[Path(path).name] = digest
    return result


def language_delivery_entries(delivery: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for item in delivery.get("languages") or []:
        if isinstance(item, dict) and item.get("language") in LANGUAGES:
            entries[str(item["language"])] = item
    return entries


def language_receipts(receipts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for item in receipts.get("messages") or []:
        if isinstance(item, dict) and item.get("language") in LANGUAGES:
            entries[str(item["language"])] = item
    return entries


def build_delivery_closeout(
    *,
    release_assurance_path: Path,
    delivery_manifest_path: Path,
    receipt_evidence_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    assurance = load_json(release_assurance_path)
    delivery = load_json(delivery_manifest_path)
    receipts = load_json(receipt_evidence_path)
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []

    assurance_pass = assurance.get("decision") == "PASS" and not assurance.get("blockers")
    add_check(
        checks,
        blockers,
        "pre_send_assurance_passed",
        assurance_pass,
        {"decision": assurance.get("decision"), "path": str(release_assurance_path)},
    )

    identity = assurance.get("identity") if isinstance(assurance.get("identity"), dict) else {}
    expected_identity = {
        "source_sha": identity.get("source_sha"),
        "run_id": identity.get("run_id"),
        "requested_close_date": identity.get("requested_close_date"),
        "report_token": identity.get("report_token"),
    }
    receipt_identity = receipts.get("identity") if isinstance(receipts.get("identity"), dict) else {}
    identity_errors = {
        key: {"expected": value, "received": receipt_identity.get(key)}
        for key, value in expected_identity.items()
        if not value or receipt_identity.get(key) != value
    }
    add_check(checks, blockers, "identity_consistent", not identity_errors, identity_errors)

    delivery_errors: dict[str, Any] = {}
    for key in ("run_id", "requested_close_date", "report_token"):
        if delivery.get(key) != expected_identity.get(key):
            delivery_errors[key] = {
                "expected": expected_identity.get(key),
                "received": delivery.get(key),
            }
    if delivery.get("delivery_status") != "smtp_sendmail_returned_no_exception":
        delivery_errors["delivery_status"] = delivery.get("delivery_status")
    delivery_entries = language_delivery_entries(delivery)
    if set(delivery_entries) != LANGUAGES:
        delivery_errors["languages"] = sorted(delivery_entries)
    add_check(
        checks,
        blockers,
        "delivery_manifest_consistent",
        not delivery_errors,
        {"errors": delivery_errors, "path": str(delivery_manifest_path)},
    )

    receipt_entries = language_receipts(receipts)
    receipt_errors: dict[str, Any] = {}
    if receipts.get("source_type") not in {"gmail_receiving_system", "independent_receiving_system"}:
        receipt_errors["source_type"] = receipts.get("source_type")
    if receipts.get("captured_by_role") != ASSURANCE_ROLE:
        receipt_errors["captured_by_role"] = receipts.get("captured_by_role")
    if set(receipt_entries) != LANGUAGES:
        receipt_errors["languages"] = sorted(receipt_entries)
    for language, item in receipt_entries.items():
        if not str(item.get("message_id") or "").strip():
            receipt_errors[f"{language}_message_id"] = "missing"
        if not str(item.get("subject") or "").strip():
            receipt_errors[f"{language}_subject"] = "missing"
        if not parse_time(item.get("received_at_utc")):
            receipt_errors[f"{language}_received_at_utc"] = item.get("received_at_utc")
        if not isinstance(item.get("attachments"), list) or not item.get("attachments"):
            receipt_errors[f"{language}_attachments"] = "missing"
    add_check(
        checks,
        blockers,
        "independent_receipts_complete",
        not receipt_errors,
        receipt_errors,
    )

    recipient_errors: dict[str, Any] = {}
    for language in LANGUAGES:
        expected = str(delivery_entries.get(language, {}).get("recipient_hash") or "")
        received = str(receipt_entries.get(language, {}).get("recipient_hash") or "")
        if not expected or received != expected:
            recipient_errors[language] = {"expected": expected, "received": received}
    add_check(
        checks,
        blockers,
        "recipient_hashes_consistent",
        not recipient_errors,
        recipient_errors,
    )

    time_errors: dict[str, Any] = {}
    for language in LANGUAGES:
        transport = parse_time(delivery_entries.get(language, {}).get("timestamp_utc"))
        received = parse_time(receipt_entries.get(language, {}).get("received_at_utc"))
        if not transport or not received or received < transport:
            time_errors[language] = {
                "transport": delivery_entries.get(language, {}).get("timestamp_utc"),
                "received": receipt_entries.get(language, {}).get("received_at_utc"),
            }
    add_check(
        checks,
        blockers,
        "receipt_timestamps_after_transport",
        not time_errors,
        time_errors,
    )

    expected_hashes = basename_hashes(assurance)
    artifact_errors: dict[str, Any] = {}
    matched_by_language: dict[str, list[str]] = {}
    required_suffixes = {".pdf", ".html", ".png"}
    for language in LANGUAGES:
        matched: list[str] = []
        received_attachments = receipt_entries.get(language, {}).get("attachments") or []
        for attachment in received_attachments:
            if not isinstance(attachment, dict):
                continue
            filename = str(attachment.get("filename") or "")
            digest = str(attachment.get("sha256") or "").lower()
            expected_digest = expected_hashes.get(filename)
            if expected_digest and digest == expected_digest:
                matched.append(filename)
            elif expected_digest:
                artifact_errors[f"{language}:{filename}"] = {
                    "expected": expected_digest,
                    "received": digest,
                }
        matched_by_language[language] = matched
        suffixes = {Path(name).suffix.lower() for name in matched}
        missing_suffixes = sorted(required_suffixes - suffixes)
        if missing_suffixes:
            artifact_errors[f"{language}:required_types"] = missing_suffixes
    add_check(
        checks,
        blockers,
        "received_artifact_hashes_consistent",
        bool(expected_hashes) and not artifact_errors,
        {"matched": matched_by_language, "errors": artifact_errors},
    )

    add_check(
        checks,
        blockers,
        "roles_separated",
        assurance.get("implementation_role") == IMPLEMENTATION_ROLE
        and assurance.get("assurance_role") == ASSURANCE_ROLE
        and IMPLEMENTATION_ROLE != ASSURANCE_ROLE,
        {
            "implementation_role": assurance.get("implementation_role"),
            "assurance_role": assurance.get("assurance_role"),
            "receipt_captured_by_role": receipts.get("captured_by_role"),
        },
    )

    decision = "DELIVERY_CONFIRMED" if not blockers else "FAIL"
    record = {
        "schema_version": "1.0.0",
        "contract_id": "ETF_RELEASE_ASSURANCE_CONTRACT_V1",
        "artifact_type": "weekly_etf_delivery_closeout",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "decision": decision,
        "implementation_role": IMPLEMENTATION_ROLE,
        "assurance_role": ASSURANCE_ROLE,
        "identity": expected_identity,
        "inputs": {
            "release_assurance": str(release_assurance_path),
            "delivery_manifest": str(delivery_manifest_path),
            "receipt_evidence": str(receipt_evidence_path),
        },
        "checks": checks,
        "blockers": blockers,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def validate_delivery_closeout(
    path: Path,
    *,
    expected_run_id: str | None = None,
    expected_close_date: str | None = None,
    expected_report_token: str | None = None,
) -> dict[str, Any]:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("decision") != "DELIVERY_CONFIRMED":
        errors.append(f"decision must be DELIVERY_CONFIRMED, got {payload.get('decision')!r}")
    if payload.get("blockers"):
        errors.append(f"blockers present: {payload.get('blockers')}")
    if payload.get("implementation_role") != IMPLEMENTATION_ROLE:
        errors.append("implementation role mismatch")
    if payload.get("assurance_role") != ASSURANCE_ROLE:
        errors.append("assurance role mismatch")

    checks = {item.get("id"): item for item in payload.get("checks", []) if isinstance(item, dict)}
    missing = sorted(REQUIRED_CHECKS - set(checks))
    failed = sorted(key for key, item in checks.items() if item.get("passed") is not True)
    if missing:
        errors.append(f"required checks missing: {missing}")
    if failed:
        errors.append(f"failed checks present: {failed}")

    identity = payload.get("identity") if isinstance(payload.get("identity"), dict) else {}
    for key, expected in {
        "run_id": expected_run_id,
        "requested_close_date": expected_close_date,
        "report_token": expected_report_token,
    }.items():
        if expected is not None and identity.get(key) != expected:
            errors.append(f"identity mismatch for {key}: expected {expected!r}, got {identity.get(key)!r}")

    if errors:
        raise RuntimeError("ETF delivery closeout rejected: " + "; ".join(errors))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--release-assurance", type=Path, required=True)
    build.add_argument("--delivery-manifest", type=Path, required=True)
    build.add_argument("--receipt-evidence", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("--closeout", type=Path, required=True)
    validate.add_argument("--expected-run-id")
    validate.add_argument("--expected-close-date")
    validate.add_argument("--expected-report-token")

    args = parser.parse_args()
    if args.command == "build":
        record = build_delivery_closeout(
            release_assurance_path=args.release_assurance,
            delivery_manifest_path=args.delivery_manifest,
            receipt_evidence_path=args.receipt_evidence,
            output_path=args.output,
        )
        print(
            "ETF_DELIVERY_CLOSEOUT_BUILT | "
            f"decision={record['decision']} | output={args.output} | blockers={record['blockers']}"
        )
        if record["decision"] != "DELIVERY_CONFIRMED":
            raise SystemExit(1)
    else:
        validate_delivery_closeout(
            args.closeout,
            expected_run_id=args.expected_run_id,
            expected_close_date=args.expected_close_date,
            expected_report_token=args.expected_report_token,
        )
        print(f"ETF_DELIVERY_CLOSEOUT_VALID | closeout={args.closeout}")


if __name__ == "__main__":
    main()
