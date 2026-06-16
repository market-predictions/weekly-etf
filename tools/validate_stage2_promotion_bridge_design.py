#!/usr/bin/env python3
"""Validate the Stage-2 promotion bridge design document.

This is a design-document validator only. It must not promote Stage-2 output
into report wording, lane scoring, fundability, portfolio actions, delivery,
execution, or historical-output mutation authority.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DESIGN_PATH = Path("control/STAGE2_PROMOTION_BRIDGE_DESIGN.md")

REQUIRED_FALSE_FIELDS = [
    "client_facing_authority: false",
    "production_report_narrative_authority: false",
    "portfolio_action_authority: false",
    "lane_scoring_authority: false",
    "fundability_authority: false",
    "portfolio_mutation: false",
    "historical_output_mutation: false",
    "delivery_authority: false",
    "execution_authority: false",
]

REQUIRED_PHRASES = [
    "Design-only. No production wiring.",
    "Stage-2 confirmation remains shadow-only until a later explicit promotion decision exists.",
    "config/macro_thesis_bilingual_aliases.yml",
    "bilingual sanitized alias exists if client wording is proposed",
    "leakage firewall passes",
    "macro/report-surface compliance passes",
    "pricing-lineage validation is complete",
    "explicit control-layer promotion decision",
    "separate future implementation package",
    "does not change production report output",
    "lane scoring",
    "fundability",
    "portfolio actions",
    "delivery behavior",
    "execution behavior",
    "historical output files",
]

FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (reason, re.compile(pattern, re.IGNORECASE))
    for reason, pattern in [
        ("claims Stage-2 is currently promoted", r"\bstage[- ]?2\s+(?:is\s+now|is|has\s+been|now)\s+promoted\b"),
        ("claims Stage-2 output is promoted", r"\bstage[- ]?2\s+output\s+(?:is\s+now|is|has\s+been|now)\s+promoted\b"),
        ("grants client-facing authority", r"\bclient_facing_authority\s*:\s*true\b"),
        ("grants production report narrative authority", r"\bproduction_report_narrative_authority\s*:\s*true\b"),
        ("grants portfolio-action authority", r"\bportfolio_action_authority\s*:\s*true\b"),
        ("grants lane-scoring authority", r"\blane_scoring_authority\s*:\s*true\b"),
        ("grants fundability authority", r"\bfundability_authority\s*:\s*true\b"),
        ("grants delivery authority", r"\bdelivery_authority\s*:\s*true\b"),
        ("grants execution authority", r"\bexecution_authority\s*:\s*true\b"),
        ("grants historical-output mutation authority", r"\bhistorical_output_mutation\s*:\s*true\b"),
        ("claims direct production wiring", r"\bdirectly\s+wires?\s+stage[- ]?2\s+into\s+production\b"),
    ]
)


@dataclass(frozen=True)
class DesignFinding:
    code: str
    detail: str


def validate_text(text: str) -> None:
    findings: list[DesignFinding] = []

    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            findings.append(DesignFinding("missing_required_phrase", phrase))

    for field in REQUIRED_FALSE_FIELDS:
        if field not in text:
            findings.append(DesignFinding("missing_false_authority_field", field))

    for reason, pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append(DesignFinding("forbidden_promotion_or_authority_claim", f"{reason}: {match.group(0)}"))

    required_sections = [
        "## Purpose",
        "## Authority boundaries",
        "## Prerequisite artifacts",
        "## Eligible evidence fields",
        "## Forbidden direct-use fields",
        "## Bilingual alias dependency",
        "## Promotion-review checklist",
        "## Explicit non-goals",
        "## Future implementation gate",
    ]
    for section in required_sections:
        if section not in text:
            findings.append(DesignFinding("missing_required_section", section))

    if findings:
        for finding in findings:
            print(f"STAGE2_PROMOTION_BRIDGE_DESIGN_FINDING | code={finding.code} | detail={finding.detail}")
        raise RuntimeError(f"Stage-2 promotion bridge design validation failed: findings={len(findings)}")


def validate_design_file(path: Path = DEFAULT_DESIGN_PATH) -> None:
    if not path.exists():
        raise RuntimeError(f"Stage-2 promotion bridge design file does not exist: {path}")
    validate_text(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design-file", type=Path, default=DEFAULT_DESIGN_PATH)
    args = parser.parse_args()

    validate_design_file(args.design_file)
    print(f"STAGE2_PROMOTION_BRIDGE_DESIGN_OK | file={args.design_file}")


if __name__ == "__main__":
    main()
