from __future__ import annotations

from typing import Any


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _conf(key: str, config: dict[str, Any], default: float) -> float:
    return _num((config.get("confidence") or {}).get(key), default)


def compute_shadow_confidence(
    *,
    candidate_regime: str,
    axes: dict[str, str],
    axis_scores: dict[str, float],
    macro_data_audit_summary: dict[str, Any] | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Return a deterministic, descriptive confidence decomposition.

    This intentionally does not predict returns or central-bank decisions. It
    measures internal agreement among observable axes so the later regime engine
    can be compared against the legacy regime path in shadow mode.
    """

    base = _conf("base", config, 0.45)
    axis_weight = _conf("axis_alignment_weight", config, 0.28)
    strength_weight = _conf("signal_strength_weight", config, 0.17)
    conflict_weight = _conf("conflict_penalty_weight", config, 0.12)
    macro_bonus = _conf("macro_audit_bonus", config, 0.03)
    minimum = _conf("min", config, 0.35)
    maximum = _conf("max", config, 0.82)

    risk_support = 0
    defensive_support = 0
    mixed_count = 0

    if axes.get("equity") == "risk_on":
        risk_support += 1
    elif axes.get("equity") == "risk_off":
        defensive_support += 1
    else:
        mixed_count += 1

    if axes.get("semiconductor_leadership") == "strong":
        risk_support += 1
    elif axes.get("semiconductor_leadership") == "weak":
        defensive_support += 1
    else:
        mixed_count += 1

    if axes.get("breadth") == "broad":
        risk_support += 1
    elif axes.get("breadth") == "weak":
        defensive_support += 1
    else:
        mixed_count += 1

    if axes.get("duration") == "supportive":
        risk_support += 1
    elif axes.get("duration") == "stress":
        defensive_support += 1
    else:
        mixed_count += 1

    if axes.get("hedge") == "gold_bid":
        defensive_support += 1
    elif axes.get("hedge") == "gold_weak":
        risk_support += 1
    else:
        mixed_count += 1

    support_total = risk_support + defensive_support + mixed_count
    dominant_support = max(risk_support, defensive_support)
    axis_alignment = dominant_support / support_total if support_total else 0.0

    strength_values = [min(abs(_num(v)) / 10.0, 1.0) for v in axis_scores.values()]
    signal_strength = sum(strength_values) / len(strength_values) if strength_values else 0.0

    conflict_pairs = 0
    if axes.get("equity") == "risk_on" and axes.get("breadth") == "weak":
        conflict_pairs += 1
    if axes.get("equity") == "risk_on" and axes.get("duration") == "stress":
        conflict_pairs += 1
    if axes.get("equity") == "risk_off" and axes.get("hedge") == "gold_weak":
        conflict_pairs += 1
    if axes.get("semiconductor_leadership") == "strong" and axes.get("breadth") in {"narrow", "weak"}:
        conflict_pairs += 0.5
    conflict_score = min(float(conflict_pairs) / 3.0, 1.0)

    macro_audit_present = bool((macro_data_audit_summary or {}).get("present"))
    raw = base + axis_weight * axis_alignment + strength_weight * signal_strength - conflict_weight * conflict_score
    if macro_audit_present:
        raw += macro_bonus
    confidence = round(max(minimum, min(maximum, raw)), 2)

    notes = [
        "Confidence measures cross-axis agreement, not forecast accuracy.",
        f"Dominant support axes: risk={risk_support}, defensive={defensive_support}, mixed={mixed_count}.",
        f"Candidate regime: {candidate_regime}.",
    ]
    if conflict_score > 0:
        notes.append("Confidence is reduced for mixed or internally conflicting cross-asset evidence.")
    if not macro_audit_present:
        notes.append("No macro audit authority is used yet; this remains relative-strength/proxy shadow evidence.")

    return {
        "method": "deterministic_axis_agreement_v1_shadow",
        "confidence": confidence,
        "shadow_only": True,
        "client_facing_authority": False,
        "decision_impact": "none_shadow_comparison_only",
        "components": {
            "base": base,
            "axis_alignment": round(axis_alignment, 4),
            "signal_strength": round(signal_strength, 4),
            "conflict_score": round(conflict_score, 4),
            "macro_audit_present": macro_audit_present,
            "raw_confidence": round(raw, 4),
            "min": minimum,
            "max": maximum,
        },
        "notes": notes,
    }
