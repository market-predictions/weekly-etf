from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCHEMA_VERSION = "macro_narrative_client_surface_v1"
REQUIRED_LANGUAGE_KEYS = ("en", "nl")

BLOCKED_KEYS = {
    "macro_axes",
    "confidence_decomposition",
}

INTERNAL_LABEL_PATTERNS = {
    "en": [
        r"\bshadow(?:[-_ ]only)?\b",
        r"\binternal\b",
        r"\boperator[- ]facing\b",
        r"\bdiagnostic\b",
        r"\bclient_facing\s*=\s*false\b",
        r"\bproduction_report\s*=\s*false\b",
        r"\bmacro_axes\b",
        r"\bconfidence_decomposition\b",
        r"\bdeterministic_regime_shadow\b",
        r"\bregime shadow\b",
    ],
    "nl": [
        r"\bschaduw(?:[- ]?only)?\b",
        r"\bintern(?:e)?\b",
        r"\boperator[- ]gericht\b",
        r"\bdiagnostisch\b",
        r"\bclient_facing\s*=\s*false\b",
        r"\bproduction_report\s*=\s*false\b",
        r"\bmacro_axes\b",
        r"\bconfidence_decomposition\b",
        r"\bdeterministic_regime_shadow\b",
        r"\bregime[- ]schaduw\b",
    ],
}

PREDICTIVE_PATTERNS = {
    "en": [
        r"\bwill\b",
        r"\bshall\b",
        r"\bguarantee(?:d|s)?\b",
        r"\bcertain(?:ly)?\b",
        r"\binevitable\b",
        r"\bsure to\b",
        r"\bforecast(?:s|ed|ing)?\b",
        r"\bpredict(?:s|ed|ing|ion)?\b",
        r"\bexpected to (?:rise|fall|rally|drop|outperform|underperform)\b",
    ],
    "nl": [
        r"\bzal\b",
        r"\bzullen\b",
        r"\bgegarandeerd\b",
        r"\bzeker(?:heid)?\b",
        r"\bonvermijdelijk\b",
        r"\bvoorspel(?:t|len|ling|d)\b",
        r"\bgaat (?:stijgen|dalen|rallyen|zakken)\b",
    ],
}

MACRO_CLAIM_PATTERNS = {
    "en": [
        r"\bmacro\b",
        r"\binflation\b",
        r"\bgrowth\b",
        r"\brates?\b",
        r"\byields?\b",
        r"\bcentral bank\b",
        r"\bECB\b",
        r"\bFed\b",
        r"\bPMI\b",
        r"\bemployment\b",
        r"\benergy prices?\b",
        r"\bgeopolitical\b",
        r"\bdollar\b",
        r"\beuro\b",
    ],
    "nl": [
        r"\bmacro\b",
        r"\binflatie\b",
        r"\bgroei\b",
        r"\brente\b",
        r"\brentes\b",
        r"\bkapitaalmarktrente\b",
        r"\bcentrale bank\b",
        r"\bECB\b",
        r"\bFed\b",
        r"\bPMI\b",
        r"\barbeidsmarkt\b",
        r"\benergieprijzen\b",
        r"\bgeopolitiek\b",
        r"\bdollar\b",
        r"\beuro\b",
    ],
}

DUTCH_ENGLISH_LEAKAGE_PATTERNS = [
    r"\bcurrent regime\b",
    r"\brisk tone\b",
    r"\bportfolio action\b",
    r"\bmacro backdrop\b",
    r"\bno buy advice\b",
    r"\bfunding authority\b",
    r"\bclient wording\b",
    r"\bshadow candidate\b",
    r"\binternal label\b",
    r"\bgrowth pressure\b",
    r"\brate pressure\b",
]

