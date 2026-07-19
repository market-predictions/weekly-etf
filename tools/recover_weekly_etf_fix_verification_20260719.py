from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report_runtime_html as srh

RUN_ID = "20260719_002755"
REQUESTED_CLOSE_DATE = "2026-07-17"
REPORT_TOKEN = "260717"
EN_REPORT = Path("output/weekly_analysis_pro_260717_04.md")
NL_REPORT = Path("output/weekly_analysis_pro_nl_260717_04.md")
RUNTIME_STATE = Path("output/runtime/etf_report_state_20260717_20260719_002755.json")
PRICING_AUDIT = Path("output/pricing/price_audit_2026-07-17_20260719_002755.json")
EXECUTION_ARTIFACT = Path(
    "output/runtime/etf_model_execution_20260717_20260719_002755_not_authorized.json"
)
RUN_MANIFEST = Path(
    "output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260719_002755.json"
)
DELIVERY_MANIFEST = Path(
    "output/delivery/weekly_etf_delivery_manifest_2026-07-17_20260719_002755.json"
)
SNAPSHOT = Path("/tmp/weekly-etf-fix-verification-delivery-authority.json")
PROTECTED = (
    Path("output/etf_portfolio_state.json"),
    Path("output/etf_trade_ledger.csv"),
    Path("output/etf_valuation_history.csv"),
)
EXPECTED_WEIGHTS = {
    "PAVE": (0.0, 4.94),
    "XLU": (5.4908, 0.52),
}


def _run(*args: str, capture: bool = False) -> str:
    print("ETF_FIX_VERIFICATION_COMMAND | " + " ".join(args))
    completed = subprocess.run(
        args,
        check=True,
        text=True,
        capture_output=capture,
    )
    if capture:
        output = (completed.stdout or "").strip()
        if output:
            print(output)
        if completed.stderr:
            print(completed.stderr.strip(), file=sys.stderr)
        return output
    return ""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required recovery input is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _authority_hashes() -> dict[str, str]:
    return {str(path): _sha256(path) for path in PROTECTED}


