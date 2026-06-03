from __future__ import annotations

from typing import Any


CONFIDENCE_DIFF_THRESHOLD = 0.05


def validate_shadow_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        raise RuntimeError("Missing deterministic_regime_shadow payload")
    if payload.get("schema_version") != "1.0":
        raise RuntimeError("deterministic_regime_shadow schema_version must be 1.0")
    if payload.get("shadow_only") is not True:
        raise RuntimeError("deterministic_regime_shadow must be shadow_only")
    if payload.get("client_facing_authority") is not False:
        raise RuntimeError("deterministic_regime_shadow must not be client-facing authority")
    if payload.get("decision_impact") != "none_shadow_comparison_only":
        raise RuntimeError("deterministic_regime_shadow must have no production decision impact")
    candidate = str(payload.get("candidate_regime") or "").strip()
    if not candidate:
        raise RuntimeError("deterministic_regime_shadow candidate_regime is required")
    confidence = float(payload.get("candidate_confidence"))
    if confidence < 0 or confidence > 1:
        raise RuntimeError("deterministic_regime_shadow candidate_confidence must be between 0 and 1")
    legacy_regime = str(payload.get("legacy_regime") or "").strip()
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
    for axis in ["equity", "semiconductor_leadership", "breadth", "duration", "hedge", "commodities"]:
        if axis not in axes:
            raise RuntimeError(f"deterministic_regime_shadow missing axis: {axis}")
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
