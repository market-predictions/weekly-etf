from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from runtime.post_execution_report_surface import validate_post_execution_report_consistency


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "control/run_queue/weekly_etf_report_correction_request_20260715_230541.md"
STATE_PATH = ROOT / "output/etf_portfolio_state.json"
LEDGER_PATH = ROOT / "output/etf_trade_ledger.csv"
DELIVERY_DIR = ROOT / "output/delivery"


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
        raise RuntimeError("Correction resend is not explicitly confirmed.")
    return values


def run(command: list[str], *, env: dict[str, str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
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


def main() -> None:
    request_path = Path(os.environ.get("ETF_CORRECTION_REQUEST_FILE", str(DEFAULT_REQUEST)))
    if not request_path.is_absolute():
        request_path = ROOT / request_path
    request = parse_request(request_path)

    source_artifact = ROOT / request["source_artifact"]
    if not source_artifact.is_file():
        raise RuntimeError(f"Source execution artifact not found: {source_artifact}")

    report_token = request["report_token"]
    suffix = request["correction_suffix"]
    report_en = ROOT / f"output/weekly_analysis_pro_{report_token}_{suffix}.md"
    report_nl = ROOT / f"output/weekly_analysis_pro_nl_{report_token}_{suffix}.md"
    correction_run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    state_before = sha256(STATE_PATH)
    ledger_before = sha256(LEDGER_PATH)
    delivery_before = {path.name for path in DELIVERY_DIR.glob("*") if path.is_file()}

    env = dict(os.environ)
    env.update(
        {
            "MRKT_RPRTS_REPORT_MODE": "pro",
            "MRKT_RPRTS_SUBJECT_PREFIX": "Corrected Weekly ETF Pro Review",
            "MRKT_RPRTS_SUBJECT_PREFIX_NL": "Gecorrigeerde Weekly ETF Pro Review | Nederlands",
            "MRKT_RPRTS_DRY_RUN_EMAIL": "0",
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH": str(report_en.relative_to(ROOT)),
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL": str(report_nl.relative_to(ROOT)),
        }
    )

    run(
        [
            sys.executable,
            "-m",
            "runtime.finalize_executed_etf_report",
            "--artifact",
            str(source_artifact.relative_to(ROOT)),
        ],
        env=env,
    )

    if not report_en.is_file() or not report_en.stat().st_size:
        raise RuntimeError(f"Corrected English report was not created: {report_en}")
    if not report_nl.is_file() or not report_nl.stat().st_size:
        raise RuntimeError(f"Corrected Dutch report was not created: {report_nl}")

    artifact = json.loads(source_artifact.read_text(encoding="utf-8"))
    state_artifact = ROOT / str(artifact["post_execution_state_artifact"])
    state = json.loads(state_artifact.read_text(encoding="utf-8"))
    validate_post_execution_report_consistency(report_en.read_text(encoding="utf-8"), state, language="en")
    validate_post_execution_report_consistency(report_nl.read_text(encoding="utf-8"), state, language="nl")
    print("ETF_CORRECTION_REPORT_SURFACE_OK | languages=EN,NL | mutation=URNM->XBI")

    if sha256(STATE_PATH) != state_before or sha256(LEDGER_PATH) != ledger_before:
        raise RuntimeError("Correction finalization mutated official state or trade ledger.")

    delivery_log = run([sys.executable, "send_report_runtime_html.py"], env=env)
    if "DELIVERY_OK | mode=pro_bilingual" not in delivery_log:
        raise RuntimeError("Delivery entrypoint did not emit the bilingual DELIVERY_OK receipt.")

    state_after = sha256(STATE_PATH)
    ledger_after = sha256(LEDGER_PATH)
    if state_after != state_before:
        raise RuntimeError("Correction delivery mutated official portfolio state.")
    if ledger_after != ledger_before:
        raise RuntimeError("Correction delivery mutated official trade ledger.")

    delivery_after = {path.name for path in DELIVERY_DIR.glob("*") if path.is_file()}
    new_delivery_files = sorted(delivery_after - delivery_before)
    delivery_manifests: list[str] = []
    delivery_statuses: list[str] = []
    for name in new_delivery_files:
        path = DELIVERY_DIR / name
        if path.suffix != ".json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "delivery_status" in payload:
            delivery_manifests.append(str(path.relative_to(ROOT)))
            delivery_statuses.append(str(payload.get("delivery_status")))

    if len(delivery_manifests) < 2:
        raise RuntimeError(f"Expected English and Dutch delivery manifests; found {delivery_manifests}")
    if any(status != "smtp_sendmail_returned_no_exception" for status in delivery_statuses):
        raise RuntimeError(f"Unexpected delivery statuses: {delivery_statuses}")

    manifest = {
        "schema_version": "1.0",
        "correction_type": "post_execution_report_surface_correction",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "correction_run_id": correction_run_id,
        "original_run_id": request["original_run_id"],
        "report_date": request["report_date"],
        "request_file": str(request_path.relative_to(ROOT)),
        "source_execution_artifact": str(source_artifact.relative_to(ROOT)),
        "source_execution_artifact_sha256": sha256(source_artifact),
        "model_execution_replayed": False,
        "official_state_mutated": False,
        "official_trade_ledger_mutated": False,
        "state_sha256_before": state_before,
        "state_sha256_after": state_after,
        "trade_ledger_sha256_before": ledger_before,
        "trade_ledger_sha256_after": ledger_after,
        "corrected_report_en": str(report_en.relative_to(ROOT)),
        "corrected_report_en_sha256": sha256(report_en),
        "corrected_report_nl": str(report_nl.relative_to(ROOT)),
        "corrected_report_nl_sha256": sha256(report_nl),
        "new_delivery_files": [str((DELIVERY_DIR / name).relative_to(ROOT)) for name in new_delivery_files],
        "delivery_manifests": delivery_manifests,
        "delivery_statuses": delivery_statuses,
        "delivery_log_status": "DELIVERY_OK",
        "email_receipt_status": "not_checked_by_workflow",
        "status": "correction_rendered_and_delivery_layer_completed",
    }
    manifest_path = DELIVERY_DIR / f"weekly_etf_correction_manifest_{request['report_date']}_{correction_run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"ETF_CORRECTION_MANIFEST_OK | path={manifest_path.relative_to(ROOT)} | delivery_manifests={len(delivery_manifests)}")


if __name__ == "__main__":
    main()
