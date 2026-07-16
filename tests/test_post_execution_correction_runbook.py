from __future__ import annotations

from pathlib import Path

import pytest

from runtime.post_execution_correction_runbook import (
    SEND_CONFIRMATION,
    SMTP_ENV_KEYS,
    assert_dispatch_send_confirmation,
    delivery_receipt_fields,
    parse_request,
    prove_recovery_has_no_smtp,
    recovery_environment,
    validate_existing_correction_manifest,
)

VALID_RECEIPT = (
    "DELIVERY_OK | mode=pro_bilingual | report_en=weekly_analysis_pro_260714_03.md | "
    "report_nl=weekly_analysis_pro_nl_260714_03.md | html_body_en=full_report | "
    "html_body_nl=full_report | pdf_en=yes | pdf_nl=yes | "
    "manifest_en=weekly_analysis_pro_260714_03_delivery_manifest.txt | "
    "manifest_nl=weekly_analysis_pro_nl_260714_03_delivery_manifest.txt"
)


def _write_request(path: Path, confirmation: str) -> None:
    path.write_text(
        "source_artifact: output/runtime/example.json\n"
        "report_token: 260714\n"
        "correction_suffix: 03\n"
        "original_run_id: 20260715_175910\n"
        "report_date: 2026-07-14\n"
        f"send_confirmation: {confirmation}\n",
        encoding="utf-8",
    )


def test_send_request_requires_exact_confirmation(tmp_path: Path) -> None:
    request = tmp_path / "request.md"
    _write_request(request, "not_confirmed")
    with pytest.raises(RuntimeError, match="not explicitly confirmed"):
        parse_request(request, require_send_confirmation=True)
    _write_request(request, SEND_CONFIRMATION)
    assert parse_request(request, require_send_confirmation=True).send_confirmation == SEND_CONFIRMATION


def test_dispatch_requires_independent_exact_confirmation() -> None:
    with pytest.raises(RuntimeError, match="exact correction resend confirmation"):
        assert_dispatch_send_confirmation("not_confirmed")
    assert_dispatch_send_confirmation(SEND_CONFIRMATION)


def test_recovery_environment_strips_mail_configuration() -> None:
    source = {key: "configured" for key in SMTP_ENV_KEYS}
    env = recovery_environment(source)
    prove_recovery_has_no_smtp(env)
    assert env["MRKT_RPRTS_DRY_RUN_EMAIL"] == "1"
    assert env["ETF_CORRECTION_MODE"] == "recover_no_send"
    assert all(key not in env for key in SMTP_ENV_KEYS)


def test_recovery_rejects_mail_configuration_leak() -> None:
    env = recovery_environment({})
    env[SMTP_ENV_KEYS[0]] = "configured"
    with pytest.raises(RuntimeError, match="contains SMTP credentials"):
        prove_recovery_has_no_smtp(env)


def test_text_receipt_contract_accepts_text_manifests() -> None:
    receipt = delivery_receipt_fields(VALID_RECEIPT)
    assert receipt["fields"]["manifest_en"].endswith("_delivery_manifest.txt")
    assert receipt["fields"]["manifest_nl"].endswith("_delivery_manifest.txt")


def test_text_receipt_contract_rejects_json_manifests() -> None:
    invalid = VALID_RECEIPT.replace("_delivery_manifest.txt", "_delivery_manifest.json")
    with pytest.raises(RuntimeError, match="production text manifest"):
        delivery_receipt_fields(invalid)


def test_text_receipt_contract_rejects_missing_pdf_confirmation() -> None:
    with pytest.raises(RuntimeError, match="pdf_nl"):
        delivery_receipt_fields(VALID_RECEIPT.replace("pdf_nl=yes", "pdf_nl=no"))


def test_closed_correction_manifest_still_validates() -> None:
    path = Path("output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json")
    payload = validate_existing_correction_manifest(path)
    assert payload["official_state_mutated"] is False
    assert payload["official_trade_ledger_mutated"] is False
    assert payload["state_sha256_before"] == payload["state_sha256_after"]
    assert payload["trade_ledger_sha256_before"] == payload["trade_ledger_sha256_after"]


def test_recovery_source_never_invokes_delivery_entrypoint() -> None:
    source = Path("runtime/recover_post_execution_correction_evidence.py").read_text(encoding="utf-8")
    assert "send_report_runtime_html.py" not in source
    assert "generate_delivery_assets_for_run" in source
    assert "prove_recovery_has_no_smtp" in source
