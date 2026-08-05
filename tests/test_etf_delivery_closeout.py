from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.etf_delivery_closeout import build_delivery_closeout, validate_delivery_closeout


def _write(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, (dict, list)):
        path.write_text(json.dumps(payload), encoding="utf-8")
    else:
        path.write_bytes(payload)
    return path


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_sha = "a" * 40
    run_id = "20260805_210000"
    close_date = "2026-08-04"
    token = "260804"

    files: dict[str, bytes] = {
        "weekly_analysis_pro_260804.pdf": b"%PDF-test-en",
        "weekly_analysis_pro_260804_delivery.html": b"<!doctype html><html>en</html>",
        "weekly_analysis_pro_260804_equity_curve.png": b"\x89PNG\r\n\x1a\n-en",
        "weekly_analysis_pro_nl_260804.pdf": b"%PDF-test-nl",
        "weekly_analysis_pro_nl_260804_delivery.html": b"<!doctype html><html>nl</html>",
        "weekly_analysis_pro_nl_260804_equity_curve.png": b"\x89PNG\r\n\x1a\n-nl",
    }
    artifact_hashes = {}
    for index, (name, data) in enumerate(files.items()):
        path = _write(tmp_path / name, data)
        artifact_hashes[f"artifact_{index}"] = {"path": str(path), "sha256": _sha(data)}

    assurance = {
        "decision": "PASS",
        "blockers": [],
        "implementation_role": "implementation_operations",
        "assurance_role": "governance_release_assurance",
        "identity": {
            "source_sha": source_sha,
            "run_id": run_id,
            "requested_close_date": close_date,
            "report_token": token,
        },
        "artifact_hashes": artifact_hashes,
    }
    assurance_path = _write(tmp_path / "assurance.json", assurance)

    recipient_en = "sha256:" + "1" * 64
    recipient_nl = "sha256:" + "2" * 64
    delivery = {
        "run_id": run_id,
        "requested_close_date": close_date,
        "report_token": token,
        "delivery_status": "smtp_sendmail_returned_no_exception",
        "languages": [
            {"language": "en", "recipient_hash": recipient_en, "timestamp_utc": "2026-08-05T20:00:00Z"},
            {"language": "nl", "recipient_hash": recipient_nl, "timestamp_utc": "2026-08-05T20:00:01Z"},
        ],
    }
    delivery_path = _write(tmp_path / "delivery.json", delivery)

    receipts = {
        "source_type": "gmail_receiving_system",
        "captured_by_role": "governance_release_assurance",
        "identity": {
            "source_sha": source_sha,
            "run_id": run_id,
            "requested_close_date": close_date,
            "report_token": token,
        },
        "messages": [
            {
                "language": "en",
                "message_id": "msg-en",
                "subject": "Weekly ETF Pro Review",
                "recipient_hash": recipient_en,
                "received_at_utc": "2026-08-05T20:01:00Z",
                "attachments": [
                    {"filename": name, "sha256": _sha(data)}
                    for name, data in files.items()
                    if "_nl_" not in name
                ],
            },
            {
                "language": "nl",
                "message_id": "msg-nl",
                "subject": "Weekly ETF Pro Review | Nederlands",
                "recipient_hash": recipient_nl,
                "received_at_utc": "2026-08-05T20:01:01Z",
                "attachments": [
                    {"filename": name, "sha256": _sha(data)}
                    for name, data in files.items()
                    if "_nl_" in name
                ],
            },
        ],
    }
    receipt_path = _write(tmp_path / "receipts.json", receipts)
    return assurance_path, delivery_path, receipt_path


def test_level4_closeout_accepts_matching_bilingual_receipts(tmp_path: Path) -> None:
    assurance, delivery, receipts = _fixture(tmp_path)
    output = tmp_path / "closeout.json"
    record = build_delivery_closeout(
        release_assurance_path=assurance,
        delivery_manifest_path=delivery,
        receipt_evidence_path=receipts,
        output_path=output,
    )
    assert record["decision"] == "DELIVERY_CONFIRMED"
    validate_delivery_closeout(
        output,
        expected_run_id="20260805_210000",
        expected_close_date="2026-08-04",
        expected_report_token="260804",
    )


def test_level4_closeout_rejects_tampered_attachment(tmp_path: Path) -> None:
    assurance, delivery, receipts = _fixture(tmp_path)
    payload = json.loads(receipts.read_text(encoding="utf-8"))
    payload["messages"][0]["attachments"][0]["sha256"] = "0" * 64
    receipts.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "closeout.json"
    record = build_delivery_closeout(
        release_assurance_path=assurance,
        delivery_manifest_path=delivery,
        receipt_evidence_path=receipts,
        output_path=output,
    )
    assert record["decision"] == "FAIL"
    assert "received_artifact_hashes_consistent" in record["blockers"]
    with pytest.raises(RuntimeError, match="decision must be DELIVERY_CONFIRMED"):
        validate_delivery_closeout(output)


def test_level4_closeout_rejects_missing_dutch_receipt(tmp_path: Path) -> None:
    assurance, delivery, receipts = _fixture(tmp_path)
    payload = json.loads(receipts.read_text(encoding="utf-8"))
    payload["messages"] = [payload["messages"][0]]
    receipts.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "closeout.json"
    record = build_delivery_closeout(
        release_assurance_path=assurance,
        delivery_manifest_path=delivery,
        receipt_evidence_path=receipts,
        output_path=output,
    )
    assert record["decision"] == "FAIL"
    assert "independent_receipts_complete" in record["blockers"]
    assert "recipient_hashes_consistent" in record["blockers"]
