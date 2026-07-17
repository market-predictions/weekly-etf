from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Iterator

from bs4 import BeautifulSoup
from pypdf import PdfReader

import send_report_runtime_html as runtime_delivery
from runtime.render_cockpit_front_page import _fmt_eur
from runtime.render_etf_report_from_state import render_en
from runtime.render_etf_report_nl_from_state import render_nl_native
from runtime.whole_share_contract import validate_whole_share_positions

FEATURE_FLAG = "MRKT_RPRTS_COCKPIT_FRONT_PAGE"
FRONT_PAGE_SELECTOR = 'section[data-cockpit-front-page="delivery"]'
STYLE_ID = "etf-cockpit-delivery-front-page-style"
PROTECTED_PATHS = (
    "output/etf_portfolio_state.json",
    "output/etf_trade_ledger.csv",
    "output/etf_valuation_history.csv",
    "output/etf_recommendation_scorecard.csv",
    "output/runtime/latest_etf_report_state_path.txt",
    "output/pricing/latest_price_audit_path.txt",
    "output/run_manifests/latest_weekly_etf_run_manifest_path.txt",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def protected_hashes(repo_root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROTECTED_PATHS:
        path = repo_root / relative
        if not path.exists():
            raise RuntimeError(f"Missing protected authority path: {relative}")
        result[relative] = _sha256(path)
    for pointer_relative in PROTECTED_PATHS[-3:]:
        pointer = repo_root / pointer_relative
        target_raw = pointer.read_text(encoding="utf-8").strip()
        if not target_raw:
            raise RuntimeError(f"Empty protected pointer: {pointer_relative}")
        target = repo_root / target_raw
        if not target.exists():
            raise RuntimeError(f"Protected pointer target missing: {target_raw}")
        result[target_raw] = _sha256(target)
    return result


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def build_exact_current_overlay(
    base_runtime: dict[str, Any], official_state: dict[str, Any]
) -> dict[str, Any]:
    positions = [dict(row) for row in official_state.get("positions", []) or [] if isinstance(row, dict)]
    errors = validate_whole_share_positions(positions, context="wp11_official_state")
    if errors:
        raise RuntimeError("WP11 exact-current overlay requires whole-share official state: " + "; ".join(errors))

    cash = round(_float(official_state.get("cash_eur")), 2)
    invested = round(
        sum(_float(row.get("market_value_eur") or row.get("previous_market_value_eur")) for row in positions),
        2,
    )
    nav = round(_float(official_state.get("nav_eur")), 2)
    if abs((invested + cash) - nav) > 0.05:
        raise RuntimeError(
            f"WP11 official state does not reconcile: invested={invested:.2f}, cash={cash:.2f}, nav={nav:.2f}"
        )

    overlay = dict(base_runtime)
    overlay["positions"] = positions
    overlay["portfolio"] = {
        "cash_eur": cash,
        "total_portfolio_value_eur": nav,
        "base_currency": str(official_state.get("base_currency") or "EUR"),
    }
    overlay["trade_intents"] = []
    overlay["rotation_plan"] = {}
    overlay["execution_context"] = {
        "report_phase": "post_execution",
        "validation_overlay": "wp11_exact_current_whole_share_state",
        "state_mutation": False,
    }
    validation_flags = dict(overlay.get("validation_flags") or {})
    validation_flags.update(
        {
            "post_execution_report": True,
            "already_executed_noop": True,
            "wp11_exact_current_overlay": True,
        }
    )
    overlay["validation_flags"] = validation_flags
    overlay["whole_share_contract"] = dict(official_state.get("whole_share_contract") or {})
    overlay["source_files"] = dict(overlay.get("source_files") or {})
    overlay["source_files"]["official_portfolio_state"] = "output/etf_portfolio_state.json"
    overlay["source_files"]["whole_share_reconciliation"] = (
        "output/runtime/etf_whole_share_reconciliation_20260716_20260717_094728.json"
    )
    return overlay


def production_feature_value(workflow_text: str) -> str | None:
    match = re.search(
        r"(?ms)^jobs:\s*\n\s{2}send-report:\s*\n(?:.*?\n)*?\s{4}env:\s*\n"
        r"(?:\s{6}[^\n]+\n)*?\s{6}MRKT_RPRTS_COCKPIT_FRONT_PAGE:\s*([^\s#]+)",
        workflow_text,
    )
    return match.group(1).strip() if match else None


def _copy_path(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    elif source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    else:
        raise RuntimeError(f"Missing validation input: {source}")


def prepare_temp_output(repo_root: Path, work_root: Path) -> Path:
    output_dir = work_root / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    for relative in (
        "output/etf_valuation_history.csv",
        "output/etf_recommendation_scorecard.csv",
        "output/lane_reviews",
        "output/macro",
        "output/pricing",
        "output/run_manifests",
    ):
        source = repo_root / relative
        destination = work_root / relative
        _copy_path(source, destination)
    return output_dir


@contextlib.contextmanager
def _environment(overrides: dict[str, str]) -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        os.environ.update(overrides)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextlib.contextmanager
def _working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _remove_optional(path: Path) -> None:
    if path.exists():
        path.unlink()


def _bundle_paths(bundle: dict[str, Any]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for language in ("en", "nl"):
        assets = bundle[language]
        result[f"{language}_html"] = Path(assets["html_path"])
        result[f"{language}_pdf"] = Path(assets["pdf_path"])
        result[f"{language}_report"] = Path(assets["report_path"])
    return result


def _save_bundle(bundle: dict[str, Any], evidence_dir: Path, label: str) -> dict[str, Path]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    saved: dict[str, Path] = {}
    for key, source in _bundle_paths(bundle).items():
        suffix = source.suffix
        destination = evidence_dir / f"{label}_{key}{suffix}"
        shutil.copy2(source, destination)
        saved[key] = destination
    return saved


def _normalized_classic_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select(FRONT_PAGE_SELECTOR):
        node.decompose()
    style = soup.find("style", id=STYLE_ID)
    if style is not None:
        style.decompose()
    for node in soup.select(".decision-cockpit"):
        node.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def _front_page_metrics(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    page = soup.select_one(FRONT_PAGE_SELECTOR)
    if page is None:
        raise RuntimeError("Enabled HTML is missing the cockpit front page")
    metrics: dict[str, str] = {}
    caption = page.select_one(".etf-cockpit-chart-caption")
    metrics["portfolio_caption"] = " ".join(caption.get_text(" ", strip=True).split()) if caption else ""
    for node in page.select(".etf-cockpit-metric"):
        label = node.select_one(".etf-cockpit-metric-label")
        value = node.select_one(".etf-cockpit-metric-value")
        sub = node.select_one(".etf-cockpit-metric-sub")
        if label and value:
            key = " ".join(label.get_text(" ", strip=True).split()).lower()
            metrics[key] = " ".join(value.get_text(" ", strip=True).split())
            if sub:
                metrics[f"{key}_sub"] = " ".join(sub.get_text(" ", strip=True).split())
    return metrics


def _section15_rows(report_text: str) -> list[dict[str, str]]:
    return runtime_delivery.report_module.parse_section15_holdings_rows_generic(report_text)


def _validate_rendered_holdings(
    report_text: str, official_positions: list[dict[str, Any]], *, language: str
) -> None:
    rows = _section15_rows(report_text)
    expected = {_ticker(row.get("ticker")): int(round(_float(row.get("shares")))) for row in official_positions}
    actual: dict[str, int] = {}
    for row in rows:
        ticker = _ticker(row.get("ticker"))
        if not ticker or ticker == "CASH":
            continue
        shares = _float(row.get("shares"))
        if abs(shares - round(shares)) > 1e-9:
            raise RuntimeError(f"{language} report contains fractional Section 15 shares for {ticker}: {shares}")
        actual[ticker] = int(round(shares))
    if actual != expected:
        raise RuntimeError(f"{language} rendered holdings mismatch: actual={actual}, expected={expected}")


def validate(
    *,
    repo_root: Path,
    work_root: Path,
    evidence_dir: Path,
    runtime_state_path: Path,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    work_root = work_root.resolve()
    evidence_dir = evidence_dir.resolve()
    before = protected_hashes(repo_root)

    official_path = repo_root / "output/etf_portfolio_state.json"
    official = _read_json(official_path)
    base_runtime = _read_json(runtime_state_path.resolve())
    overlay = build_exact_current_overlay(base_runtime, official)
    official_positions = [dict(row) for row in official.get("positions", []) or []]

    output_dir = prepare_temp_output(repo_root, work_root)
    overlay_path = output_dir / "runtime/wp11_exact_current_runtime_overlay.json"
    _write_json(overlay_path, overlay)
    (output_dir / "runtime/latest_etf_report_state_path.txt").write_text(
        str(overlay_path) + "\n", encoding="utf-8"
    )

    report_token = str(overlay.get("report_date") or overlay.get("requested_close_date") or "").replace("-", "")[2:]
    if not report_token:
        raise RuntimeError("WP11 overlay is missing a report date")
    report_en = output_dir / f"weekly_analysis_pro_{report_token}.md"
    report_nl = output_dir / f"weekly_analysis_pro_nl_{report_token}.md"

    with _working_directory(work_root):
        report_en.write_text(render_en(overlay), encoding="utf-8")
        report_nl.write_text(render_nl_native(overlay), encoding="utf-8")

        common_env = {
            "MRKT_RPRTS_OUTPUT_DIR": str(output_dir),
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH": str(report_en),
            "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL": str(report_nl),
            "MRKT_RPRTS_RUNTIME_STATE_PATH": str(overlay_path),
            "ETF_RUNTIME_STATE_PATH": str(overlay_path),
        }
        with _environment({**common_env, FEATURE_FLAG: "disabled"}):
            disabled_bundle = runtime_delivery.report_module.generate_delivery_assets_for_run(
                output_dir, report_en, mode="pro"
            )
        disabled_saved = _save_bundle(disabled_bundle, evidence_dir, "disabled")

        for path in (
            report_en.with_name(f"{report_en.stem}_delivery.html"),
            report_nl.with_name(f"{report_nl.stem}_delivery.html"),
            report_en.with_suffix(".pdf"),
            report_nl.with_suffix(".pdf"),
        ):
            _remove_optional(path)

        with _environment({**common_env, FEATURE_FLAG: "enabled"}):
            enabled_bundle = runtime_delivery.report_module.generate_delivery_assets_for_run(
                output_dir, report_en, mode="pro"
            )
        enabled_saved = _save_bundle(enabled_bundle, evidence_dir, "enabled")

    report_text_en = report_en.read_text(encoding="utf-8")
    report_text_nl = report_nl.read_text(encoding="utf-8")
    _validate_rendered_holdings(report_text_en, official_positions, language="EN")
    _validate_rendered_holdings(report_text_nl, official_positions, language="NL")

    languages: dict[str, Any] = {}
    nav = round(_float(official.get("nav_eur")), 2)
    cash = round(_float(official.get("cash_eur")), 2)
    largest = max(official_positions, key=lambda row: _float(row.get("market_value_eur")))
    expected_largest = _ticker(largest.get("ticker"))
    expected_position_count = len(official_positions)

    for language in ("en", "nl"):
        disabled_html = disabled_saved[f"{language}_html"].read_text(encoding="utf-8")
        enabled_html = enabled_saved[f"{language}_html"].read_text(encoding="utf-8")
        disabled_count = len(BeautifulSoup(disabled_html, "html.parser").select(FRONT_PAGE_SELECTOR))
        enabled_soup = BeautifulSoup(enabled_html, "html.parser")
        enabled_count = len(enabled_soup.select(FRONT_PAGE_SELECTOR))
        small_cockpit_count = len(enabled_soup.select(".decision-cockpit"))
        if disabled_count != 0 or enabled_count != 1:
            raise RuntimeError(
                f"{language} front-page count mismatch: disabled={disabled_count}, enabled={enabled_count}"
            )
        if small_cockpit_count != 0:
            raise RuntimeError(f"{language} enabled HTML duplicates the smaller decision cockpit")
        if _normalized_classic_text(disabled_html) != _normalized_classic_text(enabled_html):
            raise RuntimeError(f"{language} classic report body changed after front-page enablement")

        disabled_pages = len(PdfReader(str(disabled_saved[f"{language}_pdf"])).pages)
        enabled_pages = len(PdfReader(str(enabled_saved[f"{language}_pdf"])).pages)
        if enabled_pages != disabled_pages + 1:
            raise RuntimeError(
                f"{language} PDF page delta mismatch: disabled={disabled_pages}, enabled={enabled_pages}"
            )

        metrics = _front_page_metrics(enabled_html)
        expected_nav = _fmt_eur(nav, language)
        expected_cash = _fmt_eur(cash, language)
        if expected_nav not in metrics.get("portfolio_caption", ""):
            raise RuntimeError(f"{language} front page NAV is not exact-current: {metrics}")
        positions_key = "posities" if language == "nl" else "positions"
        largest_key = "grootste positie" if language == "nl" else "largest position"
        cash_key = "cash"
        if metrics.get(positions_key) != str(expected_position_count):
            raise RuntimeError(f"{language} front-page position count mismatch: {metrics}")
        if metrics.get(largest_key) != expected_largest:
            raise RuntimeError(f"{language} front-page largest position mismatch: {metrics}")
        if metrics.get(f"{cash_key}_sub") != expected_cash:
            raise RuntimeError(f"{language} front-page cash mismatch: {metrics}")

        languages[language] = {
            "disabled_front_page_count": disabled_count,
            "enabled_front_page_count": enabled_count,
            "enabled_small_decision_cockpit_count": small_cockpit_count,
            "classic_report_body": "preserved",
            "disabled_pdf_pages": disabled_pages,
            "enabled_pdf_pages": enabled_pages,
            "pdf_page_delta": enabled_pages - disabled_pages,
            "front_page_metrics": metrics,
            "artifact_sha256": {
                "disabled_html": _sha256(disabled_saved[f"{language}_html"]),
                "enabled_html": _sha256(enabled_saved[f"{language}_html"]),
                "disabled_pdf": _sha256(disabled_saved[f"{language}_pdf"]),
                "enabled_pdf": _sha256(enabled_saved[f"{language}_pdf"]),
            },
        }

    workflow_text = (repo_root / ".github/workflows/send-weekly-report.yml").read_text(encoding="utf-8")
    feature_value = production_feature_value(workflow_text)
    if feature_value != "enabled":
        raise RuntimeError(
            f"Production workflow does not explicitly enable the cockpit front page: {feature_value!r}"
        )

    after = protected_hashes(repo_root)
    if before != after:
        changed = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
        raise RuntimeError(f"WP11 validation mutated protected authority files: {changed}")

    evidence = {
        "schema_version": "cockpit_wp11_production_enablement_evidence_v1",
        "date": "2026-07-17",
        "repository": "market-predictions/weekly-etf",
        "package": "WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT",
        "status": "validated_ready_for_production_enablement_merge",
        "selected_option": "B_enable_additive_delivery_front_page",
        "production_feature": {
            "name": FEATURE_FLAG,
            "value": feature_value,
            "rollback_value": "disabled",
            "failure_behavior": "unchanged_classic_output",
        },
        "exact_current_authority": {
            "official_portfolio_state": "output/etf_portfolio_state.json",
            "base_runtime_state": str(runtime_state_path.relative_to(repo_root)),
            "whole_share_status": (official.get("whole_share_contract") or {}).get("status"),
            "position_count": expected_position_count,
            "nav_eur": nav,
            "cash_eur": cash,
            "largest_position": expected_largest,
            "overlay_persisted_to_production": False,
        },
        "languages": languages,
        "delivery_contract": {
            "email_count_change": False,
            "pdf_count_change": False,
            "attachment_contract_change": False,
            "manifest_contract_change": False,
            "email_sent": False,
        },
        "authority_contract": {
            "protected_hashes_before_after": "identical",
            "portfolio_model_execution": False,
            "official_state_mutation": False,
            "official_trade_ledger_mutation": False,
            "pricing_authority_change": False,
        },
        "protected_sha256": before,
    }
    _write_json(evidence_dir / "cockpit_wp11_production_enablement_evidence.json", evidence)
    print(
        "COCKPIT_WP11_PRODUCTION_ENABLEMENT_OK | "
        f"feature={feature_value} | positions={expected_position_count} | nav_eur={nav:.2f} | "
        f"email_sent=false | evidence={evidence_dir / 'cockpit_wp11_production_enablement_evidence.json'}"
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument(
        "--runtime-state",
        default="output/runtime/etf_report_state_20260716_20260717_094728.json",
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_path = Path(args.runtime_state)
    if not runtime_path.is_absolute():
        runtime_path = repo_root / runtime_path
    validate(
        repo_root=repo_root,
        work_root=Path(args.work_root),
        evidence_dir=Path(args.evidence_dir),
        runtime_state_path=runtime_path,
    )


if __name__ == "__main__":
    main()
