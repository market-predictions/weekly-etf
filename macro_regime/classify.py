from __future__ import annotations

from typing import Any

from macro_regime.confidence import compute_shadow_confidence


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _metric(metrics: dict[str, Any], symbol: str) -> dict[str, Any]:
    return dict(metrics.get(symbol.upper(), {}) or {})


def _return_3m(metrics: dict[str, Any], symbol: str) -> float:
    return _num(_metric(metrics, symbol).get("return_3m_pct"), 0.0)


def _return_1m(metrics: dict[str, Any], symbol: str) -> float:
    return _num(_metric(metrics, symbol).get("return_1m_pct"), 0.0)


def _rs_3m(metrics: dict[str, Any], symbol: str) -> float:
    return _num(_metric(metrics, symbol).get("rs_vs_spy_3m_pct"), 0.0)


def _threshold(config: dict[str, Any], axis: str, key: str, default: float) -> float:
    return _num(((config.get("axes") or {}).get(axis) or {}).get(key), default)


def _axis_labels(metrics: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, str], dict[str, float], dict[str, Any]]:
    spy_3m = _return_3m(metrics, "SPY")
    smh_3m = _return_3m(metrics, "SMH")
    iwm_rs_3m = _rs_3m(metrics, "IWM")
    tlt_3m = _return_3m(metrics, "TLT")
    gld_3m = _return_3m(metrics, "GLD")
    gsg_3m = _return_3m(metrics, "GSG")

    risk_on_spy = _threshold(config, "equity", "risk_on_spy_3m_pct", 4.0)
    risk_off_spy = _threshold(config, "equity", "risk_off_spy_3m_pct", -4.0)
    smh_strong = _threshold(config, "semiconductor_leadership", "smh_return_3m_strong_pct", 8.0)
    smh_vs_spy = _threshold(config, "semiconductor_leadership", "smh_vs_spy_leadership_pct", 4.0)
    broad_iwm = _threshold(config, "breadth", "broad_iwm_rs_vs_spy_3m_pct", 1.5)
    weak_iwm = _threshold(config, "breadth", "weak_iwm_rs_vs_spy_3m_pct", -2.0)
    supportive_tlt = _threshold(config, "duration", "supportive_tlt_return_3m_pct", 2.0)
    stress_tlt = _threshold(config, "duration", "stress_tlt_return_3m_pct", -3.0)
    gold_bid = _threshold(config, "hedge", "gold_bid_return_3m_pct", 3.0)
    gold_weak = _threshold(config, "hedge", "gold_weak_return_3m_pct", -3.0)
    inflation_bid = _threshold(config, "commodities", "inflation_bid_gsg_return_3m_pct", 3.0)
    inflation_soft = _threshold(config, "commodities", "inflation_soft_gsg_return_3m_pct", -3.0)

    equity = "risk_on" if spy_3m >= risk_on_spy else "risk_off" if spy_3m <= risk_off_spy else "mixed"
    leadership_spread = smh_3m - spy_3m
    semiconductor = "strong" if smh_3m >= smh_strong and leadership_spread >= smh_vs_spy else "weak" if smh_3m < 0 and leadership_spread < 0 else "mixed"
    breadth = "broad" if iwm_rs_3m >= broad_iwm else "weak" if iwm_rs_3m <= weak_iwm else "narrow"
    duration = "supportive" if tlt_3m >= supportive_tlt else "stress" if tlt_3m <= stress_tlt else "neutral"
    hedge = "gold_bid" if gld_3m >= gold_bid else "gold_weak" if gld_3m <= gold_weak else "neutral"
    commodities = "inflation_bid" if gsg_3m >= inflation_bid else "inflation_soft" if gsg_3m <= inflation_soft else "neutral"

    axes = {
        "equity": equity,
        "semiconductor_leadership": semiconductor,
        "breadth": breadth,
        "duration": duration,
        "hedge": hedge,
        "commodities": commodities,
    }
    axis_scores = {
        "SPY_return_3m_pct": spy_3m,
        "SMH_return_3m_pct": smh_3m,
        "SMH_vs_SPY_3m_pct": round(leadership_spread, 2),
        "IWM_rs_vs_SPY_3m_pct": iwm_rs_3m,
        "TLT_return_3m_pct": tlt_3m,
        "GLD_return_3m_pct": gld_3m,
        "GSG_return_3m_pct": gsg_3m,
    }
    evidence = {
        "SPY_return_1m_pct": _return_1m(metrics, "SPY"),
        "SMH_return_1m_pct": _return_1m(metrics, "SMH"),
        "IWM_rs_vs_SPY_3m_pct": iwm_rs_3m,
        "TLT_return_3m_pct": tlt_3m,
        "GLD_return_3m_pct": gld_3m,
        "GSG_return_3m_pct": gsg_3m,
    }
    return axes, axis_scores, evidence


