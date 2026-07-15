from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.post_execution_report_surface import validate_post_execution_report_consistency


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
DELIVERY_DIR = OUTPUT_DIR / "delivery"
STATE_PATH = OUTPUT_DIR / "etf_portfolio_state.json"
LEDGER_PATH = OUTPUT_DIR / "etf_trade_ledger.csv"
LATEST_STATE_POINTER = OUTPUT_DIR / "runtime/latest_etf_report_state_path.txt"
DEFAULT_REQUEST = ROOT / "control/run_queue/weekly_etf_report_correction_request_20260715_230541.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_request(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if ":" not in raw or raw.lstrip().startswith("#"):
            continue
        key, value = raw.split(":", 1)
        values[key.strip()] = value.strip()
    required = {
        "source_artifact",
        "report_token",
        "correction_suffix",
        "original_run_id",
        "report_date",
        "send_confirmation",
    }
    missing = sorted(required - values.keys())
    if missing:
        raise RuntimeError(f"Correction request missing fields: {', '.join(missing)}")
    if values["send_confirmation"] != "confirm_correction_resend":
        raise RuntimeError("Correction request is not explicitly confirmed.")
    return values


def run(command: list[str], *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env or os.environ.copy(),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")
    return result.stdout


def resolve_state_path() -> Path:
    if not LATEST_STATE_POINTER.is_file():
        raise RuntimeError(f"Executed-state pointer missing: {LATEST_STATE_POINTER}")
    raw = LATEST_STATE_POINTER.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError("Executed-state pointer is empty.")
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        raise RuntimeError(f"Executed-state artifact missing: {path}")
    return path


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def asset_record(path: Path) -> dict[str, Any]:
    if not path.is_file() or not path.stat().st_size:
        raise RuntimeError(f"Expected recovery asset missing or empty: {path}")
    return {
        "path": relative(path),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def delivery_receipt_fields(log_text: str) -> dict[str, Any]:
    line = next(
        (row.strip() for row in log_text.splitlines() if row.startswith("DELIVERY_OK | mode=pro_bilingual")),
        "",
    )
    if not line:
        raise RuntimeError("Prior delivery transcript lacks bilingual DELIVERY_OK receipt.")
    fields: dict[str, str] = {}
    for part in line.split("|")[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key.strip()] = value.strip()
    if fields.get("pdf_en") != "yes" or fields.get("pdf_nl") != "yes":
        raise RuntimeError(f"Prior delivery receipt does not confirm both PDFs: {line}")
    return {"line": line, "fields": fields}


def main() -> None:
    request_path = Path(os.environ.get("ETF_CORRECTION_REQUEST_FILE", str(DEFAULT_REQUEST)))
    if not request_path.is_absolute():
        request_path = ROOT / request_path
    request = parse_request(request_path)

    delivery_log_path = Path(os.environ.get("ETF_PRIOR_CORRECTION_DELIVERY_LOG", ""))
    if not delivery_log_path.is_absolute():
        delivery_log_path = ROOT / delivery_log_path
    if not delivery_log_path.is_file():
        raise RuntimeError(f"Prior correction delivery transcript missing: {delivery_log_path}")
    delivery_log_text = delivery_log_path.read_text(encoding="utf-8")
    receipt = delivery_receipt_fields(delivery_log_text)

    source_artifact = ROOT / request["source_artifact"]
    if not source_artifact.is_file():
        raise RuntimeError(f"Source execution artifact missing: {source_artifact}")

    token = request["report_token"]
    suffix = request["correction_suffix"]
    report_en = OUTPUT_DIR / f"weekly_analysis_pro_{token}_{suffix}.md"
    report_nl = OUTPUT_DIR / f"weekly_analysis_pro_nl_{token}_{suffix}.md"

    state_before = sha256(STATE_PATH)
    ledger_before = sha256(LEDGER_PATH)

    env = os.environ.copy()
    env.update(
        {
            "MRKT_RPRTS_REPORT_MODE": "pro",
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH": relative(report_en),
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL": relative(report_nl),
        }
    )
    run(
        [
            sys.executable,
            "-m",
            "runtime.finalize_executed_etf_report",
            "--artifact",
            relative(source_artifact),
        ],
        env=env,
    )

    state_artifact = resolve_state_path()
    state = json.loads(state_artifact.read_text(encoding="utf-8"))
    validate_post_execution_report_consistency(report_en.read_text(encoding="utf-8"), state, language="en")
    validate_post_execution_report_consistency(report_nl.read_text(encoding="utf-8"), state, language="nl")

    import send_report_runtime_html as runtime_html

    report_module = runtime_html.report_module
    bundle = report_module.generate_delivery_assets_for_run(OUTPUT_DIR, report_en, mode="pro")
    if not bundle.get("bilingual"):
        raise RuntimeError("Recovery render did not produce a bilingual asset bundle.")

    asset_keys = ["report_path", "clean_md_path", "html_path", "pdf_path", "equity_curve_png"]
    rendered_assets: dict[str, dict[str, dict[str, Any]]] = {"en": {}, "nl": {}}
    for language in ("en", "nl"):
        assets = bundle[language]
        for key in asset_keys:
            raw = assets.get(key)
            if raw is None:
                raise RuntimeError(f"Recovery bundle missing {language}.{key}")
            rendered_assets[language][key] = asset_record(Path(raw))

    state_after = sha256(STATE_PATH)
    ledger_after = sha256(LEDGER_PATH)
    if state_after != state_before:
        raise RuntimeError("Evidence recovery mutated official portfolio state.")
    if ledger_after != ledger_before:
        raise RuntimeError("Evidence recovery mutated official trade ledger.")

    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)
    prior_run_id = os.environ.get("ETF_PRIOR_CORRECTION_WORKFLOW_RUN_ID", "29455717158").strip()
    receipt_path = DELIVERY_DIR / f"weekly_etf_correction_delivery_receipt_{request['report_date']}_{prior_run_id}.txt"
    shutil.copyfile(delivery_log_path, receipt_path)

    created_at = datetime.now(timezone.utc)
    recovery_run_id = created_at.strftime("%Y%m%d_%H%M%S")
    manifest = {
        "schema_version": "1.0",
        "correction_type": "post_execution_report_surface_correction",
        "status": "correction_rendered_delivered_and_evidence_recovered",
        "created_at_utc": created_at.isoformat(),
        "recovery_run_id": recovery_run_id,
        "original_run_id": request["original_run_id"],
        "report_date": request["report_date"],
        "request_file": relative(request_path),
        "source_execution_artifact": relative(source_artifact),
        "source_execution_artifact_sha256": sha256(source_artifact),
        "executed_runtime_state": relative(state_artifact),
        "executed_runtime_state_sha256": sha256(state_artifact),
        "model_execution_replayed": False,
        "official_state_mutated": False,
        "official_trade_ledger_mutated": False,
        "state_sha256_before": state_before,
        "state_sha256_after": state_after,
        "trade_ledger_sha256_before": ledger_before,
        "trade_ledger_sha256_after": ledger_after,
        "rendered_assets": rendered_assets,
        "delivery_workflow_run_id": prior_run_id,
        "delivery_receipt_path": relative(receipt_path),
        "delivery_receipt_sha256": sha256(receipt_path),
        "delivery_receipt_line": receipt["line"],
        "delivery_receipt_fields": receipt["fields"],
        "delivery_layer_status": "smtp_sendmail_returned_no_exception",
        "inbox_receipt_status": "pending_external_verification",
        "inbox_receipts": [],
    }
    manifest_path = DELIVERY_DIR / f"weekly_etf_correction_manifest_{request['report_date']}_{recovery_run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        "ETF_CORRECTION_EVIDENCE_RECOVERY_OK | "
        f"manifest={relative(manifest_path)} | delivery_run={prior_run_id} | state_immutable=true | ledger_immutable=true"
    )


if __name__ == "__main__":
    main()
