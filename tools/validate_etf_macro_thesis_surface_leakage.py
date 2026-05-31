#!/usr/bin/env python3
"""Block Stage-1/Stage-2 macro/thesis artifact leakage from ETF client outputs.

This is a production-output guard. It does not promote macro/thesis artifacts; it
only prevents internal shadow vocabulary, status labels, driver IDs, authority
fields, and artifact names from appearing in English/Dutch markdown or delivery
HTML.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
DELIVERY_HTML_RE = re.compile(r"^weekly_analysis_pro(?:_nl)?_\d{6}(?:_\d{2})?_delivery\.html$")

# Exact or near-exact internal labels that should never reach client output.
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (code, re.compile(pattern, re.IGNORECASE))
    for code, pattern in [
        ("stage1_status_label", r"\bstage[_ -]?1[_ -]?(?:shadow[_ -]?)?candidate(?:[_ -]only)?\b"),
        ("stage2_status_label", r"\bstage[_ -]?2[_ -]?(?:confirmed[_ -]not[_ -]fundable|fundable[_ -]ready[_ -]shadow)\b"),
        ("stage1_thesis_candidate_phrase", r"\bStage[- ]?1\s+thesis\s+candidate\b"),
        ("stage2_confirmation_phrase", r"\bStage[- ]?2\s+confirmation\b"),
        ("dutch_stage_candidate_phrase", r"\bFase[- ]?[12]\s+(?:these|thesis|kandidaat|confirmatie)\b"),
        ("not_fundable_stage1", r"\bnot[_ -]?fundable[_ -]?stage[_ -]?1[_ -]?only\b"),
        ("requires_stage2", r"\brequires[_ -]?stage[_ -]?2[_ -]?confirmation\b"),
        ("shadow_only_field", r"\bshadow_only\b"),
        ("shadow_internal_label", r"\b(?:shadow[- ]only|shadow\s+artifact|shadow\s+validation|shadow\s+candidate)\b"),
        ("client_facing_authority_field", r"\bclient_facing_authority\b"),
        ("portfolio_action_authority_field", r"\bportfolio_action_authority\b"),
        ("fundability_authority_field", r"\bfundability_authority\b"),
        ("lane_scoring_authority_field", r"\blane_scoring_authority\b"),
        ("report_surface_allowed_field", r"\breport_surface_allowed\b"),
        ("internal_decision_impact", r"\bnone_(?:stage1|stage2|shadow|stage_1|stage_2)[a-z0-9_\-]*\b"),
        ("deterministic_shadow_payload", r"\bdeterministic_regime_shadow\b"),
        ("thesis_artifact_name", r"\b(?:latest_)?thesis_candidates\b"),
        ("stage2_artifact_name", r"\b(?:latest_)?stage2_confirmation\b"),
        ("macro_validation_artifact", r"\b(?:macro_regime_shadow_validation|stage2_confirmation_validation)\b"),
        ("workflow_marker", r"\bETF_(?:THESIS_CANDIDATES|STAGE2_CONFIRMATION|MACRO_REGIME_SHADOW)[A-Z0-9_]*\b"),
        ("driver_id_ai", r"\bai_compute_capex\b"),
        ("driver_id_grid", r"\bgrid_power_demand\b"),
        ("driver_id_defense", r"\bdefense_resilience\b"),
        ("driver_id_nuclear", r"\bnuclear_energy_security\b"),
        ("driver_id_china", r"\bchina_policy_recovery\b"),
        ("driver_id_non_us", r"\bnon_us_developed_diversification\b"),
        ("driver_id_healthcare", r"\bhealthcare_defensive_growth\b"),
        ("driver_id_duration", r"\bduration_easing_long_duration\b"),
        ("driver_id_commodity", r"\bcommodity_inflation_hedge\b"),
    ]
)


@dataclass(frozen=True)
class Finding:
    file: Path
    code: str
    line: int
    excerpt: str


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _excerpt(text: str, start: int, end: int, radius: int = 90) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return re.sub(r"\s+", " ", text[left:right].replace("\n", " ")).strip()


def _explicit_path(env_name: str, pattern: re.Pattern[str]) -> Path | None:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return None
    path = Path(raw)
    if path.exists() and pattern.match(path.name):
        return path
    return None


def _latest(output_dir: Path, pattern: re.Pattern[str]) -> Path | None:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    return reports[-1] if reports else None


def _matching_delivery_html(report_path: Path) -> Path | None:
    candidate = report_path.with_name(report_path.stem + "_delivery.html")
    return candidate if candidate.exists() else None


def current_client_files(output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    en = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH", EN_RE) or _latest(output_dir, EN_RE)
    nl = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", NL_RE) or _latest(output_dir, NL_RE)
    for report in (en, nl):
        if report is None:
            continue
        paths.append(report)
        html = _matching_delivery_html(report)
        if html is not None:
            paths.append(html)
    # Include any current delivery HTML files even if explicit report env vars are absent.
    for html in sorted(output_dir.glob("weekly_analysis_pro*_delivery.html")):
        if DELIVERY_HTML_RE.match(html.name) and html not in paths:
            paths.append(html)
    return paths


def scan_text(text: str, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for code, pattern in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                Finding(
                    file=path,
                    code=code,
                    line=_line_number(text, match.start()),
                    excerpt=_excerpt(text, match.start(), match.end()),
                )
            )
    return findings


def scan_file(path: Path) -> list[Finding]:
    return scan_text(path.read_text(encoding="utf-8", errors="ignore"), path)


def validate_files(paths: Iterable[Path]) -> None:
    findings: list[Finding] = []
    for path in paths:
        if path.exists():
            findings.extend(scan_file(path))
    if findings:
        for finding in findings[:40]:
            print(
                "ETF_MACRO_THESIS_SURFACE_LEAK_FINDING | "
                f"file={finding.file.name} | code={finding.code} | line={finding.line} | excerpt={finding.excerpt}"
            )
        raise RuntimeError(f"ETF macro/thesis surface leakage detected: findings={len(findings)}")


def run_self_test() -> None:
    safe = """
    The report describes current macro conditions. AI infrastructure remains relevant, but any portfolio action requires ordinary scoring, pricing, and risk discipline.
    De Nederlandse samenvatting beschrijft de marktomgeving zonder interne modelstatussen te tonen.
    """
    unsafe_cases = {
        "stage1": "Stage-1 thesis candidate should be reviewed.",
        "stage2": "stage_2_fundable_ready_shadow is visible here.",
        "authority": "client_facing_authority is false.",
        "artifact": "output/macro/latest_thesis_candidates.json",
        "driver": "ai_compute_capex activated the lane.",
        "dutch": "Fase-2 confirmatie is nodig.",
    }
    safe_findings = scan_text(safe, Path("safe"))
    if safe_findings:
        raise SystemExit(f"Self-test safe text unexpectedly failed: {safe_findings}")
    for name, text in unsafe_cases.items():
        if not scan_text(text, Path(name)):
            raise SystemExit(f"Self-test unsafe case did not fail: {name}")
    print("ETF_MACRO_THESIS_SURFACE_LEAKAGE_SELF_TEST_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--file", action="append", default=[], help="Explicit file to scan; may be repeated")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    paths = [Path(value) for value in args.file] if args.file else current_client_files(Path(args.output_dir))
    if not paths and not args.self_test:
        raise RuntimeError(f"No ETF client output files found in {args.output_dir}")
    validate_files(paths)
    if paths:
        print("ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK | files=" + ",".join(path.name for path in paths))


if __name__ == "__main__":
    main()