def _classify_from_axes(axes: dict[str, str]) -> str:
    if axes.get("duration") == "stress" and axes.get("hedge") == "gold_bid":
        return "Rate-hike repricing"
    if axes.get("equity") == "risk_off":
        return "Defensive / policy stress"
    if axes.get("equity") == "risk_on" and axes.get("semiconductor_leadership") == "strong" and axes.get("breadth") in {"narrow", "weak"}:
        return "Risk-on narrow leadership"
    if axes.get("equity") == "risk_on" and axes.get("breadth") == "broad":
        return "Risk-on growth"
    return "Policy transition / mixed regime"


def _what_changed(candidate: str, axes: dict[str, str], axis_scores: dict[str, float]) -> list[str]:
    bullets: list[str] = []
    if candidate == "Risk-on narrow leadership":
        bullets.append("Equity trend is positive, but leadership is concentrated rather than broadly confirmed.")
    elif candidate == "Risk-on growth":
        bullets.append("Equity trend and breadth both support a broader risk-on interpretation.")
    elif candidate == "Rate-hike repricing":
        bullets.append("Duration stress and hedge demand point to a rates-sensitive regime interpretation.")
    elif candidate == "Defensive / policy stress":
        bullets.append("Equity trend is weak enough to require a defensive regime interpretation.")
    else:
        bullets.append("Cross-asset evidence is mixed, so the deterministic candidate remains a transition regime.")

    if axes.get("semiconductor_leadership") == "strong":
        bullets.append(f"Semiconductor leadership is strong versus SPY ({axis_scores.get('SMH_vs_SPY_3m_pct')} percentage points over 3m).")
    if axes.get("breadth") == "narrow":
        bullets.append("Small-cap relative strength is not broad enough to confirm full-market participation.")
    if axes.get("hedge") == "gold_weak":
        bullets.append("Gold is not confirming hedge demand in the current evidence window.")
    if axes.get("duration") == "neutral":
        bullets.append("Duration evidence is neutral rather than a clean easing or stress signal.")
    return bullets[:4]


def classify_regime_shadow(
    *,
    metrics: dict[str, Any],
    macro_data_audit_summary: dict[str, Any] | None,
    thresholds: dict[str, Any],
    legacy_regime: str,
    legacy_confidence: float,
) -> dict[str, Any]:
    """Build a shadow deterministic regime candidate.

    The returned payload is intended for comparison and fixture replay. It must
    not drive production lane scoring or client-facing portfolio actions until a
    later control-layer decision explicitly promotes it.
    """

    axes, axis_scores, evidence = _axis_labels(metrics, thresholds)
    candidate = _classify_from_axes(axes)
    confidence_payload = compute_shadow_confidence(
        candidate_regime=candidate,
        axes=axes,
        axis_scores=axis_scores,
        macro_data_audit_summary=macro_data_audit_summary or {},
        config=thresholds,
    )
    confidence = confidence_payload["confidence"]
    differs = candidate != legacy_regime or abs(float(confidence) - float(legacy_confidence)) >= 0.05

    return {
        "schema_version": "1.0",
        "method": "deterministic_axis_classifier_v1_shadow",
        "shadow_only": True,
        "client_facing_authority": False,
        "decision_impact": "none_shadow_comparison_only",
        "candidate_regime": candidate,
        "candidate_confidence": confidence,
        "legacy_regime": legacy_regime,
        "legacy_confidence": legacy_confidence,
        "differs_from_legacy": differs,
        "axes": axes,
        "axis_scores": axis_scores,
        "evidence": evidence,
        "confidence_decomposition": confidence_payload,
        "what_changed": _what_changed(candidate, axes, axis_scores),
        "notes": [
            "Shadow-only deterministic candidate; not used for production lane scoring or client-facing decisions.",
            "Legacy regime and lane_adjustments remain the production-compatible path until explicit promotion.",
        ],
    }
