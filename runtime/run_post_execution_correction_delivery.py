from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from runtime.post_execution_correction_runbook import (
    DELIVERY_DIR,
    ROOT,
    STATE_PATH,
    LEDGER_PATH,
    asset_record,
    assert_authority_hashes_unchanged,
    assert_dispatch_send_confirmation,
    correction_request_from_env,
    delivery_environment,
    delivery_receipt_fields,
    relative,
    require_smtp_environment,
    resolve_executed_state_path,
    run_command,
    sha256,
    snapshot_authority_hashes,
)
from runtime.post_execution_report_surface import validate_post_execution_report_consistency


def main() -> None:
    request_path, request = correction_request_from_env(require_send_confirmation=True)
    assert_dispatch_send_confirmation(os.environ.get("ETF_CORRECTION_SEND_CONFIRMATION", ""))

    source_artifact = ROOT / request.source_artifact
    if not source_artifact.is_file():
        raise RuntimeError(f"Source execution artifact not found: {source_artifact}")

    env = delivery_environment(request)
    require_smtp_environment(env)
    authority_before = snapshot_authority_hashes()
    correction_run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    run_command(
        [
            sys.executable,
            "-m",
            "runtime.finalize_executed_etf_report",
            "--artifact",
            relative(source_artifact),
        ],
        env=env,
    )
    if not request.report_en.is_file() or request.report_en.stat().st_size <= 0:
        raise RuntimeError(f"Corrected English report was not created: {request.report_en}")
    if not request.report_nl.is_file() or request.report_nl.stat().st_size <= 0:
        raise RuntimeError(f"Corrected Dutch report was not created: {request.report_nl}")

    state_artifact = resolve_executed_state_path()
    state = json.loads(state_artifact.read_text(encoding="utf-8"))
    validate_post_execution_report_consistency(
        request.report_en.read_text(encoding="utf-8"), state, language="en"
    )
    validate_post_execution_report_consistency(
        request.report_nl.read_text(encoding="utf-8"), state, language="nl"
    )
    assert_authority_hashes_unchanged(authority_before)
    print(
        "ETF_CORRECTION_REPORT_SURFACE_OK | languages=EN,NL | "
        f"runtime_state={relative(state_artifact)}"
    )

    delivery_log = run_command([sys.executable, "send_report_runtime_html.py"], env=env)
    receipt = delivery_receipt_fields(delivery_log)
    authority_after = assert_authority_hashes_unchanged(authority_before)

    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = DELIVERY_DIR / (
        f"weekly_etf_correction_delivery_receipt_{request.report_date}_{correction_run_id}.txt"
    )
    receipt_path.write_text(delivery_log, encoding="utf-8")

    rendered_assets = {
        "en": {
            "report_path": asset_record(request.report_en),
            "clean_md_path": asset_record(request.report_en.with_name(f"{request.report_en.stem}_clean.md")),
            "html_path": asset_record(request.report_en.with_name(f"{request.report_en.stem}_delivery.html")),
            "pdf_path": asset_record(request.report_en.with_suffix(".pdf")),
            "equity_curve_png": asset_record(request.report_en.with_name(f"{request.report_en.stem}_equity_curve.png")),
        },
        "nl": {
            "report_path": asset_record(request.report_nl),
            "clean_md_path": asset_record(request.report_nl.with_name(f"{request.report_nl.stem}_clean.md")),
            "html_path": asset_record(request.report_nl.with_name(f"{request.report_nl.stem}_delivery.html")),
            "pdf_path": asset_record(request.report_nl.with_suffix(".pdf")),
            "equity_curve_png": asset_record(request.report_nl.with_name(f"{request.report_nl.stem}_equity_curve.png")),
        },
    }

    manifest = {
        "schema_version": "1.1",
        "correction_type": "post_execution_report_surface_correction",
        "status": "correction_rendered_and_delivery_layer_completed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "correction_run_id": correction_run_id,
        "original_run_id": request.original_run_id,
        "report_date": request.report_date,
        "request_file": relative(request_path),
        "source_execution_artifact": relative(source_artifact),
        "source_execution_artifact_sha256": sha256(source_artifact),
        "executed_runtime_state": relative(state_artifact),
        "executed_runtime_state_sha256": sha256(state_artifact),
        "model_execution_replayed": False,
        "official_state_mutated": False,
        "official_trade_ledger_mutated": False,
        "state_sha256_before": authority_before["state"],
        "state_sha256_after": authority_after["state"],
        "trade_ledger_sha256_before": authority_before["ledger"],
        "trade_ledger_sha256_after": authority_after["ledger"],
        "rendered_assets": rendered_assets,
        "delivery_receipt_path": relative(receipt_path),
        "delivery_receipt_sha256": sha256(receipt_path),
        "delivery_receipt_line": receipt["line"],
        "delivery_receipt_fields": receipt["fields"],
        "delivery_text_manifests": [
            receipt["fields"]["manifest_en"],
            receipt["fields"]["manifest_nl"],
        ],
        "delivery_layer_status": "smtp_sendmail_returned_no_exception",
        "inbox_receipt_status": "pending_external_verification",
        "inbox_receipts": [],
    }
    manifest_path = DELIVERY_DIR / (
        f"weekly_etf_correction_manifest_{request.report_date}_{correction_run_id}.json"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        "ETF_CORRECTION_MANIFEST_OK | "
        f"path={relative(manifest_path)} | receipt_contract=text | "
        "state_immutable=true | ledger_immutable=true"
    )


if __name__ == "__main__":
    main()
