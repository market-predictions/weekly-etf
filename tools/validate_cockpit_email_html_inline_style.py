from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from runtime.additive_cockpit_front_page import (
    FRONT_PAGE_MARKER,
    STYLE_ID,
    inject_additive_cockpit_front_page,
    render_delivery_cockpit_front_page_fragment,
)

PROTECTED_PATHS = (
    "output/etf_portfolio_state.json",
    "output/etf_trade_ledger.csv",
    "output/etf_valuation_history.csv",
    "output/etf_recommendation_scorecard.csv",
    "output/runtime/latest_etf_report_state_path.txt",
    "output/pricing/latest_price_audit_path.txt",
    "output/run_manifests/latest_weekly_etf_run_manifest_path.txt",
)

REQUIRED_INLINE_SELECTORS = (
    "section.etf-cockpit-page",
    ".etf-cockpit-inner",
    ".etf-cockpit-header",
    ".etf-cockpit-kicker",
    ".etf-cockpit-mast",
    ".etf-cockpit-strap",
    ".etf-cockpit-section-title",
    ".etf-cockpit-lede",
    ".etf-cockpit-card",
    ".etf-cockpit-performance",
    ".etf-cockpit-metric",
    ".etf-cockpit-discipline",
    ".etf-cockpit-trigger",
    ".etf-cockpit-evidence",
    ".etf-cockpit-footer",
)


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
            raise RuntimeError(f"Missing protected path: {relative}")
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


def _inline_failures(soup: BeautifulSoup) -> list[str]:
    failures: list[str] = []
    for selector in REQUIRED_INLINE_SELECTORS:
        node = soup.select_one(selector)
        if node is None:
            failures.append(f"missing:{selector}")
            continue
        if not str(node.get("style") or "").strip():
            failures.append(f"missing_inline_style:{selector}")
    return failures


def _validate_email(language: str, output_dir: Path) -> dict[str, Any]:
    fragment = render_delivery_cockpit_front_page_fragment(
        output_dir=output_dir,
        language=language,
        render_mode="email",
    )
    if fragment.css:
        raise RuntimeError(f"{language} email fragment still depends on head CSS")
    soup = BeautifulSoup(fragment.html, "html.parser")
    if soup.find("style") is not None:
        raise RuntimeError(f"{language} email fragment contains a style block")
    failures = _inline_failures(soup)
    if failures:
        raise RuntimeError(f"{language} inline email failures: {failures}")
    presentation_tables = soup.find_all("table", attrs={"role": "presentation"})
    if len(presentation_tables) < 8:
        raise RuntimeError(f"{language} email cockpit is not sufficiently table-based")
    lowered = fragment.html.lower().replace(" ", "")
    for forbidden in ("display:grid", "display:flex", "<svg"):
        if forbidden in lowered:
            raise RuntimeError(f"{language} email cockpit contains non-email-safe essential layout: {forbidden}")

    classic = (
        "<!doctype html><html><head><style>.classic{color:#123456}</style></head>"
        "<body><main id='classic-report'><h1>Classic report body</h1>"
        "<p>Classic evidence layer remains.</p></main></body></html>"
    )
    result = inject_additive_cockpit_front_page(
        classic,
        language=language,
        output_dir=output_dir,
        render_mode="email",
        feature_value="enabled",
    )
    if result.status != "enabled" or result.front_page_count != 1:
        raise RuntimeError(f"{language} email injection failed: {result}")
    degraded = BeautifulSoup(result.html, "html.parser")
    for node in degraded.find_all("style"):
        node.decompose()
    failures_after_strip = _inline_failures(degraded)
    if failures_after_strip:
        raise RuntimeError(
            f"{language} email cockpit fails after head-style removal: {failures_after_strip}"
        )
    if degraded.select_one("#classic-report") is None:
        raise RuntimeError(f"{language} classic report body disappeared")
    if FRONT_PAGE_MARKER not in str(degraded):
        raise RuntimeError(f"{language} cockpit marker disappeared after degradation test")

    text = degraded.get_text(" ", strip=True)
    required_text = (
        ("Rapportvoorpagina", "Bronnen en controle")
        if language == "nl"
        else ("Report front page", "Sources & controls")
    )
    for token in required_text:
        if token not in text:
            raise RuntimeError(f"{language} email cockpit is missing client text: {token}")

    return {
        "inline_selector_count": len(REQUIRED_INLINE_SELECTORS),
        "presentation_table_count": len(presentation_tables),
        "head_style_dependency": False,
        "style_strip_degradation_test": "passed",
        "front_page_count": result.front_page_count,
        "classic_body_preserved": True,
        "html_sha256": hashlib.sha256(fragment.html.encode("utf-8")).hexdigest(),
    }


def _validate_pdf(language: str, output_dir: Path) -> dict[str, Any]:
    fragment = render_delivery_cockpit_front_page_fragment(
        output_dir=output_dir,
        language=language,
        render_mode="pdf",
    )
    if STYLE_ID not in fragment.css:
        raise RuntimeError(f"{language} PDF cockpit lost its current stylesheet")
    if "@media print" not in fragment.css:
        raise RuntimeError(f"{language} PDF cockpit lost print rules")
    if '<svg class="spark"' not in fragment.html:
        raise RuntimeError(f"{language} PDF cockpit lost the SVG sparkline")
    if "etf-cockpit-email-sparkline" in fragment.html:
        raise RuntimeError(f"{language} PDF cockpit incorrectly uses the email fallback")
    return {
        "class_based_stylesheet_preserved": True,
        "print_rules_preserved": True,
        "svg_sparkline_preserved": True,
        "html_sha256": hashlib.sha256(fragment.html.encode("utf-8")).hexdigest(),
        "css_sha256": hashlib.sha256(fragment.css.encode("utf-8")).hexdigest(),
    }


def validate(repo_root: Path, evidence_path: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = repo_root / "output"
    before = protected_hashes(repo_root)
    languages: dict[str, Any] = {}
    for language in ("en", "nl"):
        languages[language] = {
            "email": _validate_email(language, output_dir),
            "pdf": _validate_pdf(language, output_dir),
        }
    after = protected_hashes(repo_root)
    if before != after:
        changed = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
        raise RuntimeError(f"Validator mutated protected authority: {changed}")

    evidence = {
        "schema_version": "cockpit_email_html_inline_style_fix_v1",
        "date": "2026-07-18",
        "repository": "market-predictions/weekly-etf",
        "package": "WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX",
        "status": "validated_no_send",
        "root_cause": "cockpit depended on a separate head stylesheet that the mail client did not reliably retain or apply",
        "implementation": {
            "email_layout": "inline_styles_and_presentation_tables",
            "email_head_css_required": False,
            "pdf_layout": "existing_class_based_surface_preserved",
        },
        "languages": languages,
        "authority": {
            "protected_hashes_before_after": "identical",
            "portfolio_state_mutation": False,
            "trade_ledger_mutation": False,
            "valuation_history_mutation": False,
            "pricing_authority_change": False,
            "historical_report_mutation": False,
            "email_sent": False,
        },
        "protected_sha256": before,
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "COCKPIT_EMAIL_INLINE_STYLE_OK | en=passed | nl=passed | "
        "pdf_preserved=true | protected_hashes=identical | email_sent=false"
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--evidence-path", required=True)
    args = parser.parse_args()
    validate(Path(args.repo_root), Path(args.evidence_path))


if __name__ == "__main__":
    main()
