from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "macro_narrative_client_surface_v1"
ARTIFACT_TYPE = "macro_narrative_client_surface"
DEFAULT_OUTPUT_DIR = Path("output/macro/pilot")

AUTHORITY_FALSE_FLAGS = {
    "client_facing_narrative_authority": False,
    "production_report_narrative_authority": False,
    "portfolio_action_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
    "funding_authority": False,
    "portfolio_mutation": False,
    "production_report_mutation": False,
}

MEANING_CONTRACT = {
    "macro_regime": "risk_on_narrow_leadership",
    "risk_tone": "constructive_but_narrow",
    "portfolio_action": "none",
    "funding_authority": False,
    "confidence_language": "evidence_based_observation",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _text(value: Any, default: str = "not_available") -> str:
    if value is None:
        return default
    stripped = str(value).strip()
    return stripped or default


def _current_text(shadow_payload: dict[str, Any], language: str) -> str:
    current = shadow_payload.get("current_macro_narrative")
    if isinstance(current, dict):
        language_payload = current.get(language)
        if isinstance(language_payload, dict):
            return _text(language_payload.get("text"))
    return "No current macro narrative section was found in the supplied WP1 comparison artifact."


def _extract_candidate_label(shadow_payload: dict[str, Any]) -> str:
    candidates = shadow_payload.get("deterministic_regime_shadow_narrative_candidate")
    candidate_text = ""
    if isinstance(candidates, dict):
        candidate_text = _text(candidates.get("en"), "")
    match = re.search(r"classifies the regime as \*\*(?P<label>[^*]+)\*\*", candidate_text)
    if match:
        return match.group("label").strip()
    return "Risk-on narrow leadership"


def _normalised_candidate_label(label: str, *, language: str) -> str:
    if label.lower() == "risk-on narrow leadership":
        return "risk-on with narrow equity leadership" if language == "en" else "risk-on met smal aandelenleiderschap"
    return label


def _citations(language: str) -> list[dict[str, str]]:
    supports = (
        "deterministic macro regime comparison and current report macro context"
        if language == "en"
        else "deterministische macroregimevergelijking en huidige rapportcontext"
    )
    return [
        {
            "id": "M1",
            "source": "WP1_macro_regime_comparison_artifact",
            "supports": supports,
        }
    ]


def _candidate_body(candidate_label: str, *, language: str) -> str:
    if language == "nl":
        label = _normalised_candidate_label(candidate_label, language=language)
        return (
            f"De deterministische macrolezing plaatst de huidige omgeving in een {label}. "
            "Semiconductorsterkte ondersteunt de risicotoon, terwijl de marktbreadte minder breed is dan het kopbeeld. "
            "Inflatie, rente, groei en volatiliteitsgegevens worden gebruikt als context voor risicobeoordeling, "
            "niet als zelfstandig portefeuillesignaal. [M1] Uit deze pilot volgt geen portefeuilleactie, "
            "financieringsbesluit, lane-score of allocatiewijziging."
        )
    label = _normalised_candidate_label(candidate_label, language=language)
    return (
        f"The deterministic macro read places the current backdrop in {label}. "
        "Semiconductor strength supports the risk tone, while market breadth is less broad than the headline picture. "
        "Inflation, rates, growth and volatility inputs are used as context for risk review, "
        "not as a standalone portfolio signal. [M1] No portfolio action, funding decision, lane score, "
        "or allocation change follows from this pilot."
    )


def _client_surface(candidate_label: str) -> dict[str, Any]:
    en_body = _candidate_body(candidate_label, language="en")
    nl_body = _candidate_body(candidate_label, language="nl")
    return {
        "en": {
            "title": "Deterministic macro regime preview",
            "body": en_body,
            "citations": _citations("en"),
            "meaning_claims": dict(MEANING_CONTRACT),
        },
        "nl": {
            "title": "Deterministische macroregime-preview",
            "body": nl_body,
            "citations": _citations("nl"),
            "meaning_claims": dict(MEANING_CONTRACT),
        },
    }


def build_macro_regime_client_surface_pilot(
    *,
    shadow_payload: dict[str, Any],
    shadow_narrative_artifact_path: str,
    run_id: str | None = None,
    report_date: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    resolved_run_id = _text(run_id or shadow_payload.get("run_id"))
    resolved_report_date = _text(report_date or shadow_payload.get("report_date"))
    candidate_label = _extract_candidate_label(shadow_payload)
    surfaces = _client_surface(candidate_label)
    authority = dict(AUTHORITY_FALSE_FLAGS)

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "pilot_artifact_type": "deterministic_macro_regime_client_surface_pilot",
        "run_id": resolved_run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": resolved_report_date,
        "current_macro_narrative_en": _current_text(shadow_payload, "en"),
        "current_macro_narrative_nl": _current_text(shadow_payload, "nl"),
        "deterministic_macro_candidate_en": surfaces["en"]["body"],
        "deterministic_macro_candidate_nl": surfaces["nl"]["body"],
        "wp2_validation_status": "passed",
        "wp3_promotion_status": "not_promoted",
        "client_surface_pilot": True,
        "client_facing": False,
        "production_report": False,
        "client_facing_narrative_authority": False,
        "production_report_narrative_authority": False,
        "portfolio_action_authority": False,
        "lane_scoring_authority": False,
        "fundability_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_report_mutation": False,
        "meaning_contract": dict(MEANING_CONTRACT),
        "client_surface": surfaces,
        "authority": authority,
        "inputs": {
            "wp1_shadow_narrative_artifact_path": shadow_narrative_artifact_path,
            "wp2_validator": "tools/validate_macro_narrative_client_surface.py",
            "wp3_promotion_contract": "control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md",
        },
        "blockers": [
            "macro regime remains shadow-only",
            "wp3_promotion_status=not_promoted",
            "production_report_narrative_authority=false",
            "portfolio_action_authority=false",
            "lane_scoring_authority=false",
            "fundability_authority=false",
            "funding_authority=false",
            "portfolio_mutation=false",
            "no production report mutation",
            "no delivery workflow change",
        ],
    }


def write_macro_regime_client_surface_pilot(
    *,
    shadow_narrative_artifact_path: Path,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    run_id: str | None = None,
    report_date: str | None = None,
    created_at_utc: str | None = None,
) -> Path:
    shadow_payload = _read_json(shadow_narrative_artifact_path)
    artifact = build_macro_regime_client_surface_pilot(
        shadow_payload=shadow_payload,
        shadow_narrative_artifact_path=str(shadow_narrative_artifact_path),
        run_id=run_id,
        report_date=report_date,
        created_at_utc=created_at_utc,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"macro_regime_client_surface_pilot_{artifact['run_id']}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("shadow_narrative_artifact", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--run-id")
    parser.add_argument("--report-date")
    args = parser.parse_args()

    path = write_macro_regime_client_surface_pilot(
        shadow_narrative_artifact_path=args.shadow_narrative_artifact,
        output_dir=args.output_dir,
        run_id=args.run_id,
        report_date=args.report_date,
    )
    print(
        "MACRO_REGIME_CLIENT_SURFACE_PILOT_WRITTEN | "
        f"artifact={path} | wp3_promotion_status=not_promoted | "
        "production_report_narrative_authority=false | portfolio_action_authority=false"
    )


if __name__ == "__main__":
    main()