def _write_snapshot() -> None:
    missing = [str(path) for path in PROTECTED if not path.exists()]
    if missing:
        raise RuntimeError("Protected authority input missing: " + ", ".join(missing))
    SNAPSHOT.write_text(
        json.dumps(_authority_hashes(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _assert_authority_unchanged() -> None:
    if not SNAPSHOT.exists():
        raise RuntimeError(f"Recovery authority snapshot missing: {SNAPSHOT}")
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    after = _authority_hashes()
    if before != after:
        raise RuntimeError(
            f"Protected authority changed during fix-verification delivery: before={before} after={after}"
        )
    print("ETF_FIX_VERIFICATION_AUTHORITY_UNCHANGED")


def _set_environment() -> None:
    values = {
        "PYTHONPATH": ".",
        "MRKT_RPRTS_REPORT_MODE": "pro",
        "MRKT_RPRTS_COCKPIT_FRONT_PAGE": "enabled",
        "ETF_PRICING_RUN_ID": RUN_ID,
        "MRKT_RPRTS_RUN_ID": RUN_ID,
        "REQUESTED_CLOSE_DATE": REQUESTED_CLOSE_DATE,
        "REPORT_TOKEN": REPORT_TOKEN,
        "MRKT_RPRTS_EXPLICIT_REPORT_PATH": str(EN_REPORT),
        "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL": str(NL_REPORT),
        "MRKT_RPRTS_RUNTIME_STATE_PATH": str(RUNTIME_STATE),
        "ETF_RUNTIME_STATE_PATH": str(RUNTIME_STATE),
        "MRKT_RPRTS_PRICING_AUDIT_PATH": str(PRICING_AUDIT),
        "ETF_PRICING_AUDIT_PATH": str(PRICING_AUDIT),
        "ETF_MODEL_EXECUTION_PATH": str(EXECUTION_ARTIFACT),
        "MRKT_RPRTS_MODEL_EXECUTION_PATH": str(EXECUTION_ARTIFACT),
    }
    os.environ.update(values)


def _assert_inputs() -> None:
    required = (EN_REPORT, NL_REPORT, RUNTIME_STATE, PRICING_AUDIT, RUN_MANIFEST, *PROTECTED)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Fix-verification recovery inputs missing: " + ", ".join(missing))


def _assert_not_already_sent() -> None:
    receipts = (
        DELIVERY_MANIFEST,
        EN_REPORT.with_name(f"{EN_REPORT.stem}_delivery_manifest.txt"),
        NL_REPORT.with_name(f"{NL_REPORT.stem}_delivery_manifest.txt"),
    )
    existing = [str(path) for path in receipts if path.exists()]
    if existing:
        raise RuntimeError(
            "Delivery recovery is fail-closed because send evidence already exists: "
            + ", ".join(existing)
        )


def _assert_trade_lineage() -> None:
    state = _read_json(RUNTIME_STATE)
    by_ticker = {
        str(row.get("ticker") or "").upper(): row
        for row in state.get("positions", []) or []
        if str(row.get("ticker") or "").strip()
    }
    for ticker, (expected_before, expected_after) in EXPECTED_WEIGHTS.items():
        row = by_ticker.get(ticker)
        if row is None:
            raise RuntimeError(f"Runtime state is missing fix-verification ticker {ticker}")
        before = float(row.get("previous_weight_pct"))
        after = float(row.get("current_weight_pct"))
        if abs(before - expected_before) > 0.0001 or abs(after - expected_after) > 0.0001:
            raise RuntimeError(
                f"Trade-lineage mismatch for {ticker}: {before}->{after}, "
                f"expected {expected_before}->{expected_after}"
            )
    print("ETF_FIX_VERIFICATION_LINEAGE_OK | PAVE=0.0->4.94 | XLU=5.4908->0.52")


def _build_guarded_no_execution_artifact() -> None:
    if EXECUTION_ARTIFACT.exists():
        EXECUTION_ARTIFACT.unlink()
    output = _run(
        sys.executable,
        "-m",
        "runtime.model_execution_guarded_auto",
        "--runtime-state",
        str(RUNTIME_STATE),
        "--portfolio-state",
        str(PROTECTED[0]),
        "--trade-ledger",
        str(PROTECTED[1]),
        "--output-dir",
        "output/runtime",
        capture=True,
    )
    if not EXECUTION_ARTIFACT.exists():
        raise RuntimeError(
            f"Guarded report-only recovery did not produce expected artifact {EXECUTION_ARTIFACT}; output={output}"
        )
    payload = _read_json(EXECUTION_ARTIFACT)
    result = payload.get("guarded_auto_result") or {}
    if payload.get("execution_mode") != "guarded_auto":
        raise RuntimeError("Recovery artifact is not guarded_auto")
    if payload.get("execution_status") != "no_trade_intents":
        raise RuntimeError(
            f"Recovery must remain report-only; execution_status={payload.get('execution_status')}"
        )
    if result.get("authorization_status") != "not_authorized":
        raise RuntimeError(
            f"Portfolio execution was not explicitly blocked: {result.get('authorization_status')}"
        )
    if result.get("portfolio_state_written") is True or result.get("trade_ledger_written") is True:
        raise RuntimeError("Report-only recovery attempted to write portfolio state or trade ledger")
    print(f"ETF_FIX_VERIFICATION_NO_EXECUTION_OK | artifact={EXECUTION_ARTIFACT}")


def _check_front_pages_and_weights() -> None:
    marker = 'data-cockpit-front-page="delivery"'
    required_tokens = {
        "PAVE": ("PAVE 0.0%", "4.9%"),
        "XLU": ("XLU 5.5%", "0.5%"),
    }
    for path in (
        EN_REPORT.with_name(f"{EN_REPORT.stem}_delivery.html"),
        NL_REPORT.with_name(f"{NL_REPORT.stem}_delivery.html"),
    ):
        text = path.read_text(encoding="utf-8")
        count = text.count(marker)
        if count != 1:
            raise RuntimeError(f"{path}: expected one cockpit front page, found {count}")
        missing = [
            token
            for pair in required_tokens.values()
            for token in pair
            if token not in text
        ]
        if missing:
            raise RuntimeError(f"{path}: corrected cockpit trade weights missing: {missing}")
        print(f"ETF_FIX_VERIFICATION_COCKPIT_OK | file={path.name} | count={count}")


def prepare() -> None:
    _set_environment()
    _assert_inputs()
    _assert_not_already_sent()
    _write_snapshot()
    _assert_trade_lineage()

    _run(
        sys.executable,
        "tools/validate_etf_persisted_valuation_state.py",
        "--runtime-state",
        str(RUNTIME_STATE),
        "--portfolio-state",
        str(PROTECTED[0]),
        "--valuation-history",
        str(PROTECTED[2]),
    )
    _run(
        sys.executable,
        "tools/validate_etf_trade_ledger_idempotency.py",
        "--trade-ledger",
        str(PROTECTED[1]),
    )
    _build_guarded_no_execution_artifact()
    _run(
        sys.executable,
        "tools/validate_etf_whole_share_contract.py",
        "--portfolio-state",
        str(PROTECTED[0]),
        "--artifact",
        str(EXECUTION_ARTIFACT),
    )
    _run(
        sys.executable,
        "tools/validate_etf_model_execution.py",
        "--artifact",
        str(EXECUTION_ARTIFACT),
        "--expected-mode",
        "guarded_auto",
    )
    _run(
        sys.executable,
        "tools/validate_etf_pricing_lineage_contract.py",
        "--manifest",
        str(RUN_MANIFEST),
    )

    bundle = srh.report_module.generate_delivery_assets_for_run(
        Path("output"), EN_REPORT, mode="pro"
    )
    if bundle.get("bilingual") is not True:
        raise RuntimeError("Fix-verification asset generation did not produce a bilingual package")

    _run(sys.executable, "tools/validate_etf_delivery_html_contract.py", "--output-dir", "output")
    _run(sys.executable, "tools/validate_etf_client_surface_clean.py", "--output-dir", "output")
    _run(
        sys.executable,
        "tools/validate_etf_macro_thesis_surface_leakage.py",
        "--output-dir",
        "output",
    )
    _run(sys.executable, "tools/validate_etf_pdf_visual_contract.py", "--output-dir", "output")
    _check_front_pages_and_weights()
    _assert_authority_unchanged()
    print("ETF_FIX_VERIFICATION_PREPARE_OK")


def finalize() -> None:
    _set_environment()
    if not SNAPSHOT.exists():
        raise RuntimeError(f"Recovery authority snapshot missing: {SNAPSHOT}")

    _run(
        sys.executable,
        "tools/write_etf_delivery_manifest_summary.py",
        "--run-id",
        RUN_ID,
        "--requested-close-date",
        REQUESTED_CLOSE_DATE,
        "--report-token",
        REPORT_TOKEN,
        "--english-report",
        str(EN_REPORT),
        "--dutch-report",
        str(NL_REPORT),
    )
    if not DELIVERY_MANIFEST.exists():
        raise RuntimeError(f"Delivery manifest missing after successful send: {DELIVERY_MANIFEST}")

    _run(
        sys.executable,
        "tools/write_weekly_etf_run_manifest.py",
        "--run-id",
        RUN_ID,
        "--requested-close-date",
        REQUESTED_CLOSE_DATE,
        "--report-token",
        REPORT_TOKEN,
        "--pricing-audit",
        str(PRICING_AUDIT),
        "--runtime-state",
        str(RUNTIME_STATE),
        "--english-report",
        str(EN_REPORT),
        "--dutch-report",
        str(NL_REPORT),
        "--portfolio-state",
        str(PROTECTED[0]),
        "--valuation-history",
        str(PROTECTED[2]),
        "--delivery-manifest",
        str(DELIVERY_MANIFEST),
        "--status",
        "workflow_success",
        "--conclusion",
        "success",
        "--notes",
        "Fix-verification delivery recovery; corrected PAVE/XLU lineage delivered without portfolio or broker execution.",
    )
    _run(sys.executable, "tools/validate_etf_manifest_evidence.py")
    _assert_authority_unchanged()
    print("ETF_FIX_VERIFICATION_FINALIZE_OK")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover and deliver the persisted Weekly ETF fix-verification package."
    )
    parser.add_argument("phase", choices=("prepare", "finalize"))
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        finalize()


if __name__ == "__main__":
    main()
