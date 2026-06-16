#!/usr/bin/env python3
"""Validate the macro/thesis bilingual alias source.

WP29 is preparation-only. This validator proves the alias source defines narrow,
sanitized English/Dutch labels for possible future client-safe surfaces without
exposing internal thesis pipeline plumbing or granting any report, scoring,
fundability, portfolio-action, delivery, or execution authority.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_ALIAS_PATH = Path("config/macro_thesis_bilingual_aliases.yml")

FORBIDDEN_RAW_TERMS = [
    "stage_1_candidate",
    "stage_2_confirmed_not_fundable",
    "stage_2_fundable_ready_shadow",
    "stage2_confirmation",
    "stage_2_confirmation",
    "thesis_candidates",
    "latest_thesis_candidates",
    "driver_catalog",
    "driver_beneficiary_map",
    "active_drivers",
    "driver_id",
    "driver_ids",
    "beneficiary_map",
    "confirmation_status",
    "stage2_status",
    "client_facing_authority",
    "fundability_authority",
    "lane_scoring_authority",
    "portfolio_action_authority",
    "report_surface_allowed",
    "shadow_only",
    "internal_only",
]

FORBIDDEN_VALUE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (reason, re.compile(pattern, re.IGNORECASE))
    for reason, pattern in [
        ("raw internal Stage-1/Stage-2/driver plumbing term", r"\b(?:" + "|".join(re.escape(term) for term in FORBIDDEN_RAW_TERMS) + r")\b"),
        ("raw Stage-1/Stage-2 label", r"\bstage[- ]?[12]\b"),
        ("recommendation language is not allowed in aliases", r"\b(recommendation|recommend|recommended|aanbeveling|aanbevelen)\b"),
        ("trade language is not allowed in aliases", r"\b(trade|trades|trading|buy|sell|koop|kopen|verkoop|verkopen|handel)\b"),
        ("fundability language is not allowed in aliases", r"\b(fundability|fundable|funded|funding|allocatiebesluit|geschikt voor allocatie)\b"),
        ("portfolio-action language is not allowed in aliases", r"\bportfolio action(?:s)?\b|\bportefeuilleactie(?:s)?\b"),
        ("authority language is not allowed in aliases", r"\b(authority|authorized|narrative authority|delivery authority|execution authority|bevoegdheid|gezag)\b"),
        ("lane-scoring language is not allowed in aliases", r"\blane[- ]?scoring\b|\bscoret?\b"),
    ]
)

LAZY_DUTCH_WORDS = {
    "evidence",
    "alignment",
    "policy",
    "risk",
    "portfolio",
    "discipline",
    "check",
    "driver",
    "candidate",
    "confirmation",
    "fundable",
}

REQUIRED_CONCEPT_FIELDS = {"en", "nl", "client_safe"}
OPTIONAL_TOP_LEVEL_FIELDS = {"version", "purpose", "concepts"}


@dataclass(frozen=True)
class AliasFinding:
    concept: str
    language: str
    value: str
    reason: str


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Alias file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_simple_alias_yaml(text)
    payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Alias file must contain a YAML mapping: {path}")
    return payload


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _parse_simple_alias_yaml(text: str) -> dict[str, Any]:
    """Small fallback parser for the deterministic WP29 alias schema.

    It supports the committed shape only: top-level scalars plus a ``concepts``
    mapping where each concept has scalar ``en``, ``nl`` and ``client_safe``
    fields. PyYAML is still preferred when available.
    """

    payload: dict[str, Any] = {}
    concepts: dict[str, dict[str, Any]] = {}
    in_concepts = False
    current_key: str | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            if line == "concepts:":
                in_concepts = True
                payload["concepts"] = concepts
                continue
            in_concepts = False
            if ":" in line:
                key, value = line.split(":", 1)
                payload[key.strip()] = _strip_quotes(value.strip())
            continue
        if in_concepts and indent == 2 and line.endswith(":"):
            current_key = line[:-1].strip()
            concepts[current_key] = {}
            continue
        if in_concepts and indent == 4 and current_key and ":" in line:
            key, value = line.split(":", 1)
            raw_value = _strip_quotes(value.strip())
            concepts[current_key][key.strip()] = raw_value.lower() == "true" if raw_value.lower() in {"true", "false"} else raw_value
    return payload


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _finding(concept: str, language: str, value: Any, reason: str) -> AliasFinding:
    return AliasFinding(concept=concept, language=language, value=str(value), reason=reason)


def _is_lazy_dutch_copy(en: str, nl: str) -> bool:
    en_norm = re.sub(r"[^a-z0-9]+", " ", en.lower()).strip()
    nl_norm = re.sub(r"[^a-z0-9]+", " ", nl.lower()).strip()
    if en_norm == nl_norm:
        return True
    nl_words = set(nl_norm.split())
    return bool(nl_words & LAZY_DUTCH_WORDS)


def _validate_alias_value(concept: str, language: str, value: str) -> list[AliasFinding]:
    findings: list[AliasFinding] = []
    for reason, pattern in FORBIDDEN_VALUE_PATTERNS:
        match = pattern.search(value)
        if match:
            findings.append(_finding(concept, language, value, f"{reason}: {match.group(0)}"))
    return findings


def validate_payload(payload: dict[str, Any]) -> None:
    findings: list[AliasFinding] = []

    unknown_top = set(payload) - OPTIONAL_TOP_LEVEL_FIELDS
    if unknown_top:
        findings.append(_finding("__schema__", "schema", sorted(unknown_top), "unknown top-level field(s)"))

    concepts = payload.get("concepts")
    if not isinstance(concepts, dict) or not concepts:
        findings.append(_finding("__schema__", "schema", concepts, "concepts mapping is required and must be non-empty"))
        _raise_if_findings(findings)
        return

    keys = list(concepts)
    if keys != sorted(keys):
        findings.append(_finding("__schema__", "schema", ",".join(keys), "concept keys must be sorted for deterministic review"))

    for concept, entry in concepts.items():
        if not isinstance(concept, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", concept):
            findings.append(_finding(str(concept), "schema", concept, "concept key must be lowercase snake_case"))
            continue
        for raw_term in FORBIDDEN_RAW_TERMS:
            if raw_term.lower() in concept.lower():
                findings.append(_finding(concept, "concept", concept, f"concept key contains forbidden raw term: {raw_term}"))
        if not isinstance(entry, dict):
            findings.append(_finding(concept, "schema", entry, "concept entry must be a mapping"))
            continue
        missing = REQUIRED_CONCEPT_FIELDS - set(entry)
        if missing:
            for field in sorted(missing):
                findings.append(_finding(concept, field, "", f"missing required field: {field}"))
        unknown = set(entry) - REQUIRED_CONCEPT_FIELDS
        if unknown:
            findings.append(_finding(concept, "schema", sorted(unknown), "unknown concept field(s)"))
        if entry.get("client_safe") is not True:
            findings.append(_finding(concept, "client_safe", entry.get("client_safe"), "client_safe must be true for every alias"))

        en = _as_text(entry.get("en")).strip()
        nl = _as_text(entry.get("nl")).strip()
        if not en:
            findings.append(_finding(concept, "en", entry.get("en"), "English alias must be a non-empty string"))
        if not nl:
            findings.append(_finding(concept, "nl", entry.get("nl"), "Dutch alias must be a non-empty string"))
        if en:
            findings.extend(_validate_alias_value(concept, "en", en))
        if nl:
            findings.extend(_validate_alias_value(concept, "nl", nl))
        if en and nl and _is_lazy_dutch_copy(en, nl):
            findings.append(_finding(concept, "nl", nl, "Dutch alias appears to be a lazy English copy rather than native terminology"))

    _raise_if_findings(findings)


def _raise_if_findings(findings: list[AliasFinding]) -> None:
    if not findings:
        return
    for finding in findings:
        print(
            "MACRO_THESIS_BILINGUAL_ALIAS_FINDING | "
            f"concept={finding.concept} | language={finding.language} | "
            f"value={finding.value!r} | reason={finding.reason}"
        )
    raise RuntimeError(f"Macro/thesis bilingual alias validation failed: findings={len(findings)}")


def validate_alias_file(path: Path = DEFAULT_ALIAS_PATH) -> None:
    validate_payload(_load_yaml(path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alias-file", type=Path, default=DEFAULT_ALIAS_PATH)
    args = parser.parse_args()

    validate_alias_file(args.alias_file)
    print(f"MACRO_THESIS_BILINGUAL_ALIASES_OK | file={args.alias_file}")


if __name__ == "__main__":
    main()
