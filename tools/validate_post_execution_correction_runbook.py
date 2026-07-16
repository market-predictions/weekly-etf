from __future__ import annotations

from runtime.post_execution_correction_runbook import ROOT, validate_existing_correction_manifest

WORKFLOW = ROOT / ".github/workflows/resend-corrected-post-execution-report.yml"
BRIDGE = ROOT / ".github/workflows/dispatch-corrected-etf-report-bridge.yml"
SENDER = ROOT / "runtime/run_post_execution_correction_delivery.py"
RECOVERY = ROOT / "runtime/recover_post_execution_correction_evidence.py"
MANIFEST = ROOT / "output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json"

PRODUCTION_SECRET_KEYS = (
    "MRKT_RPRTS_SMTP_HOST",
    "MRKT_RPRTS_SMTP_PORT",
    "MRKT_RPRTS_SMTP_USER",
    "MRKT_RPRTS_SMTP_PASS",
    "MRKT_RPRTS_MAIL_FROM",
    "MRKT_RPRTS_MAIL_TO",
    "MRKT_RPRTS_MAIL_TO_NL",
)
OBSOLETE_ENV_PREFIXES = (
    "MAIL_USERNAME:",
    "MAIL_PASSWORD:",
    "MAIL_TO:",
    "MAIL_TO_NL:",
    "SMTP_SERVER:",
    "SMTP_PORT:",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    workflow_lines = [line.strip() for line in workflow.splitlines()]
    sender = SENDER.read_text(encoding="utf-8")
    recovery = RECOVERY.read_text(encoding="utf-8")

    require("workflow_dispatch:" in workflow, "Canonical correction workflow is not manual-dispatch controlled.")
    require("push:" not in workflow_lines, "Canonical correction workflow still has an automatic push send trigger.")
    for mode in ("validate_only", "recover_no_send", "send"):
        require(mode in workflow, f"Canonical correction workflow lacks mode: {mode}")
    for key in PRODUCTION_SECRET_KEYS:
        require(key in workflow, f"Canonical correction workflow lacks production secret key: {key}")
    for prefix in OBSOLETE_ENV_PREFIXES:
        require(
            not any(line.startswith(prefix) for line in workflow_lines),
            f"Canonical correction workflow still contains obsolete environment key: {prefix}",
        )

    require(not BRIDGE.exists(), "One-shot correction dispatch bridge has not been retired.")
    require("assert_dispatch_send_confirmation" in sender, "Send runner lacks dispatch confirmation guard.")
    require("require_smtp_environment" in sender, "Send runner lacks production SMTP configuration guard.")
    require("delivery_receipt_fields" in sender, "Send runner does not validate the text delivery receipt.")
    require("Expected English and Dutch delivery manifests" not in sender, "Send runner retains obsolete JSON-manifest assumption.")
    require("delivery_text_manifests" in sender, "Send manifest does not record production text manifests.")

    require("prove_recovery_has_no_smtp" in recovery, "Recovery runner lacks explicit no-SMTP proof.")
    require("run_post_execution_correction_delivery" not in recovery, "Recovery runner invokes the send runner.")
    require("send_report_runtime_html.py" not in recovery, "Recovery runner invokes the SMTP delivery entrypoint.")
    require("generate_delivery_assets_for_run" in recovery, "Recovery runner does not use render-only asset generation.")
    require("Refusing to overwrite different historical delivery receipt" in recovery, "Recovery can overwrite historical receipt evidence.")

    validate_existing_correction_manifest(MANIFEST)

    print(
        "ETF_POST_EXECUTION_CORRECTION_RUNBOOK_OK | "
        "automatic_send_trigger=false | receipt_contract=text | "
        "recovery_email_send=false | bridge_retired=true | "
        "historical_manifest_internal_hashes=valid"
    )


if __name__ == "__main__":
    main()
