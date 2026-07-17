#!/usr/bin/env python3
"""Validate the deterministic-regime supplementary client surface.

This validator preserves the no-authority contract. It checks a narrow, client-safe
comparison surface and does not promote deterministic macro/regime authority.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tools.validate_etf_macro_thesis_surface_leakage import scan_text
from tools.validate_macro_compliance import validate_text

DEFAULT_SURFACE = Path("fixtures/deterministic_regime_client_surface/safe_surface_fixture.json")
REQUIRED_FALSE_FIELDS = [
    "client_facing_authority",
    "production_report_narrative_authority",
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "portfolio_mutation",
]
REQUIRED_FIELDS = [
    "schema_version",
    "surface_status",
    "surface_mode",
    "source_evidence_path",
    "source_comparison_path",
    "regime_label_en",
    "regime_label_nl",
    "confidence_band_en",
    "confidence_band_nl",
    "comparison_status_en",
    "comparison_status_nl",
    "short_explanation_en",
    "short_explanation_nl",
    "discipline_note_en",
    "discipline_note_nl",
    "authority_disclaimer_en",
    "authority_disclaimer_nl",
    "prohibited_source_fields_confirmed_absent",
    "safe_surface_en",
    "safe_surface_nl",
]
BLOCKED_TEXT_PATTERNS: tuple[tuple[str, str], ...] = (
    ("raw_shadow_payload", r"\bdeterministic_regime_shadow\b"),
    ("shadow_engine", r"\bshadow[- ]engine\b"),
    ("review_only", r"\breview-only\b|\balleen ter review\b"),
    ("legacy_regime", r"\blegacy regime read\b"),
    ("raw_macro_axes", r"\bmacro_axes\b"),
    ("raw_macro_axis_scores", r"\bmacro_axis_scores\b"),
    ("raw_macro_evidence", r"\bmacro_evidence\b"),
    ("raw_confidence_decomposition", r"\bconfidence_decomposition\b"),
    ("raw_conflict_score", r"\b(?:macro_)?conflict_score\b"),
    ("authority_field", r"\b(?:client_facing_authority|production_report_narrative_authority|portfolio_action_authority|lane_scoring_authority|fundability_authority|portfolio_mutation)\b"),
    ("workflow_metadata", r"\b(?:workflow_run_id|workflow_run_number|run_id|commit_sha)\b"),
    ("fixture_name", r"\bfixture(?:s)?\b"),
    ("source_path", r"\b(?:output/macro|fixtures/|\.json)\b"),
    ("numeric_confidence", r"\bconfidence\s+(?:is|=|:)?\s*\d+(?:\.\d+)?\s*%?"),
)
REQUIRED_EN_PHRASES = ["supplementary regime cross-check", "does not change portfolio actions", "pricing"]
REQUIRED_NL_PHRASES = ["aanvullende regimecontrole", "verandert de portefeuilleacties niet", "prijsbasis"]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Surface fixture not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object in {path}")
    return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    _require(isinstance(value, str) and value.strip(), f"{key} must be a non-empty string")
    return str(value).strip()


def _validate_payload_contract(payload: dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        _require(field in payload, f"missing required DTO field: {field}")
    _require(payload.get("schema_version") == "1.0", "schema_version must be 1.0")
    _require(payload.get("prohibited_source_fields_confirmed_absent") is True, "prohibited_source_fields_confirmed_absent must be true")
    for field in REQUIRED_FALSE_FIELDS:
        _require(field in payload, f"missing authority field: {field}")
        _require(payload.get(field) is False, f"{field} must be false")
    for path_field in ["source_evidence_path", "source_comparison_path"]:
        value = _text(payload, path_field)
        _require(value.startswith("output/macro/validation/"), f"{path_field} must point to macro validation evidence")


def _validate_surface_text(name: str, text: str, required_phrases: list[str]) -> None:
    lower = text.lower()
    for phrase in required_phrases:
        _require(phrase.lower() in lower, f"{name} missing required phrase: {phrase}")
    for code, pattern in BLOCKED_TEXT_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raise RuntimeError(f"{name} leaked blocked term {code}: {match.group(0)}")
    compliance = validate_text(text)
    if compliance:
        first = compliance[0]
        raise RuntimeError(f"{name} failed macro compliance: {first.code} line={first.line} {first.excerpt}")
    leakage = scan_text(text, Path(name))
    if leakage:
        first = leakage[0]
        raise RuntimeError(f"{name} failed surface leakage scan: {first.code} line={first.line} {first.excerpt}")


def validate_surface_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _validate_payload_contract(payload)
    en = _text(payload, "safe_surface_en")
    nl = _text(payload, "safe_surface_nl")
    _validate_surface_text("deterministic_regime_surface_en", en, REQUIRED_EN_PHRASES)
    _validate_surface_text("deterministic_regime_surface_nl", nl, REQUIRED_NL_PHRASES)
    _require(payload["regime_label_en"] in en, "English surface must include sanitized regime_label_en")
    _require(payload["regime_label_nl"] in nl, "Dutch surface must include sanitized regime_label_nl")
    _require(payload["confidence_band_en"] in en, "English surface must include confidence_band_en")
    _require(payload["confidence_band_nl"] in nl, "Dutch surface must include confidence_band_nl")
    return {
        "status": "passed",
        "en_chars": len(en),
        "nl_chars": len(nl),
        "regime_label_en": payload["regime_label_en"],
        "regime_label_nl": payload["regime_label_nl"],
    }


def run_self_test() -> None:
    safe = _load_json(DEFAULT_SURFACE)
    validate_surface_payload(safe)
    bad_cases: dict[str, dict[str, Any]] = {}
    bad = dict(safe)
    bad["safe_surface_en"] += " raw macro_axes should fail."
    bad_cases["raw_macro_axes"] = bad
    bad = dict(safe)
    bad["portfolio_action_authority"] = True
    bad_cases["authority_true"] = bad
    bad = dict(safe)
    bad["safe_surface_en"] = "Supplementary regime cross-check: confidence 82% and output/macro/latest.json are visible."
    bad_cases["numeric_and_path"] = bad
    bad = dict(safe)
    bad["safe_surface_en"] += " The shadow engine remains visible."
    bad_cases["shadow_engine"] = bad
    for name, payload in bad_cases.items():
        try:
            validate_surface_payload(payload)
        except RuntimeError:
            continue
        raise RuntimeError(f"self-test unsafe case did not fail: {name}")
    print("DETERMINISTIC_REGIME_CLIENT_SURFACE_SELF_TEST_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", type=Path, default=DEFAULT_SURFACE)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
    result = validate_surface_payload(_load_json(args.surface))
    print(
        "DETERMINISTIC_REGIME_CLIENT_SURFACE_OK | "
        f"surface={args.surface} | regime_en={result['regime_label_en']} | "
        f"regime_nl={result['regime_label_nl']} | en_chars={result['en_chars']} | nl_chars={result['nl_chars']}"
    )


if __name__ == "__main__":
    main()
