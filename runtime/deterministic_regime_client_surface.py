from __future__ import annotations

from typing import Any


REGIME_LABEL_NL = {
    "Risk-on growth": "Risk-on groei",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "Defensive / policy stress": "Defensief / beleidsstress",
    "Rate-hike repricing": "Renteherprijzing",
    "Policy transition / mixed regime": "Beleidstransitie / gemengd regime",
}

FALSE_AUTHORITY = {
    "client_facing_authority": False,
    "production_report_narrative_authority": False,
    "portfolio_action_authority": False,
    "lane_scoring_authority": False,
    "fundability_authority": False,
    "portfolio_mutation": False,
}


def confidence_band_en(confidence: float) -> str:
    if confidence < 0.55:
        return "low"
    if confidence < 0.72:
        return "moderate"
    return "high"


def confidence_band_nl(confidence: float) -> str:
    if confidence < 0.55:
        return "laag"
    if confidence < 0.72:
        return "gemiddeld"
    return "hoog"


def _candidate_from(validation_evidence: dict[str, Any], comparison_evidence: dict[str, Any] | None) -> tuple[str, float]:
    comparison = (comparison_evidence or {}).get("comparison") or {}
    if comparison.get("shadow_candidate_regime"):
        return str(comparison["shadow_candidate_regime"]), float(comparison.get("shadow_candidate_confidence", 0.0))
    shadow = validation_evidence.get("shadow_summary") or {}
    return str(shadow.get("candidate_regime") or "Unknown regime"), float(shadow.get("candidate_confidence", 0.0))


def _alignment_from(comparison_evidence: dict[str, Any] | None) -> tuple[str, str, bool, bool]:
    comparison = (comparison_evidence or {}).get("comparison") or {}
    label_differs = bool(comparison.get("regime_label_differs", False))
    confidence_differs = bool(comparison.get("confidence_differs", False))
    if label_differs:
        return (
            "differs from the primary regime view and therefore remains a supplementary cross-check",
            "wijkt af van het primaire regimebeeld en blijft daarom een aanvullende controle",
            label_differs,
            confidence_differs,
        )
    return (
        "broadly aligned with the primary regime view",
        "grotendeels in lijn met het primaire regimebeeld",
        label_differs,
        confidence_differs,
    )


def _explanation_en(label_differs: bool, confidence_differs: bool) -> str:
    if label_differs:
        return "The secondary assessment differs from the primary view and should be treated as contextual evidence only."
    if confidence_differs:
        return "The regime label is aligned while the confidence assessment differs; the comparison remains contextual."
    return "The current evidence is broadly consistent across the primary and supplementary assessments."


def _explanation_nl(label_differs: bool, confidence_differs: bool) -> str:
    if label_differs:
        return "De tweede beoordeling wijkt af van het primaire beeld en geldt daarom uitsluitend als context."
    if confidence_differs:
        return "Het regimebeeld is gelijk, maar de betrouwbaarheidsinschatting verschilt; de vergelijking blijft contextueel."
    return "Het actuele bewijs is grotendeels consistent tussen de primaire en aanvullende beoordeling."


def _join_sentences(first: str, second: str) -> str:
    return f"{first.rstrip().rstrip('.')} . {second.strip()}".replace(" . ", ". ")


def render_deterministic_regime_surface_en(dto: dict[str, Any]) -> str:
    authority_sentence = _join_sentences(dto["authority_disclaimer_en"], dto["discipline_note_en"])
    return (
        "Supplementary regime cross-check: "
        f"A secondary rules-based assessment indicates {dto['regime_label_en']} and is {dto['comparison_status_en']}. "
        f"Confidence is {dto['confidence_band_en']}, reflecting consistency in the underlying evidence rather than a forecast. "
        f"{authority_sentence}"
    )


def render_deterministic_regime_surface_nl(dto: dict[str, Any]) -> str:
    authority_sentence = _join_sentences(dto["authority_disclaimer_nl"], dto["discipline_note_nl"])
    return (
        "Aanvullende regimecontrole: "
        f"Een tweede regelgebaseerde beoordeling wijst op {dto['regime_label_nl']} en is {dto['comparison_status_nl']}. "
        f"De betrouwbaarheid is {dto['confidence_band_nl']} en weerspiegelt consistentie in het onderliggende bewijs, niet een voorspelling. "
        f"{authority_sentence}"
    )


def build_deterministic_regime_client_surface(
    *,
    validation_evidence: dict[str, Any],
    comparison_evidence: dict[str, Any] | None,
    source_evidence_path: str,
    source_comparison_path: str,
) -> dict[str, Any]:
    """Build the narrow client-safe deterministic-regime DTO.

    Raw model fields, evidence arrays, workflow metadata and authority-bearing
    fields remain excluded from the rendered surface. The false authority fields
    stay explicit so the supplementary comparison cannot become action authority.
    """
    regime_en, confidence = _candidate_from(validation_evidence, comparison_evidence)
    regime_nl = REGIME_LABEL_NL.get(regime_en, regime_en)
    comparison_en, comparison_nl, label_differs, confidence_differs = _alignment_from(comparison_evidence)

    dto: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "deterministic_regime_client_surface",
        "surface_status": "helper_generated",
        "surface_mode": "helper_only",
        "source_evidence_path": source_evidence_path,
        "source_comparison_path": source_comparison_path,
        "regime_label_en": regime_en,
        "regime_label_nl": regime_nl,
        "confidence_band_en": confidence_band_en(confidence),
        "confidence_band_nl": confidence_band_nl(confidence),
        "comparison_status_en": comparison_en,
        "comparison_status_nl": comparison_nl,
        "short_explanation_en": _explanation_en(label_differs, confidence_differs),
        "short_explanation_nl": _explanation_nl(label_differs, confidence_differs),
        "discipline_note_en": "Pricing, relative strength and position discipline remain decisive.",
        "discipline_note_nl": "Prijsbasis, relatieve sterkte en positiediscipline blijven leidend.",
        "authority_disclaimer_en": "This supplementary check does not change portfolio actions.",
        "authority_disclaimer_nl": "Deze aanvullende controle verandert de portefeuilleacties niet.",
        "prohibited_source_fields_confirmed_absent": True,
        **FALSE_AUTHORITY,
    }
    dto["safe_surface_en"] = render_deterministic_regime_surface_en(dto)
    dto["safe_surface_nl"] = render_deterministic_regime_surface_nl(dto)
    return dto
