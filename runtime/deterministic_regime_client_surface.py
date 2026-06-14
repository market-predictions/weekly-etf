from __future__ import annotations

from typing import Any


REGIME_LABEL_NL = {
    "Risk-on growth": "Risk-on groei",
    "Risk-on narrow leadership": "Risk-on met smalle leiderschap",
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
    return "high but review-only"


def confidence_band_nl(confidence: float) -> str:
    if confidence < 0.55:
        return "laag"
    if confidence < 0.72:
        return "gemiddeld"
    return "hoog maar alleen ter review"


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
            "not aligned with the legacy regime read and therefore review-only",
            "niet in lijn met de bestaande regime-inschatting en daarom alleen ter review",
            label_differs,
            confidence_differs,
        )
    return (
        "broadly aligned with the legacy regime read",
        "grotendeels in lijn met de bestaande regime-inschatting",
        label_differs,
        confidence_differs,
    )


def _explanation_en(label_differs: bool, confidence_differs: bool) -> str:
    if label_differs:
        return "The regime label differs from the legacy read, so this remains an internal review signal."
    if confidence_differs:
        return "The regime label is aligned, while confidence differs; this remains an internal review signal."
    return "Current evidence is broadly consistent, but this remains an internal review signal."


def _explanation_nl(label_differs: bool, confidence_differs: bool) -> str:
    if label_differs:
        return "Het regime-label wijkt af van de bestaande inschatting; dit blijft daarom een intern reviewsignaal."
    if confidence_differs:
        return "Het regime-label is in lijn, terwijl de betrouwbaarheid verschilt; dit blijft een intern reviewsignaal."
    return "Het huidige bewijs is grotendeels samenhangend, maar dit blijft een intern reviewsignaal."


def _join_sentences(first: str, second: str) -> str:
    return f"{first.rstrip().rstrip('.')} . {second.strip()}".replace(" . ", ". ")


def render_deterministic_regime_surface_en(dto: dict[str, Any]) -> str:
    authority_sentence = _join_sentences(dto["authority_disclaimer_en"], dto["discipline_note_en"])
    return (
        "Deterministic regime read — review-only: "
        f"The shadow engine currently classifies the backdrop as {dto['regime_label_en']}, "
        f"{dto['comparison_status_en']}. "
        f"Confidence is {dto['confidence_band_en']}, reflecting evidence consistency rather than a forecast. "
        f"{authority_sentence}"
    )


def render_deterministic_regime_surface_nl(dto: dict[str, Any]) -> str:
    authority_sentence = _join_sentences(dto["authority_disclaimer_nl"], dto["discipline_note_nl"])
    return (
        "Deterministische regime-inschatting — alleen ter review: "
        f"De shadow-engine classificeert de marktomgeving momenteel als {dto['regime_label_nl']}, "
        f"{dto['comparison_status_nl']}. "
        f"De betrouwbaarheid is {dto['confidence_band_nl']} en beschrijft samenhang in het bewijs, geen voorspelling. "
        f"{authority_sentence}"
    )


def build_deterministic_regime_client_surface(
    *,
    validation_evidence: dict[str, Any],
    comparison_evidence: dict[str, Any] | None,
    source_evidence_path: str,
    source_comparison_path: str,
) -> dict[str, Any]:
    """Build the narrow WP21/WP22 safe-surface DTO.

    This helper intentionally drops raw shadow fields such as axes, scores,
    macro evidence, workflow metadata and confidence decompositions.
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
        "discipline_note_en": "The normal discipline gates remain decisive.",
        "discipline_note_nl": "De normale discipline blijft leidend.",
        "authority_disclaimer_en": "This does not authorize portfolio changes.",
        "authority_disclaimer_nl": "Dit geeft geen autoriteit voor portefeuillewijzigingen.",
        "prohibited_source_fields_confirmed_absent": True,
        **FALSE_AUTHORITY,
    }
    dto["safe_surface_en"] = render_deterministic_regime_surface_en(dto)
    dto["safe_surface_nl"] = render_deterministic_regime_surface_nl(dto)
    return dto
