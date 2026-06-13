from __future__ import annotations

from typing import Any


CONFIDENCE_DIFF_THRESHOLD = 0.05
EXPECTED_DECISION_IMPACT = "none_shadow_comparison_only"
REQUIRED_MARKET_AXES = ["equity", "semiconductor_leadership", "breadth", "duration", "hedge", "commodities"]
REQUIRED_FALSE_AUTHORITY_FIELDS = [
    "client_facing_authority",
    "production_report_narrative_authority",
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
    "portfolio_mutation",
    "historical_output_mutation",
]


def _require_false(payload: dict[str, Any], field: str) -> None:
    if field not in payload:
        raise RuntimeError(f"deterministic_regime_shadow missing authority field: {field}")
    if payload.get(field) is not False:
        raise RuntimeError(f"deterministic_regime_shadow {field} must be false")


def validate_shadow_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        raise RuntimeError("Missing deterministic_regime_shadow payload")
    if payload.get("schema_version") != "1.0":
        raise RuntimeError("deterministic_regime_shadow schema_version must be 1.0")
    if payload.get("method") != "deterministic_axis_classifier_v1_shadow":
        raise RuntimeError("deterministic_regime_shadow method must be deterministic_axis_classifier_v1_shadow")
    if payload.get("shadow_only") is not True:
        raise RuntimeError("deterministic_regime_shadow must be shadow_only")
    for field in REQUIRED_FALSE_AUTHORITY_FIELDS:
        _require_false(payload, field)
    if payload.get("decision_impact") != EXPECTED_DECISION_IMPACT:
        raise RuntimeError("deterministic_regime_shadow must have no production decision impact")
    candidate = str(payload.get("candidate_regime") or "").strip()
    if not candidate:
        raise RuntimeError("deterministic_regime_shadow candidate_regime is required")
    confidence = float(payload.get("candidate_confidence"))
    if confidence < 0 or confidence > 1:
        raise RuntimeError("deterministic_regime_shadow candidate_confidence must be between 0 and 1")
    legacy_regime = str(payload.get("legacy_regime") or "").strip()
    if not legacy_regime:
        raise RuntimeError("deterministic_regime_shadow legacy_regime is required")
    legacy_confidence = float(payload.get("legacy_confidence"))
    confidence_delta = float(payload.get("confidence_delta"))
    expected_delta = round(confidence - legacy_confidence, 4)
    if confidence_delta != expected_delta:
        raise RuntimeError(f"deterministic_regime_shadow confidence_delta expected {expected_delta}, got {confidence_delta}")
    expected_label_differs = candidate != legacy_regime
    if payload.get("regime_label_differs") is not expected_label_differs:
        raise RuntimeError("deterministic_regime_shadow regime_label_differs is inconsistent with labels")
    threshold = float(payload.get("confidence_diff_threshold", CONFIDENCE_DIFF_THRESHOLD))
    if threshold != CONFIDENCE_DIFF_THRESHOLD:
        raise RuntimeError(f"deterministic_regime_shadow confidence_diff_threshold must be {CONFIDENCE_DIFF_THRESHOLD}")
    expected_confidence_differs = abs(confidence_delta) >= threshold
    if payload.get("confidence_differs") is not expected_confidence_differs:
        raise RuntimeError("deterministic_regime_shadow confidence_differs is inconsistent with confidence_delta")
    expected_differs = expected_label_differs or expected_confidence_differs
    if payload.get("differs_from_legacy") is not expected_differs:
        raise RuntimeError("deterministic_regime_shadow differs_from_legacy must equal regime_label_differs OR confidence_differs")
    axes = payload.get("axes") or {}
    if not isinstance(axes, dict):
        raise RuntimeError("deterministic_regime_shadow axes must be an object")
    for axis in REQUIRED_MARKET_AXES:
        if axis not in axes:
            raise RuntimeError(f"deterministic_regime_shadow missing axis: {axis}")
    confidence_decomposition = payload.get("confidence_decomposition") or {}
    if not isinstance(confidence_decomposition, dict):
        raise RuntimeError("deterministic_regime_shadow confidence_decomposition must be an object")
    components = confidence_decomposition.get("components") or {}
    if not isinstance(components, dict):
        raise RuntimeError("deterministic_regime_shadow confidence components must be an object")
    macro_axes = payload.get("macro_axes") or {}
    macro_scores = payload.get("macro_axis_scores") or {}
    macro_evidence = payload.get("macro_evidence") or {}
    macro_audit_present = components.get("macro_audit_present") is True
    if macro_axes or macro_scores:
        if not macro_audit_present:
            raise RuntimeError("deterministic_regime_shadow macro axes require macro_audit_present=true")
        if not isinstance(macro_evidence, dict) or not macro_evidence.get("observation_count"):
            raise RuntimeError("deterministic_regime_shadow macro evidence is required when macro axes are present")
    return {
        "candidate_regime": candidate,
        "candidate_confidence": confidence,
        "legacy_regime": legacy_regime,
        "legacy_confidence": legacy_confidence,
        "differs_from_legacy": bool(payload.get("differs_from_legacy")),
        "regime_label_differs": bool(payload.get("regime_label_differs")),
        "confidence_differs": bool(payload.get("confidence_differs")),
        "confidence_delta": confidence_delta,
    }
