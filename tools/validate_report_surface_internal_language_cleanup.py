#!/usr/bin/env python3
"""Validate report-surface internal-language cleanup without mutating reports.

The validator uses the immutable 260716 bilingual report pair as representative
input, applies the production cleanup path in memory, and writes separate preview
and evidence artifacts. It does not generate a new report or send email.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.report_surface_language_contract import (
    evidence_summary,
    markdown_link_multiset,
    numeric_multiset,
)
from runtime.wp16_followup3_cleanup import clean_text

DEFAULT_EN = Path("output/weekly_analysis_pro_260716.md")
DEFAULT_NL = Path("output/weekly_analysis_pro_nl_260716.md")
DEFAULT_EVIDENCE_DIR = Path("output/report_surface_language_validation")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_one(path: Path, *, language: str, evidence_dir: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing representative report: {path}")
    original = path.read_text(encoding="utf-8")
    cleaned = clean_text(original, language=language)
    summary = evidence_summary(original, cleaned, language=language)

    if not summary["before_findings"]:
        raise RuntimeError(f"Representative {language} report contains no planted/internal-language findings")
    if summary["after_findings"]:
        raise RuntimeError(f"Internal-language findings remain in {language}: {summary['after_findings']}")
    if not summary["numeric_multiset_preserved"]:
        before = numeric_multiset(original)
        after = numeric_multiset(cleaned)
        raise RuntimeError(f"Numeric parity failed for {language}: before_only={before - after}; after_only={after - before}")
    if not summary["markdown_link_multiset_preserved"]:
        before = markdown_link_multiset(original)
        after = markdown_link_multiset(cleaned)
        raise RuntimeError(f"Markdown-link parity failed for {language}: before_only={before - after}; after_only={after - before}")
    if not summary["idempotent"]:
        raise RuntimeError(f"Cleanup is not idempotent for {language}")

    preview_path = evidence_dir / f"weekly_analysis_pro_260716_{language}_clean_preview.md"
    preview_path.write_text(cleaned, encoding="utf-8")
    summary.update(
        {
            "source_path": str(path),
            "preview_path": str(preview_path),
            "source_sha256": _sha256_text(original),
            "preview_sha256": _sha256_text(cleaned),
            "source_bytes_unchanged": path.read_text(encoding="utf-8") == original,
            "number_token_count": sum(numeric_multiset(original).values()),
            "markdown_link_count": sum(markdown_link_multiset(original).values()),
        }
    )
    return summary


def validate(*, english_report: Path, dutch_report: Path, evidence_dir: Path) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    languages = {
        "en": _validate_one(english_report, language="en", evidence_dir=evidence_dir),
        "nl": _validate_one(dutch_report, language="nl", evidence_dir=evidence_dir),
    }
    payload: dict[str, Any] = {
        "schema_version": "report_surface_internal_language_cleanup_evidence_v1",
        "package": "WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP",
        "status": "validated_no_send",
        "representative_report_token": "260716",
        "languages": languages,
        "contract": {
            "forbidden_internal_terms_after_cleanup": 0,
            "double_punctuation_after_cleanup": 0,
            "numeric_multiset_before_after": "identical",
            "markdown_link_multiset_before_after": "identical",
            "cleanup_idempotent": True,
            "historical_report_mutation": False,
            "portfolio_state_mutation": False,
            "trade_ledger_mutation": False,
            "pricing_authority_change": False,
            "macro_thesis_authority_promotion": False,
            "portfolio_execution_change": False,
            "email_sent": False,
        },
    }
    evidence_path = evidence_dir / "report_surface_internal_language_cleanup_evidence.json"
    evidence_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_OK | "
        f"evidence={evidence_path} | en_before={len(languages['en']['before_findings'])} | "
        f"nl_before={len(languages['nl']['before_findings'])} | after=0 | email_sent=false"
    )
    return evidence_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english-report", type=Path, default=DEFAULT_EN)
    parser.add_argument("--dutch-report", type=Path, default=DEFAULT_NL)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    validate(
        english_report=args.english_report,
        dutch_report=args.dutch_report,
        evidence_dir=args.evidence_dir,
    )


if __name__ == "__main__":
    main()
