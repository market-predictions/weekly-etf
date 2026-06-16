#!/usr/bin/env python3
"""Block Stage-1/Stage-2 macro/thesis artifact leakage from ETF client outputs.

This is a production-output guard. It does not promote macro/thesis artifacts; it
only prevents internal shadow vocabulary, status labels, driver IDs, authority
fields, and artifact names from appearing in English/Dutch markdown, clean
markdown, or delivery HTML.
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


@dataclass(frozen=True)
class ForbiddenPattern:
    code: str
    pattern: re.Pattern[str]
    reason: str


# Exact or near-exact internal labels that should never reach client output.
FORBIDDEN_PATTERNS: tuple[ForbiddenPattern, ...] = tuple(
    ForbiddenPattern(code, re.compile(pattern, re.IGNORECASE), reason)
    for code, pattern, reason in [
        (
            "stage1_status_label",
            r"\bstage[_ -]?1[_ -]?(?:shadow[_ -]?)?candidate(?:[_ -]only)?\b",
            "Stage-1 candidate status is an internal shadow state, not a client-facing report label.",
        ),
        (
            "stage2_status_label",
            r"\bstage[_ -]?2[_ -]?(?:confirmed[_ -]not[_ -]fundable|fundable[_ -]ready[_ -]shadow)\b",
            "Stage-2 confirmation/fundability status is shadow-only and not report-surface authority.",
        ),
        (
            "stage2_confirmation_label",
            r"\bstage[_ -]?2[_ -]?confirmation\b",
            "Stage-2 confirmation is an internal gate and must not appear as client-surface plumbing.",
        ),
        (
            "stage1_thesis_candidate_phrase",
            r"\bStage[- ]?1\s+thesis\s+candidate\b",
            "Stage-1 thesis candidates must stay internal until an explicit future promotion decision.",
        ),
        (
            "stage2_confirmation_phrase",
            r"\bStage[- ]?2\s+confirmation\b",
            "Stage-2 confirmation must stay internal until an explicit future promotion decision.",
        ),
        (
            "stage2_fundable_ready_phrase",
            r"\bStage[- ]?2\s+fundable[- ]ready\s+shadow\b",
            "Fundable-ready shadow status is not a recommendation or report-surface claim.",
        ),
        (
            "dutch_stage_candidate_phrase",
            r"\bFase[- ]?[12]\s+(?:these|thesis|kandidaat|confirmatie)\b",
            "Dutch client output must not expose internal Stage-1/Stage-2 gate wording.",
        ),
        (
            "not_fundable_stage1",
            r"\bnot[_ -]?fundable[_ -]?stage[_ -]?1[_ -]?only\b",
            "Internal fundability gate state must not leak to client output.",
        ),
        (
            "requires_stage2",
            r"\brequires[_ -]?stage[_ -]?2[_ -]?confirmation\b",
            "Internal Stage-2 gate requirements must remain outside client output.",
        ),
        (
            "shadow_only_field",
            r"\bshadow_only\b",
            "Authority fields from shadow artifacts must not appear in client output.",
        ),
        (
            "internal_only_field",
            r"\binternal_only\b",
            "Internal-only artifact fields must not appear in client output.",
        ),
        (
            "shadow_internal_label",
            r"\b(?:shadow[- ]only|shadow\s+artifact|shadow\s+validation|shadow\s+candidate)\b",
            "Shadow artifact labels are operational metadata, not client-facing wording.",
        ),
        (
            "client_facing_authority_field",
            r"\bclient_facing_authority\b",
            "Raw authority fields must not appear in client output.",
        ),
        (
            "decision_impact_shadow_field",
            r"\bdecision_impact\s*:\s*none_stage2_confirmation_shadow_only\b",
            "Raw decision-impact metadata must not appear in client output.",
        ),
        (
            "portfolio_action_authority_field",
            r"\bportfolio_action_authority\b",
            "Raw authority fields must not appear in client output.",
        ),
        (
            "fundability_authority_field",
            r"\bfundability_authority\b",
            "Raw authority fields must not appear in client output.",
        ),
        (
            "lane_scoring_authority_field",
            r"\blane_scoring_authority\b",
            "Raw authority fields must not appear in client output.",
        ),
        (
            "report_surface_allowed_field",
            r"\breport_surface_allowed\b",
            "Raw report-surface authority fields must not appear in client output.",
        ),
        (
            "internal_decision_impact",
            r"\bnone_(?:stage1|stage2|shadow|stage_1|stage_2)[a-z0-9_\-]*\b",
            "Internal no-authority decision-impact labels must not appear in client output.",
        ),
        (
            "deterministic_shadow_payload",
            r"\bdeterministic_regime_shadow\b",
            "Raw deterministic-regime shadow payload names must not appear in client output.",
        ),
        (
            "thesis_artifact_name",
            r"\b(?:latest_)?thesis_candidates\b",
            "Thesis-candidate artifact names are internal and shadow-only.",
        ),
        (
            "stage2_artifact_name",
            r"\b(?:latest_)?stage[_]?2_confirmation\b",
            "Stage-2 confirmation artifact names are internal and shadow-only.",
        ),
        (
            "macro_validation_artifact",
            r"\b(?:macro_regime_shadow_validation|stage[_]?2_confirmation_validation)\b",
            "Validation artifact names must not leak to client output.",
        ),
        (
            "driver_catalog_artifact",
            r"\bdriver_catalog\b",
            "Driver catalog names are internal macro/thesis configuration, not client-facing wording.",
        ),
        (
            "driver_beneficiary_map_artifact",
            r"\bdriver_beneficiary_map\b",
            "Driver-beneficiary map names are internal macro/thesis configuration, not client-facing wording.",
        ),
        (
            "active_drivers_field",
            r"\bactive_drivers\b",
            "Raw active-driver fields must not appear in client output.",
        ),
        (
            "driver_id_field",
            r"\bdriver_ids?\b",
            "Raw driver-id fields must not appear in client output.",
        ),
        (
            "beneficiary_map_field",
            r"\bbeneficiary_map\b",
            "Raw beneficiary-map fields must not appear in client output.",
        ),
        (
            "confirmation_status_field",
            r"\bconfirmation_status\b",
            "Raw confirmation-status fields must not appear in client output.",
        ),
        (
            "stage2_status_field",
            r"\bstage2_status\b",
            "Raw Stage-2 status fields must not appear in client output.",
        ),
        (
            "fundable_ready_shadow_label",
            r"\bfundable[_ -]?ready[_ -]?shadow\b",
            "Fundable-ready shadow status is not a recommendation or report-surface claim.",
        ),
        (
            "workflow_marker",
            r"\bETF_(?:THESIS_CANDIDATES|STAGE2_CONFIRMATION|MACRO_REGIME_SHADOW)[A-Z0-9_]*\b",
            "Workflow markers are operational metadata, not client-facing wording.",
        ),
        (
            "driver_id_ai",
            r"\bai_compute_capex\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_grid",
            r"\bgrid_power_demand\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_defense",
            r"\bdefense_resilience\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_nuclear",
            r"\bnuclear_energy_security\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_china",
            r"\bchina_policy_recovery\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_non_us",
            r"\bnon_us_developed_diversification\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_healthcare",
            r"\bhealthcare_defensive_growth\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_duration",
            r"\bduration_easing_long_duration\b",
            "Raw driver IDs must not appear in client output.",
        ),
        (
            "driver_id_commodity",
            r"\bcommodity_inflation_hedge\b",
            "Raw driver IDs must not appear in client output.",
        ),
    ]
)


@dataclass(frozen=True)
class Finding:
    file: Path
    code: str
    line: int
    matched: str
    reason: str
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
    if not path.exists():
        raise RuntimeError(f"Explicit ETF report path from {env_name} does not exist: {path}")
    if not pattern.match(path.name):
        raise RuntimeError(f"Explicit ETF report path from {env_name} is not canonical for this guard: {path}")
    return path


def _latest(output_dir: Path, pattern: re.Pattern[str]) -> Path | None:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    return reports[-1] if reports else None


def _matching_client_companions(report_path: Path) -> list[Path]:
    candidates = [
        report_path.with_name(report_path.stem + "_clean.md"),
        report_path.with_name(report_path.stem + "_delivery.html"),
    ]
    return [candidate for candidate in candidates if candidate.exists()]


def current_client_files(output_dir: Path) -> list[Path]:
    """Return the current EN/NL client-surface files without stale HTML fallback.

    Explicit current report paths win when supplied by the production workflow. This
    avoids the prior stale-artifact class of bug where validators accidentally
    inspected a lexicographically latest delivery HTML file instead of the current
    run's report pair.
    """

    en = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH", EN_RE)
    nl = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", NL_RE)
    if en is None and nl is None:
        en = _latest(output_dir, EN_RE)
        nl = _latest(output_dir, NL_RE)

    paths: list[Path] = []
    for report in (en, nl):
        if report is None:
            continue
        paths.append(report)
        paths.extend(_matching_client_companions(report))
    return paths


def scan_text(text: str, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for forbidden in FORBIDDEN_PATTERNS:
        for match in forbidden.pattern.finditer(text):
            findings.append(
                Finding(
                    file=path,
                    code=forbidden.code,
                    line=_line_number(text, match.start()),
                    matched=match.group(0),
                    reason=forbidden.reason,
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
                f"file={finding.file} | code={finding.code} | line={finding.line} | "
                f"matched={finding.matched!r} | reason={finding.reason} | excerpt={finding.excerpt}"
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
        "decision_impact": "decision_impact: none_stage2_confirmation_shadow_only",
        "artifact": "output/macro/latest_thesis_candidates.json",
        "driver_catalog": "config/driver_catalog.yml",
        "driver_field": "driver_id=ai_compute_capex",
        "beneficiary_map": "driver_beneficiary_map activated this lane.",
        "stage2_status": "stage2_status is fundable_ready_shadow.",
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
