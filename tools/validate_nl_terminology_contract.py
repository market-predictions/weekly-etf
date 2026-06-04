#!/usr/bin/env python3
"""Validate the central Dutch terminology contract.

This is a guardrail for Dutch output quality. It verifies that the central
terminology module is usable by legacy localization, that native Dutch runtime
reports remain guard-only, and that runtime.nl_localization sources its alias
maps from runtime.nl_terminology rather than maintaining duplicate dictionaries.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import nl_localization as loc
from runtime import nl_terminology as term
from runtime.apply_nl_localization import localize_report
from runtime.nl_localization import localize_text
from runtime.scrub_nl_client_language import scrub_text
from tools.validate_etf_dutch_language_quality import _failures_for_text


REQUIRED_MAPS = [
    "REPORT_LABELS",
    "TABLE_LABELS",
    "ACTION_REPLACEMENTS",
    "ROLE_TRANSLATIONS",
    "THESIS_TRANSLATIONS",
    "LANE_TRANSLATIONS",
    "PHRASE_REPLACEMENTS",
    "CLIENT_LANGUAGE_CLEANUPS",
    "EXACT_CLIENT_LANGUAGE_REPLACEMENTS",
    "REGEX_CLIENT_LANGUAGE_REPLACEMENTS",
    "FORBIDDEN_CLIENT_LABELS",
    "FORBIDDEN_AFTER_SCRUB",
]

CLIENT_FACING_VALUE_MAPS = [
    "REPORT_LABELS",
    "TABLE_LABELS",
    "ACTION_REPLACEMENTS",
    "ROLE_TRANSLATIONS",
    "THESIS_TRANSLATIONS",
    "LANE_TRANSLATIONS",
    "PHRASE_REPLACEMENTS",
    "CLIENT_LANGUAGE_CLEANUPS",
    "EXACT_CLIENT_LANGUAGE_REPLACEMENTS",
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

FORBIDDEN_IN_CLIENT_FACING_VALUES = [
    "Neetable",
    "Toevoegened",
    "Verlagend",
    "Sluitend",
    "Aanhouden but replaceable",
]

KNOWN_BAD_OUTPUT_TOKENS = [
    "Neetable",
    "Toevoegened",
    "Verlagend",
    "Sluitend",
    "Neeg",
]


class ContractError(RuntimeError):
    pass


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _assert_same(name: str, left: object, right: object) -> None:
    _assert(left is right, f"{name} is not sourced from runtime.nl_terminology")


def validate_localization_aliases_are_centralized() -> None:
    _assert_same("DUTCH_DISCLAIMER", loc.DUTCH_DISCLAIMER, term.DUTCH_DISCLAIMER)
    _assert_same("ALLOWED_ENGLISH_TERMS", loc.ALLOWED_ENGLISH_TERMS, term.ALLOWED_ENGLISH_TERMS)
    _assert_same("LABELS", loc.LABELS, term.REPORT_LABELS)
    _assert_same("TABLE_LABELS", loc.TABLE_LABELS, term.TABLE_LABELS)
    _assert_same("ACTION_REPLACEMENTS", loc.ACTION_REPLACEMENTS, term.ACTION_REPLACEMENTS)
    _assert_same("PHRASE_REPLACEMENTS", loc.PHRASE_REPLACEMENTS, term.PHRASE_REPLACEMENTS)
    _assert_same("DECISION_TRANSLATIONS", loc.DECISION_TRANSLATIONS, term.DECISION_TRANSLATIONS)
    _assert_same("TRIGGER_TRANSLATIONS", loc.TRIGGER_TRANSLATIONS, term.TRIGGER_TRANSLATIONS)
    _assert_same("FORBIDDEN_NL_STRINGS", loc.FORBIDDEN_NL_STRINGS, term.FORBIDDEN_NL_STRINGS)


def validate_maps() -> None:
    combined = term.combined_text_replacements()
    for name in REQUIRED_MAPS:
        value = getattr(term, name, None)
        _assert(value is not None, f"missing central terminology object: {name}")
        _assert(len(value) > 0, f"central terminology object is empty: {name}")
    for src, expected in REQUIRED_TRANSLATIONS.items():
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
    for name in CLIENT_FACING_VALUE_MAPS:
        payload = getattr(term, name)
        if isinstance(payload, dict):
            values.extend(str(v) for v in payload.values())
        elif isinstance(payload, list | tuple | set):
            values.extend(str(v) for v in payload)
    for _pattern, replacement in term.REGEX_CLIENT_LANGUAGE_REPLACEMENTS:
        values.append(str(replacement))
    joined = "\n".join(values)
    for token in FORBIDDEN_IN_CLIENT_FACING_VALUES:
        _assert(token not in joined, f"forbidden low-quality Dutch token appears in client-facing terminology values: {token}")


def validate_known_bad_tokens_are_repaired_or_blocked_in_legacy_mode() -> None:
    forbidden_joined = "\n".join(str(token) for token in term.FORBIDDEN_AFTER_SCRUB)
    for token in KNOWN_BAD_OUTPUT_TOKENS:
        repaired = scrub_text(token, native_dutch=False)
        if token not in repaired:
            continue
        _assert(token in forbidden_joined, f"known bad token is neither repaired by legacy scrub_text nor present in forbidden guard: {token}")


def validate_legacy_runtime_overlay() -> None:
    sample = "## 1. Executive Summary\n\n| Theme | Primary ETF | What needs to happen |\n|---|---|---|\n| AI compute infrastructure | SMH | Hold but replaceable |"
    localized = localize_text(sample, language="nl")
    scrubbed = scrub_text(localized, native_dutch=False)
    required = ["Kernsamenvatting", "Thema", "Primaire ETF", "Benodigde bevestiging", "Aanhouden, maar vervangbaar"]
    for token in required:
        _assert(token in scrubbed, f"legacy runtime overlay missing expected Dutch token: {token}")
    forbidden = ["Executive Summary", "What needs to happen", "Hold but replaceable"]
    for token in forbidden:
        _assert(token not in scrubbed, f"legacy runtime overlay left forbidden English token: {token}")


def validate_native_dutch_guard_only_overlay() -> None:
    native = """# Wekelijkse ETF-review

