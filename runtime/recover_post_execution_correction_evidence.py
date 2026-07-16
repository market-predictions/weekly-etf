from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from runtime.post_execution_correction_runbook import (
    DELIVERY_DIR,
    OUTPUT_DIR,
    ROOT,
    asset_record,
    assert_authority_hashes_unchanged,
    correction_request_from_env,
    delivery_receipt_fields,
    prove_recovery_has_no_smtp,
    relative,
    render_environment,
    resolve_executed_state_path,
    resolve_repo_path,
    run_command,
    sha256,
    snapshot_authority_hashes,
)
from runtime.post_execution_report_surface import validate_post_execution_report_consistency


def _persist_receipt_without_overwrite(path: Path, text: str) -> None:
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing != text:
            raise RuntimeError(f"Refusing to overwrite different historical delivery receipt: {path}")
        return
    path.write_text(text, encoding="utf-8")


def main() -> None:
    request_path, request = correction_request_from_env(require_send_confirmation=False)

    delivery_log_raw = os.environ.get("ETF_PRIOR_CORRECTION_DELIVERY_LOG", "").strip()
    if not delivery_log_raw:
        raise RuntimeError("ETF_PRIOR_CORRECTION_DELIVERY_LOG is required for no-send recovery.")
    delivery_log_path = resolve_repo_path(delivery_log_raw)
    if not delivery_log_path.is_file():
        raise RuntimeError(f"Prior correction delivery transcript missing: {delivery_log_path}")
    delivery_log_text = delivery_log_path.read_text(encoding="utf-8")
    receipt = delivery_receipt_fields(delivery_log_text)

    source_artifact = ROOT / request.source_artifact
    if not source_artifact.is_file():
        raise RuntimeError(f"Source execution artifact missing: {source_artifact}")

    env = render_environment(request)
    prove_recovery_has_no_smtp(env)
    authority_before = snapshot_authority_hashes()

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

    state_artifact = resolve_executed_state_path()
    state = json.loads(state_artifact.read_text(encoding="utf-8"))
    validate_post_execution_report_consistency(
        request.report_en.read_text(encoding="utf-8"), state, language="en"
    )
    validate_post_execution_report_consistency(
        request.report_nl.read_text(encoding="utf-8"), state, language="nl"
    )

    import send_report_runtime_html as runtime_html

    report_module = runtime_html.report_module
    bundle = report_module.generate_delivery_assets_for_run(OUTPUT_DIR, request.report_en, mode="pro")
    if not bundle.get("bilingual"):
        raise RuntimeError("Recovery render did not produce a bilingual asset bundle.")

    asset_keys = ["report_path", "clean_md_path", "html_path", "pdf_path", "equity_curve_png"]
    rendered_assets: dict[str, dict[str, dict[str, object]]] = {"en": {}, "nl": {}}
    for language in ("en", "nl"):
        assets = bundle[language]
        for key in asset_keys:
            raw = assets.get(key)
            if raw is None:
                raise RuntimeError(f"Recovery bundle missing {language}.{key}")
            rendered_assets[language][key] = asset_record(Path(raw))

    authority_after = assert_authority_hashes_unchanged(authority_before)

    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)
    prior_run_id = os.environ.get("ETF_PRIOR_CORRECTION_WORKFLOW_RUN_ID", "unknown").strip() or "unknown"
    receipt_path = DELIVERY_DIR / (
        f"weekly_etf_correction_delivery_receipt_{request.report_date}_{prior_run_id}.txt"
    )
    _persist_receipt_without_overwrite(receipt_path, delivery_log_text)

    created_at = datetime.now(timezone.utc)
    recovery_run_id = created_at.strftime("%Y%m%d_%H%M%S")
    manifest = {
        "schema_version": "1.1",
        "correction_type": "post_execution_report_surface_correction",
        "status": "correction_rendered_delivered_and_evidence_recovered",
        "created_at_utc": created_at.isoformat(),
        "recovery_run_id": recovery_run_id,
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
        "delivery_workflow_run_id": prior_run_id,
        "delivery_receipt_path": relative(receipt_path),
        "delivery_receipt_sha256": sha256(receipt_path),
        "delivery_receipt_line": receipt["line"],
        "delivery_receipt_fields": receipt["fields"],
        "delivery_text_manifests": [
            receipt["fields"]["manifest_en"],
            receipt["fields"]["manifest_nl"],
        ],
        "delivery_layer_status": "smtp_sendmail_returned_no_exception",
        "recovery_email_send": False,
        "inbox_receipt_status": "pending_external_verification",
        "inbox_receipts": [],
    }
    manifest_path = DELIVERY_DIR / (
        f"weekly_etf_correction_manifest_{request.report_date}_{recovery_run_id}.json"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        "ETF_CORRECTION_EVIDENCE_RECOVERY_OK | "
        f"manifest={relative(manifest_path)} | delivery_run={prior_run_id} | "
        "email_send=false | state_immutable=true | ledger_immutable=true"
    )


if __name__ == "__main__":
    main()
