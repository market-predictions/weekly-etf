from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, MutableMapping

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
DELIVERY_DIR = OUTPUT_DIR / "delivery"
STATE_PATH = OUTPUT_DIR / "etf_portfolio_state.json"
LEDGER_PATH = OUTPUT_DIR / "etf_trade_ledger.csv"
LATEST_EXECUTED_STATE_POINTER = OUTPUT_DIR / "runtime/latest_etf_report_state_path.txt"
DEFAULT_REQUEST = ROOT / "control/run_queue/weekly_etf_report_correction_request_20260715_230541.md"

SEND_CONFIRMATION = "confirm_correction_resend"
DELIVERY_OK_PREFIX = "DELIVERY_OK | mode=pro_bilingual"
SMTP_ENV_KEYS = (
    "MRKT_RPRTS_SMTP_HOST",
    "MRKT_RPRTS_SMTP_PORT",
    "MRKT_RPRTS_SMTP_USER",
    "MRKT_RPRTS_SMTP_PASS",
    "MRKT_RPRTS_MAIL_FROM",
    "MRKT_RPRTS_MAIL_TO",
    "MRKT_RPRTS_MAIL_TO_NL",
)


@dataclass(frozen=True)
class CorrectionRequest:
    source_artifact: str
    report_token: str
    correction_suffix: str
    original_run_id: str
    report_date: str
    send_confirmation: str

    @property
    def report_en(self) -> Path:
        return OUTPUT_DIR / f"weekly_analysis_pro_{self.report_token}_{self.correction_suffix}.md"

    @property
    def report_nl(self) -> Path:
        return OUTPUT_DIR / f"weekly_analysis_pro_nl_{self.report_token}_{self.correction_suffix}.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def resolve_repo_path(raw: str | Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def parse_request(path: Path, *, require_send_confirmation: bool) -> CorrectionRequest:
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

    request = CorrectionRequest(**{key: values[key] for key in required})
    if not request.report_token.isdigit() or len(request.report_token) != 6:
        raise RuntimeError(f"Invalid report_token: {request.report_token!r}")
    if not request.correction_suffix.isdigit() or len(request.correction_suffix) != 2:
        raise RuntimeError(f"Invalid correction_suffix: {request.correction_suffix!r}")
    if require_send_confirmation and request.send_confirmation != SEND_CONFIRMATION:
        raise RuntimeError("Correction resend is not explicitly confirmed.")
    return request


def assert_dispatch_send_confirmation(value: str) -> None:
    if value != SEND_CONFIRMATION:
        raise RuntimeError("Workflow dispatch did not provide the exact correction resend confirmation.")


def require_smtp_environment(env: Mapping[str, str]) -> None:
    missing = [key for key in SMTP_ENV_KEYS if not str(env.get(key, "")).strip()]
    if missing:
        raise RuntimeError(f"Missing production SMTP configuration: {', '.join(missing)}")


def recovery_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    for key in SMTP_ENV_KEYS:
        env.pop(key, None)
    env["MRKT_RPRTS_DRY_RUN_EMAIL"] = "1"
    env["ETF_CORRECTION_MODE"] = "recover_no_send"
    return env


