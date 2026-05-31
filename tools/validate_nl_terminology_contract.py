#!/usr/bin/env python3
"""Validate the central Dutch terminology contract.

This is a Phase 7 guardrail. It verifies that the central terminology module is
usable by localization, scrubbing, and Dutch quality validation layers, without
changing production report content by itself.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import nl_terminology as term
from runtime.scrub_nl_client_language import scrub_text
from runtime.nl_localization import localize_text


REQUIRED_MAPS = [
    "REPORT_LABELS",
    "TABLE_LABELS",
    "ACTION_REPLACEMENTS",
    "ROLE_TRANSLATIONS",
    "THESIS_TRANSLATIONS",
    "LANE_TRANSLATIONS",
    "PHRASE_REPLACEMENTS",
    "CLIENT_LANGUAGE_CLEANUPS",
    "FORBIDDEN_CLIENT_LABELS",
    "FORBIDDEN_AFTER_SCRUB",
]

REQUIRED_TRANSLATIONS = {
    "Executive Summary": "Kernsamenvatting",
    "Portfolio Action Snapshot": "Portefeuille-acties",
    "Current Position Review": "Review huidige posities",
    "Portfolio Rotation Plan": "Rotatieplan portefeuille",
    "Current Portfolio Holdings and Cash": "Huidige posities en cash",
    "AI compute infrastructure": "AI-rekenkrachtinfrastructuur",
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
    "Replacement Duel Table": "Vervangingsanalyse",
}

FORBIDDEN_IN_CENTRAL_VALUES = [
    "Neetable",
    "Toevoegened",
    "Verlagend",
    "Sluitend",
    "Aanhouden but replaceable",
]


class ContractError(RuntimeError):
    pass


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_maps() -> None:
    for name in REQUIRED_MAPS:
        value = getattr(term, name, None)
        _assert(value is not None, f"missing central terminology object: {name}")
        _assert(len(value) > 0, f"central terminology object is empty: {name}")
    for src, expected in REQUIRED_TRANSLATIONS.items():
        combined = term.combined_text_replacements()
        actual = (
            combined.get(src)
            or term.LANE_TRANSLATIONS.get(src)
            or term.ACTION_REPLACEMENTS.get(src)
            or term.REPORT_LABELS.get(src)
            or term.TABLE_LABELS.get(src)
        )
        _assert(actual == expected, f"translation mismatch for {src!r}: {actual!r} != {expected!r}")


def validate_bad_value_absence() -> None:
    values = []
    for name in REQUIRED_MAPS:
        payload = getattr(term, name)
        if isinstance(payload, dict):
            values.extend(str(v) for v in payload.values())
        elif isinstance(payload, list | tuple | set):
            values.extend(str(v) for v in payload)
    joined = "\n".join(values)
    for token in FORBIDDEN_IN_CENTRAL_VALUES:
        _assert(token not in joined, f"forbidden low-quality Dutch token appears in central values: {token}")


def validate_runtime_overlay() -> None:
    sample = "## 1. Executive Summary\n\n| Theme | Primary ETF | What needs to happen |\n|---|---|---|\n| AI compute infrastructure | SMH | Hold but replaceable |"
    localized = localize_text(sample, language="nl")
    scrubbed = scrub_text(localized)
    required = ["Kernsamenvatting", "Thema", "Primaire ETF", "Benodigde bevestiging", "Aanhouden, maar vervangbaar"]
    for token in required:
        _assert(token in scrubbed, f"runtime overlay missing expected Dutch token: {token}")
    forbidden = ["Executive Summary", "What needs to happen", "Hold but replaceable"]
    for token in forbidden:
        _assert(token not in scrubbed, f"runtime overlay left forbidden English token: {token}")


def validate_regex_entries() -> None:
    for pattern, _replacement in term.REGEX_CLIENT_LANGUAGE_REPLACEMENTS:
        re.compile(pattern, re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run embedded central terminology checks")
    args = parser.parse_args()
    validate_maps()
    validate_bad_value_absence()
    validate_regex_entries()
    validate_runtime_overlay()
    print("ETF_NL_TERMINOLOGY_CONTRACT_OK")


if __name__ == "__main__":
    main()
