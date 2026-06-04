#!/usr/bin/env python3
"""Validate macro/regime/thesis compliance before client-facing promotion.

This validator is intentionally conservative. It protects the macro/thesis roadmap
while the deterministic regime engine remains shadow-only.

It can validate report text, macro-pack JSON, methodology notes, committed report
macro sections, or embedded self-tests. The first production use should be as a
gate before any expanded macro/regime/thesis text is allowed onto the client
surface.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PREDICTIVE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("market_level_forecast", r"\b(?:will|shall)\s+(?:rise|fall|rally|crash|drop|surge|break|reach|hit|trade at)\b"),
    ("certainty_prediction", r"\b(?:guaranteed|certain|certainty|inevitable|must happen|cannot fail)\b"),
    ("central_bank_certainty", r"\b(?:Fed|Federal Reserve|ECB|BoE|BoJ|PBoC|central bank|central banks)\b.{0,80}\b(?:will|shall|must)\s+(?:cut|hike|raise|lower|pause|pivot)\b"),
    ("asset_direction_certainty", r"\b(?:ETF|ETFs|equities|stocks|bonds|gold|dollar|euro|rates|yields|Nasdaq|S&P|DAX)\b.{0,80}\b(?:will|shall|must)\s+(?:outperform|underperform|rise|fall|rally|drop|surge|crash)\b"),
)

STAGE1_LEAK_PATTERNS: tuple[tuple[str, str], ...] = (
    ("stage1_label", r"\bStage[- ]?1\s+(?:thesis\s+)?candidate\b"),
    ("candidate_recommendation", r"\b(?:candidate|watchlist lane|thesis candidate)\b.{0,80}\b(?:buy|fund|add|increase|allocate|recommend|recommended)\b"),
    ("internal_driver_id", r"\bdriver[_-][a-z0-9_\-]+\b"),
    ("shadow_payload_leak", r"\bdeterministic_regime_shadow\b|\bnone_shadow_comparison_only\b|\bclient_facing_authority\b"),
)

ORPHAN_MACRO_FIGURE_PATTERN = re.compile(
    r"\b(?:CPI|PCE|PMI|GDP|unemployment|payrolls|inflation|yields?|rates?|policy rate|terminal rate|10Y|2Y)\b[^\n]{0,100}\b\d+(?:\.\d+)?\s?(?:%|bp|bps|points?)(?=\s|$|[,.;:)])",
    re.IGNORECASE,
)

PROVENANCE_HINT_PATTERN = re.compile(
    r"\b(?:source|provenance|as[- ]of|fetched|series|provider|FRED|ECB|Treasury|BLS|BEA|Eurostat|ONS)\b",
    re.IGNORECASE,
)

OVERLAY_PATTERN = re.compile(r"\b(?:institutional overlay|consensus overlay|bank view|strategist view|broker view)\b", re.IGNORECASE)
CITATION_HINT_PATTERN = re.compile(r"\b(?:source|citation|cited|according to|paraphrased|as of|provider)\b|https?://", re.IGNORECASE)

REQUIRED_CAP_METHODOLOGY_PHRASES: tuple[str, ...] = (
    "stable shadow methodology rule",
    "risk-on shadow candidate",
    "macro_conflict_cap_threshold",
    "risk_on_macro_conflict_cap",
    "descriptive cross-axis agreement score",
    "not a forecast probability",
    "diagnostic only",
    "no client-facing, lane-scoring, fundability, or portfolio-action authority",
)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    line: int
    excerpt: str


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _excerpt(text: str, start: int, end: int, radius: int = 90) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = text[left:right].replace("\n", " ").strip()
    return re.sub(r"\s+", " ", snippet)


def _pattern_findings(text: str, patterns: Iterable[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for code, pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            findings.append(
                Finding(
                    code=code,
                    message=f"Blocked macro/thesis wording matched pattern: {code}",
                    line=_line_number(text, match.start()),
                    excerpt=_excerpt(text, match.start(), match.end()),
                )
            )
    return findings


def _orphan_macro_figure_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in ORPHAN_MACRO_FIGURE_PATTERN.finditer(text):
        window = text[max(0, match.start() - 160) : min(len(text), match.end() + 160)]
        if PROVENANCE_HINT_PATTERN.search(window):
            continue
        findings.append(
            Finding(
                code="orphan_macro_figure",
                message="Macro figure appears without nearby provenance/source/as-of context.",
                line=_line_number(text, match.start()),
                excerpt=_excerpt(text, match.start(), match.end()),
            )
        )
    return findings


def _uncited_overlay_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in OVERLAY_PATTERN.finditer(text):
        window = text[max(0, match.start() - 180) : min(len(text), match.end() + 220)]
        if CITATION_HINT_PATTERN.search(window):
            continue
        findings.append(
            Finding(
                code="uncited_overlay",
                message="Institutional/consensus overlay appears without citation or paraphrase/source hint.",
                line=_line_number(text, match.start()),
                excerpt=_excerpt(text, match.start(), match.end()),
            )
        )
    return findings


def validate_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_pattern_findings(text, PREDICTIVE_PATTERNS))
    findings.extend(_pattern_findings(text, STAGE1_LEAK_PATTERNS))
    findings.extend(_orphan_macro_figure_findings(text))
    findings.extend(_uncited_overlay_findings(text))
    return findings


def _extract_report_macro_sections(text: str) -> str:
    lines = text.splitlines()
    selected: list[str] = []
    for line in lines:
        if re.match(r"^##\s+5\.", line):
            break
        selected.append(line)
    return "\n".join(selected).strip() + "\n"


def _latest_report_artifacts(output_dir: Path) -> list[Path]:
    if not output_dir.exists():
        raise SystemExit(f"Report output directory not found: {output_dir}")
    english = sorted(p for p in output_dir.glob("weekly_analysis_pro_*.md") if "_nl_" not in p.name)
    dutch = sorted(output_dir.glob("weekly_analysis_pro_nl_*.md"))
    if not english:
        raise SystemExit("No English weekly_analysis_pro_*.md report artifact found")
    if not dutch:
        raise SystemExit("No Dutch weekly_analysis_pro_nl_*.md report artifact found")
    return [english[-1], dutch[-1]]


def validate_report_macro_sections(path: Path) -> list[Finding]:
    if not path.exists():
        return [Finding("report_artifact_missing", "Report artifact is missing.", 1, str(path))]
    text = path.read_text(encoding="utf-8")
    section = _extract_report_macro_sections(text)
    if not section.strip():
        return [Finding("report_macro_section_empty", "Report macro section extraction produced no text.", 1, str(path))]
    print(f"ETF_MACRO_COMPLIANCE_REPORT_SECTION_CHECK | path={path}")
    return validate_text(section)


def validate_cap_methodology(path: Path) -> list[Finding]:
    if not path.exists():
        return [Finding("cap_methodology_missing", "Macro conflict cap methodology note is missing.", 1, str(path))]
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    findings: list[Finding] = []
    for phrase in REQUIRED_CAP_METHODOLOGY_PHRASES:
        if phrase.lower() not in lower:
            findings.append(
                Finding(
                    "cap_methodology_phrase_missing",
                    f"Required macro conflict cap methodology phrase is missing: {phrase}",
                    1,
                    phrase,
                )
            )
    findings.extend(validate_text(text))
    return findings


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def validate_macro_pack(path: Path) -> list[Finding]:
    payload = _load_json(path)
    findings: list[Finding] = []

    authority = payload.get("authority")
    if isinstance(authority, dict):
        if authority.get("client_facing_authority") is True:
            findings.append(Finding("macro_pack_promoted_without_gate", "Macro pack has client-facing authority before compliance promotion.", 1, str(authority)))
    shadow = payload.get("deterministic_regime_shadow")
    if isinstance(shadow, dict):
        if shadow.get("client_facing_authority") is True:
            findings.append(Finding("shadow_payload_promoted", "deterministic_regime_shadow is marked client-facing.", 1, str(shadow)[:240]))
        if shadow.get("decision_impact") not in {None, "none_shadow_comparison_only"}:
            findings.append(Finding("shadow_decision_impact", "deterministic_regime_shadow has non-shadow decision impact.", 1, str(shadow)[:240]))

    flattened_strings: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, str):
            flattened_strings.append(value)
        elif isinstance(value, dict):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, list):
            for nested in value:
                collect(nested)

    collect(payload)
    findings.extend(validate_text("\n".join(flattened_strings)))
    return findings


def _print_findings(findings: list[Finding]) -> None:
    for finding in findings:
        print(f"MACRO_COMPLIANCE_FINDING | {finding.code} | line={finding.line} | {finding.message}")
        print(f"  excerpt: {finding.excerpt}")


def run_self_test() -> None:
    safe_text = """
    The model describes current conditions only. Inflation was 2.7% as of 2026-05-29; source FRED CPI series, fetched 2026-05-31.
    The regime label is a descriptive classification, not a forecast. Candidate lanes remain internal until confirmation gates pass.
    """
    bad_cases = {
        "predictive": "The Fed will cut rates next month and equities will rally.",
        "orphan_figure": "CPI is 3.2% and this changes the regime.",
        "overlay": "The institutional overlay says investors are bullish.",
        "candidate": "Stage-1 thesis candidate should be recommended for funding now.",
        "shadow_leak": "deterministic_regime_shadow shows client_facing_authority false.",
    }
    if validate_text(safe_text):
        raise SystemExit("Self-test failed: safe text produced findings")
    for name, text in bad_cases.items():
        if not validate_text(text):
            raise SystemExit(f"Self-test failed: bad case did not fail: {name}")
    print("ETF_MACRO_COMPLIANCE_SELF_TEST_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", type=Path, action="append", default=[], help="Text/markdown report file to validate")
    parser.add_argument("--macro-pack", type=Path, action="append", default=[], help="Macro policy pack JSON to validate")
    parser.add_argument("--cap-methodology", type=Path, action="append", default=[], help="Macro conflict cap methodology note to validate")
    parser.add_argument("--report-macro-sections", type=Path, action="append", default=[], help="Report artifact whose macro-sensitive sections should be validated")
    parser.add_argument("--latest-report-macro-sections", action="store_true", help="Validate macro-sensitive sections of latest committed English and Dutch report artifacts")
    parser.add_argument("--report-output-dir", type=Path, default=Path("output"), help="Directory containing committed report artifacts")
    parser.add_argument("--self-test", action="store_true", help="Run embedded positive and negative validator tests")
    parser.add_argument("--expect-fail", action="store_true", help="Exit 0 only if findings are produced")
    args = parser.parse_args()

    findings: list[Finding] = []
    if args.self_test:
        run_self_test()
    for path in args.text:
        if not path.exists():
            raise SystemExit(f"Text file not found: {path}")
        findings.extend(validate_text(path.read_text(encoding="utf-8")))
    for path in args.macro_pack:
        if not path.exists():
            raise SystemExit(f"Macro pack not found: {path}")
        findings.extend(validate_macro_pack(path))
    for path in args.cap_methodology:
        findings.extend(validate_cap_methodology(path))
    for path in args.report_macro_sections:
        findings.extend(validate_report_macro_sections(path))
    if args.latest_report_macro_sections:
        for path in _latest_report_artifacts(args.report_output_dir):
            findings.extend(validate_report_macro_sections(path))

    if args.expect_fail:
        if findings:
            _print_findings(findings)
            print("ETF_MACRO_COMPLIANCE_EXPECTED_FAILURE_OK")
            return
        raise SystemExit("Expected macro compliance findings, but none were produced")

    if findings:
        _print_findings(findings)
        raise SystemExit(f"ETF_MACRO_COMPLIANCE_FAILED | findings={len(findings)}")

    print("ETF_MACRO_COMPLIANCE_OK")


if __name__ == "__main__":
    main()
