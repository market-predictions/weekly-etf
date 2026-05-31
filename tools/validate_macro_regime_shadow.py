from __future__ import annotations

from typing import Any


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
    axes = payload.get("axes") or {}
    for axis in ["equity", "semiconductor_leadership", "breadth", "duration", "hedge", "commodities"]:
        if axis not in axes:
            raise RuntimeError(f"deterministic_regime_shadow missing axis: {axis}")
    return {
        "candidate_regime": candidate,
        "candidate_confidence": confidence,
        "legacy_regime": payload.get("legacy_regime"),
        "differs_from_legacy": bool(payload.get("differs_from_legacy")),
    }
