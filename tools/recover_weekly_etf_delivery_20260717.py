from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report_runtime_html as srh

RUN_ID = "20260717_154351"
REQUESTED_CLOSE_DATE = "2026-07-16"
REPORT_TOKEN = "260716"
EN_REPORT = Path("output/weekly_analysis_pro_260716_02.md")
NL_REPORT = Path("output/weekly_analysis_pro_nl_260716_02.md")
RUNTIME_STATE = Path("output/runtime/etf_report_state_20260716_20260717_154351_executed.json")
PRICING_AUDIT = Path("output/pricing/price_audit_2026-07-16_20260717_154351.json")
EXECUTION_ARTIFACT = Path("output/runtime/etf_model_execution_20260716_20260717_154351.json")
RUN_MANIFEST = Path("output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json")
DELIVERY_MANIFEST = Path("output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json")
SNAPSHOT = Path("/tmp/weekly-etf-delivery-recovery-authority.json")
PROTECTED = (
    Path("output/etf_portfolio_state.json"),
    Path("output/etf_trade_ledger.csv"),
    Path("output/etf_valuation_history.csv"),
)


def _run(*args: str) -> None:
    print("ETF_RECOVERY_COMMAND | " + " ".join(args))
    subprocess.run(args, check=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _authority_hashes() -> dict[str, str]:
    return {str(path): _sha256(path) for path in PROTECTED}


def _write_snapshot() -> None:
    SNAPSHOT.write_text(json.dumps(_authority_hashes(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _assert_authority_unchanged() -> None:
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    after = _authority_hashes()
    if before != after:
        raise RuntimeError(f"Protected authority changed during delivery recovery: before={before} after={after}")
    print("ETF_RECOVERY_AUTHORITY_UNCHANGED")


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


def _assert_not_already_sent() -> None:
    receipt_paths = [
        DELIVERY_MANIFEST,
        EN_REPORT.with_name(f"{EN_REPORT.stem}_delivery_manifest.txt"),
        NL_REPORT.with_name(f"{NL_REPORT.stem}_delivery_manifest.txt"),
    ]
    existing = [str(path) for path in receipt_paths if path.exists()]
    if existing:
        raise RuntimeError(
            "Delivery recovery is fail-closed because send evidence already exists: " + ", ".join(existing)
        )


def _check_front_pages() -> None:
    marker = 'data-cockpit-front-page="delivery"'
    for path in (
        EN_REPORT.with_name(f"{EN_REPORT.stem}_delivery.html"),
        NL_REPORT.with_name(f"{NL_REPORT.stem}_delivery.html"),
    ):
        count = path.read_text(encoding="utf-8").count(marker)
        if count != 1:
            raise RuntimeError(f"{path}: expected one cockpit front page, found {count}")
        print(f"ETF_RECOVERY_COCKPIT_OK | file={path.name} | count={count}")


def prepare() -> None:
    _set_environment()
    _assert_not_already_sent()
    _write_snapshot()

    _run("python", "tools/validate_etf_whole_share_contract.py", "--portfolio-state", str(PROTECTED[0]), "--artifact", str(EXECUTION_ARTIFACT))
    _run("python", "tools/validate_etf_model_execution.py", "--artifact", str(EXECUTION_ARTIFACT), "--expected-mode", "guarded_auto")
    _run("python", "tools/validate_etf_trade_ledger_idempotency.py", "--trade-ledger", str(PROTECTED[1]))
    _run("python", "tools/validate_etf_client_surface_clean.py", "--output-dir", "output")

    bundle = srh.report_module.generate_delivery_assets_for_run(Path("output"), EN_REPORT, mode="pro")
    if bundle.get("bilingual") is not True:
        raise RuntimeError("Recovery asset generation did not produce a bilingual package")

    _run("python", "tools/validate_etf_delivery_html_visible_language_contract.py", "--output-dir", "output")
    _run("python", "tools/validate_etf_client_surface_clean.py", "--output-dir", "output")
    _run("python", "tools/validate_etf_macro_thesis_surface_leakage.py", "--output-dir", "output")
    _run("python", "tools/validate_etf_pdf_visual_contract.py", "--output-dir", "output")
    _run("python", "tools/validate_etf_pricing_lineage_contract.py", "--manifest", str(RUN_MANIFEST))
    _check_front_pages()
    _assert_authority_unchanged()
    print("ETF_RECOVERY_PREPARE_OK")


def finalize() -> None:
    _set_environment()
    if not SNAPSHOT.exists():
        raise RuntimeError(f"Recovery authority snapshot missing: {SNAPSHOT}")

    _run(
        "python",
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
        "python",
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
        "Idempotent delivery recovery; persisted XLU-to-PAVE execution reused without second mutation.",
    )
    _run("python", "tools/validate_etf_manifest_evidence.py")
    _assert_authority_unchanged()
    print("ETF_RECOVERY_FINALIZE_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover delivery of the persisted Weekly ETF 20260717_154351 package.")
    parser.add_argument("phase", choices=("prepare", "finalize"))
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        finalize()


if __name__ == "__main__":
    main()