CITATION_PATTERN = re.compile(r"\[M\d+\]")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _strings_from(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings_from(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings_from(child)


def _find_blocked_keys(value: Any, *, path: str = "$", found: list[str] | None = None) -> list[str]:
    if found is None:
        found = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in BLOCKED_KEYS:
                found.append(child_path)
            _find_blocked_keys(child, path=child_path, found=found)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _find_blocked_keys(child, path=f"{path}[{index}]", found=found)
    return found


def _compile_any(patterns: list[str]) -> re.Pattern[str]:
    return re.compile("|".join(f"(?:{pattern})" for pattern in patterns), flags=re.IGNORECASE)


def _has_any(text: str, patterns: list[str]) -> bool:
    return bool(_compile_any(patterns).search(text))


def _citation_ids(citations: Any) -> set[str]:
    if not isinstance(citations, list):
        return set()
    ids: set[str] = set()
    for item in citations:
        if isinstance(item, dict) and _text(item.get("id")):
            ids.add(_text(item.get("id")))
        elif isinstance(item, str) and item.strip():
            ids.add(item.strip())
    return ids


def _surface_text(surface: dict[str, Any]) -> str:
    text_parts: list[str] = []
    for key in ("title", "summary", "body", "bullets"):
        if key in surface:
            text_parts.extend(_strings_from(surface[key]))
    if not text_parts:
        text_parts.extend(_strings_from(surface))
    return "\n".join(part.strip() for part in text_parts if part and part.strip())


def _used_citation_ids(text: str) -> set[str]:
    return {match.strip("[]") for match in CITATION_PATTERN.findall(text)}


def _validate_language_surface(language: str, surface: Any, errors: list[str]) -> tuple[set[str], dict[str, Any]]:
    if not isinstance(surface, dict):
        errors.append(f"{language}:surface_must_be_object")
        return set(), {}

    text = _surface_text(surface)
    if not text:
        errors.append(f"{language}:client_text_required")

    if _has_any(text, PREDICTIVE_PATTERNS[language]):
        errors.append(f"{language}:predictive_wording_detected")

    if _has_any(text, INTERNAL_LABEL_PATTERNS[language]):
        errors.append(f"{language}:shadow_or_internal_label_leakage")

    if language == "nl" and _has_any(text, DUTCH_ENGLISH_LEAKAGE_PATTERNS):
        errors.append("nl:english_leakage_detected")

    citation_ids = _citation_ids(surface.get("citations"))
    used_ids = _used_citation_ids(text)
    has_macro_claim = _has_any(text, MACRO_CLAIM_PATTERNS[language])
    if has_macro_claim and not used_ids:
        errors.append(f"{language}:uncited_macro_claim")
    if has_macro_claim and not citation_ids:
        errors.append(f"{language}:citations_required_for_macro_claims")
    missing_ids = used_ids - citation_ids
    if missing_ids:
        errors.append(f"{language}:citation_markers_without_citation_ids:{','.join(sorted(missing_ids))}")

    meaning_claims = surface.get("meaning_claims")
    if not isinstance(meaning_claims, dict):
        errors.append(f"{language}:meaning_claims_required")
        meaning_claims = {}

    return used_ids, meaning_claims


def validate(path: Path) -> None:
    payload = _load_json(path)
    errors: list[str] = []

    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_must_be_macro_narrative_client_surface_v1")
    if payload.get("artifact_type") != "macro_narrative_client_surface":
        errors.append("artifact_type_must_be_macro_narrative_client_surface")

    blocked_key_paths = _find_blocked_keys(payload)
    if blocked_key_paths:
        errors.append("blocked_internal_keys_present:" + ",".join(blocked_key_paths))

    surfaces = payload.get("client_surface")
    if not isinstance(surfaces, dict):
        errors.append("client_surface_must_be_object")
        surfaces = {}

    used_citations: dict[str, set[str]] = {}
    meaning_by_language: dict[str, dict[str, Any]] = {}
    for language in REQUIRED_LANGUAGE_KEYS:
        used_ids, meaning_claims = _validate_language_surface(language, surfaces.get(language), errors)
        used_citations[language] = used_ids
        meaning_by_language[language] = meaning_claims

    if used_citations.get("en") != used_citations.get("nl"):
        errors.append("citation_parity_mismatch")

    expected_meaning = payload.get("meaning_contract")
    if not isinstance(expected_meaning, dict):
        errors.append("meaning_contract_required")
        expected_meaning = {}

    parity_keys = [
        "macro_regime",
        "risk_tone",
        "portfolio_action",
        "funding_authority",
        "confidence_language",
    ]
    for language in REQUIRED_LANGUAGE_KEYS:
        language_meaning = meaning_by_language.get(language, {})
        for key in parity_keys:
            if expected_meaning.get(key) != language_meaning.get(key):
                errors.append(f"{language}:meaning_contract_mismatch:{key}")

    if meaning_by_language.get("en") and meaning_by_language.get("nl"):
        for key in parity_keys:
            if meaning_by_language["en"].get(key) != meaning_by_language["nl"].get(key):
                errors.append(f"meaning_drift_between_en_nl:{key}")

    if errors:
        raise RuntimeError("MACRO_NARRATIVE_CLIENT_SURFACE_FAILED: " + "; ".join(errors))

    print(f"MACRO_NARRATIVE_CLIENT_SURFACE_OK | artifact={path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    validate(args.artifact)


if __name__ == "__main__":
    main()
