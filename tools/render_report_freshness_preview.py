from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from runtime.report_freshness_contract import load_runtime_state, validate_report_freshness
from runtime.standalone_html_equity_embed import validate_standalone_html_equity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
STATE_PATH = OUTPUT / "etf_portfolio_state.json"
LEDGER_PATH = OUTPUT / "etf_trade_ledger.csv"
SOURCE_ARTIFACT = OUTPUT / "runtime/etf_model_execution_20260714_20260715_175910.json"
REPORT_EN = OUTPUT / "weekly_analysis_pro_260714_04.md"
REPORT_NL = OUTPUT / "weekly_analysis_pro_nl_260714_04.md"
VALIDATION_PATH = OUTPUT / "validation/etf_report_freshness_260714_04.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size <= 0:
        raise RuntimeError(f"Expected preview artifact is missing or empty: {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def main() -> None:
    if not SOURCE_ARTIFACT.is_file():
        raise RuntimeError(f"Authoritative source execution artifact is missing: {SOURCE_ARTIFACT}")

    state_before = sha256(STATE_PATH)
    ledger_before = sha256(LEDGER_PATH)

    os.environ["MRKT_RPRTS_REPORT_MODE"] = "pro"
    os.environ["MRKT_RPRTS_EXPLICIT_REPORT_PATH"] = str(REPORT_EN.relative_to(ROOT))
    os.environ["MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"] = str(REPORT_NL.relative_to(ROOT))

    from runtime.finalize_executed_etf_report import finalize_from_artifact

    result = finalize_from_artifact(SOURCE_ARTIFACT.relative_to(ROOT))
    if not result.get("finalized"):
        raise RuntimeError(f"Executed-report finalizer did not produce the preview: {result}")

    runtime_state = load_runtime_state(result.get("runtime_state"))
    if not runtime_state:
        raise RuntimeError("Preview replay could not resolve the executed runtime state.")

    text_en = REPORT_EN.read_text(encoding="utf-8")
    text_nl = REPORT_NL.read_text(encoding="utf-8")
    validate_report_freshness(text_en, runtime_state, "en")
    validate_report_freshness(text_nl, runtime_state, "nl")

    expected_en = [
        "No material regime change was recorded versus the prior review.",
        "already represents 24.05% of the portfolio",
        "Existing funded position; no additional lane promotion was granted this run.",
        "DFEN",
    ]
    expected_nl = [
        "Er is geen materiële regimeverandering vastgesteld ten opzichte van de vorige review.",
        "vertegenwoordigt al 24.05% van de portefeuille",
        "Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend.",
        "DFEN",
    ]
    for phrase in expected_en:
        if phrase not in text_en:
            raise RuntimeError(f"English freshness proof is missing: {phrase}")
    for phrase in expected_nl:
        if phrase not in text_nl:
            raise RuntimeError(f"Dutch freshness proof is missing: {phrase}")

    forbidden_en = [
        "Zero allocation is an explicit U.S. exceptionalism bet.",
        "Portfolio has limited non-U.S. exposure.",
        "Non-U.S. equity exposure remains a diversification gap.",
    ]
    forbidden_nl = [
        "De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS.",
        "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.",
    ]
    for phrase in forbidden_en:
        if phrase in text_en:
            raise RuntimeError(f"English stale wording remains: {phrase}")
    for phrase in forbidden_nl:
        if phrase in text_nl:
            raise RuntimeError(f"Dutch stale wording remains: {phrase}")

    import send_report_runtime_html as delivery_entrypoint

    bundle = delivery_entrypoint.report_module.generate_delivery_assets_for_run(
        OUTPUT,
        REPORT_EN,
        mode="pro",
    )
    if not bundle.get("bilingual"):
        raise RuntimeError("Freshness preview did not produce a bilingual delivery bundle.")

    artifacts: dict[str, dict[str, dict[str, object]]] = {"en": {}, "nl": {}}
    for language in ("en", "nl"):
        assets = bundle[language]
        html_path = Path(assets["html_path"])
        validate_standalone_html_equity(html_path)
        if "cid:equitycurve" not in str(assets.get("html_email") or "").lower():
            raise RuntimeError(f"MIME email HTML lost the CID graph reference for {language}.")
        for key in ("report_path", "clean_md_path", "html_path", "pdf_path", "equity_curve_png"):
            artifacts[language][key] = record(Path(assets[key]))

    state_after = sha256(STATE_PATH)
    ledger_after = sha256(LEDGER_PATH)
    if state_before != state_after:
        raise RuntimeError("Freshness preview mutated official portfolio state.")
    if ledger_before != ledger_after:
        raise RuntimeError("Freshness preview mutated the official trade ledger.")

    payload = {
        "schema_version": "1.0",
        "status": "passed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation_type": "report_freshness_and_standalone_html_equity",
        "source_execution_artifact": str(SOURCE_ARTIFACT.relative_to(ROOT)),
        "source_execution_artifact_sha256": sha256(SOURCE_ARTIFACT),
        "email_sent": False,
        "model_execution_replayed": False,
        "official_state_mutated": False,
        "official_trade_ledger_mutated": False,
        "state_sha256_before": state_before,
        "state_sha256_after": state_after,
        "trade_ledger_sha256_before": ledger_before,
        "trade_ledger_sha256_after": ledger_after,
        "freshness_contract": {
            "what_changed_delta_only": True,
            "stale_relative_policy_event_removed": True,
            "current_iefa_allocation_reflected": True,
            "current_dfen_holding_reflected": True,
            "dutch_mixed_language_fragments_removed": True,
        },
        "html_equity_contract": {
            "standalone_html_uses_embedded_data_uri": True,
            "standalone_html_contains_no_cid_reference": True,
            "mime_email_html_keeps_cid_reference": True,
        },
        "artifacts": artifacts,
    }
    VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        "ETF_REPORT_FRESHNESS_PREVIEW_OK | "
        f"en={REPORT_EN.name} | nl={REPORT_NL.name} | validation={VALIDATION_PATH.relative_to(ROOT)} | "
        "email_sent=false | state_mutated=false | ledger_mutated=false"
    )


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