def delivery_environment(request: CorrectionRequest, base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(base or os.environ)
    env.update(
        {
            "MRKT_RPRTS_REPORT_MODE": "pro",
            "MRKT_RPRTS_SUBJECT_PREFIX": "Corrected Weekly ETF Pro Review",
            "MRKT_RPRTS_SUBJECT_PREFIX_NL": "Gecorrigeerde Weekly ETF Pro Review | Nederlands",
            "MRKT_RPRTS_DRY_RUN_EMAIL": "0",
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH": relative(request.report_en),
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL": relative(request.report_nl),
            "ETF_CORRECTION_MODE": "send",
        }
    )
    return env


def render_environment(request: CorrectionRequest, base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = recovery_environment(base)
    env.update(
        {
            "MRKT_RPRTS_REPORT_MODE": "pro",
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH": relative(request.report_en),
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL": relative(request.report_nl),
        }
    )
    return env


def run_command(command: list[str], *, env: Mapping[str, str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=dict(env),
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


def resolve_executed_state_path() -> Path:
    if not LATEST_EXECUTED_STATE_POINTER.is_file():
        raise RuntimeError(f"Executed-state pointer missing: {LATEST_EXECUTED_STATE_POINTER}")
    raw = LATEST_EXECUTED_STATE_POINTER.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError("Executed-state pointer is empty.")
    path = resolve_repo_path(raw)
    if not path.is_file():
        raise RuntimeError(f"Executed-state artifact missing: {path}")
    return path


def snapshot_authority_hashes() -> dict[str, str]:
    return {"state": sha256(STATE_PATH), "ledger": sha256(LEDGER_PATH)}


def assert_authority_hashes_unchanged(before: Mapping[str, str]) -> dict[str, str]:
    after = snapshot_authority_hashes()
    if after["state"] != before["state"]:
        raise RuntimeError("Correction operation mutated official portfolio state.")
    if after["ledger"] != before["ledger"]:
        raise RuntimeError("Correction operation mutated official trade ledger.")
    return after


def delivery_receipt_fields(log_text: str) -> dict[str, Any]:
    line = next((row.strip() for row in log_text.splitlines() if row.startswith(DELIVERY_OK_PREFIX)), "")
    if not line:
        raise RuntimeError("Delivery transcript lacks bilingual DELIVERY_OK receipt.")

    fields: dict[str, str] = {}
    for part in line.split("|")[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key.strip()] = value.strip()

    required = {
        "mode": "pro_bilingual",
        "pdf_en": "yes",
        "pdf_nl": "yes",
        "html_body_en": "full_report",
        "html_body_nl": "full_report",
    }
    for key, expected in required.items():
        if fields.get(key) != expected:
            raise RuntimeError(f"Delivery receipt field {key!r} expected {expected!r}, found {fields.get(key)!r}.")

    for key in ("manifest_en", "manifest_nl"):
        value = fields.get(key, "")
        if not value.endswith("_delivery_manifest.txt"):
            raise RuntimeError(f"Delivery receipt does not identify a production text manifest for {key}: {value!r}")

    return {"line": line, "fields": fields}


def validate_existing_correction_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("model_execution_replayed") is not False:
        raise RuntimeError("Correction manifest does not prove model execution was avoided.")
    if payload.get("official_state_mutated") is not False:
        raise RuntimeError("Correction manifest does not prove state immutability.")
    if payload.get("official_trade_ledger_mutated") is not False:
        raise RuntimeError("Correction manifest does not prove trade-ledger immutability.")
    if payload.get("state_sha256_before") != payload.get("state_sha256_after"):
        raise RuntimeError("Correction manifest state hashes differ.")
    if payload.get("trade_ledger_sha256_before") != payload.get("trade_ledger_sha256_after"):
        raise RuntimeError("Correction manifest trade-ledger hashes differ.")

    receipt_path_raw = str(payload.get("delivery_receipt_path") or "").strip()
    if not receipt_path_raw:
        raise RuntimeError("Correction manifest lacks delivery_receipt_path.")
    receipt_path = resolve_repo_path(receipt_path_raw)
    receipt = delivery_receipt_fields(receipt_path.read_text(encoding="utf-8"))
    recorded_line = str(payload.get("delivery_receipt_line") or "")
    if recorded_line and recorded_line != receipt["line"]:
        raise RuntimeError("Correction manifest receipt line does not match the persisted text receipt.")
    return payload


def asset_record(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size <= 0:
        raise RuntimeError(f"Expected correction asset missing or empty: {path}")
    return {"path": relative(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def correction_request_from_env(*, require_send_confirmation: bool) -> tuple[Path, CorrectionRequest]:
    path = resolve_repo_path(os.environ.get("ETF_CORRECTION_REQUEST_FILE", str(DEFAULT_REQUEST)))
    return path, parse_request(path, require_send_confirmation=require_send_confirmation)


def prove_recovery_has_no_smtp(env: Mapping[str, str]) -> None:
    leaked = [key for key in SMTP_ENV_KEYS if str(env.get(key, "")).strip()]
    if leaked:
        raise RuntimeError(f"Recovery environment contains SMTP credentials: {', '.join(leaked)}")
    if env.get("MRKT_RPRTS_DRY_RUN_EMAIL") != "1":
        raise RuntimeError("Recovery environment is not explicitly no-send.")