## 1. Kernsamenvatting
## 2. Portefeuille-acties
## 3. Regime-dashboard
## 10. Review huidige posities
## 12. Rotatieplan portefeuille
## 15. Huidige posities en cash
## 16. Input voor de volgende run

Nog geen alternatief is sterk genoeg om direct te financieren.

## 17. Disclaimer

Old placeholder disclaimer.
"""
    localized = localize_report(native)
    scrubbed = scrub_text(localized, native_dutch=True)
    required = [
        "Nog geen alternatief is sterk genoeg om direct te financieren.",
        term.DUTCH_DISCLAIMER,
    ]
    for token in required:
        _assert(token in scrubbed, f"native Dutch guard-only output missing expected token: {token}")
    forbidden = ["Neeg", "Old placeholder disclaimer"]
    for token in forbidden:
        _assert(token not in scrubbed, f"native Dutch guard-only output left forbidden token: {token}")
    quality_failures = _failures_for_text(scrubbed)
    if quality_failures:
        raise ContractError("native Dutch guard-only output fails Dutch quality: " + "; ".join(quality_failures))


def validate_native_dutch_does_not_translate_english_leakage() -> None:
    native_with_leak = """# Wekelijkse ETF-review

## 1. Kernsamenvatting
## 2. Portefeuille-acties
## 3. Regime-dashboard
## 10. Review huidige posities
## 15. Huidige posities en cash

Replacement trigger watch — challenger leading over 3m.

## 17. Disclaimer

Old placeholder disclaimer.
"""
    localized = localize_report(native_with_leak)
    _assert("Replacement trigger watch" in localized, "native guard-only mode incorrectly translated an English leakage phrase")
    failures = _failures_for_text(localized)
    _assert(any("Replacement trigger watch" in failure for failure in failures), "native English leakage did not fail Dutch quality validation")


def validate_regex_entries() -> None:
    for pattern, _replacement in term.REGEX_CLIENT_LANGUAGE_REPLACEMENTS:
        re.compile(pattern, re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run embedded central terminology checks")
    parser.parse_args()
    validate_localization_aliases_are_centralized()
    validate_maps()
    validate_bad_value_absence()
    validate_known_bad_tokens_are_repaired_or_blocked_in_legacy_mode()
    validate_regex_entries()
    validate_legacy_runtime_overlay()
    validate_native_dutch_guard_only_overlay()
    validate_native_dutch_does_not_translate_english_leakage()
    print("ETF_NL_TERMINOLOGY_CONTRACT_OK | source=runtime.nl_terminology")


if __name__ == "__main__":
    main()
