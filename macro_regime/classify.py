from __future__ import annotations

from typing import Any

from macro_regime.confidence import compute_shadow_confidence


CONFIDENCE_DIFF_THRESHOLD = 0.05


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


def _macro_threshold(config: dict[str, Any], axis: str, key: str, default: float) -> float:
    return _num(((config.get("macro_axes") or {}).get(axis) or {}).get(key), default)


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


def _observations_by_key(macro_data_audit: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in (macro_data_audit or {}).get("observations") or []:
        if isinstance(row, dict) and row.get("key"):
            out[str(row.get("key"))] = row
    return out


def _obs_value(observations: dict[str, dict[str, Any]], key: str) -> float | None:
    if key not in observations:
        return None
    return _num(observations[key].get("value"), None)  # type: ignore[arg-type]


def _macro_axis_labels(macro_data_audit: dict[str, Any] | None, config: dict[str, Any]) -> tuple[dict[str, str], dict[str, float], dict[str, Any]]:
    observations = _observations_by_key(macro_data_audit)
    if not observations:
        return {}, {}, {}

    us_10y = _obs_value(observations, "us_10y_yield")
    us_2y = _obs_value(observations, "us_2y_yield")
    real_10y = _obs_value(observations, "us_10y_real_yield")
    breakeven = _obs_value(observations, "us_10y_breakeven")
    fed_funds = _obs_value(observations, "fed_funds_effective")
    vix = _obs_value(observations, "vix_close")

    curve_spread = None
    if us_10y is not None and us_2y is not None:
        curve_spread = round(us_10y - us_2y, 4)

    vix_calm = _macro_threshold(config, "volatility", "vix_calm_below", 16.0)
    vix_stress = _macro_threshold(config, "volatility", "vix_stress_above", 25.0)
    real_restrictive = _macro_threshold(config, "real_rates", "restrictive_above", 1.75)
    real_supportive = _macro_threshold(config, "real_rates", "supportive_below", 0.75)
    curve_inverted = _macro_threshold(config, "yield_curve", "inverted_below", -0.25)
    curve_normalizing = _macro_threshold(config, "yield_curve", "normalizing_above", 0.25)
    breakeven_elevated = _macro_threshold(config, "inflation_expectations", "elevated_above", 2.6)
    breakeven_contained = _macro_threshold(config, "inflation_expectations", "contained_below", 2.3)
    fed_restrictive = _macro_threshold(config, "policy_rate", "restrictive_above", 4.25)
    fed_accommodative = _macro_threshold(config, "policy_rate", "accommodative_below", 2.0)

    axes: dict[str, str] = {}
    if vix is not None:
        axes["volatility"] = "calm" if vix <= vix_calm else "stress" if vix >= vix_stress else "neutral"
    if real_10y is not None:
        axes["real_rates"] = "restrictive" if real_10y >= real_restrictive else "supportive" if real_10y <= real_supportive else "neutral"
    if curve_spread is not None:
        axes["yield_curve"] = "inverted" if curve_spread <= curve_inverted else "normalizing" if curve_spread >= curve_normalizing else "flat"
    if breakeven is not None:
        axes["inflation_expectations"] = "elevated" if breakeven >= breakeven_elevated else "contained" if breakeven <= breakeven_contained else "neutral"
    if fed_funds is not None:
        axes["policy_rate"] = "restrictive" if fed_funds >= fed_restrictive else "accommodative" if fed_funds <= fed_accommodative else "neutral"

    scores = {
        "us_10y_yield": us_10y,
        "us_2y_yield": us_2y,
        "us_10y_2y_spread": curve_spread,
        "us_10y_real_yield": real_10y,
        "us_10y_breakeven": breakeven,
        "fed_funds_effective": fed_funds,
        "vix_close": vix,
    }
    scores = {key: value for key, value in scores.items() if value is not None}
    evidence = {
        "macro_audit_mode": (macro_data_audit or {}).get("mode"),
        "macro_audit_reference_date": (macro_data_audit or {}).get("reference_date"),
        "observation_count": len(observations),
        "observation_keys_used": sorted(observations),
    }
    return axes, scores, evidence


def _classify_from_axes(axes: dict[str, str], macro_axes: dict[str, str] | None = None) -> str:
    macro_axes = macro_axes or {}
    if axes.get("duration") == "stress" and axes.get("hedge") == "gold_bid":
        return "Rate-hike repricing"
    if axes.get("equity") == "risk_off":
        return "Defensive / policy stress"
    if axes.get("equity") == "risk_on" and axes.get("semiconductor_leadership") == "strong" and axes.get("breadth") in {"narrow", "weak"}:
        return "Risk-on narrow leadership"
    if axes.get("equity") == "risk_on" and axes.get("breadth") == "broad":
        return "Risk-on growth"
    if macro_axes.get("volatility") == "stress" or macro_axes.get("yield_curve") == "inverted":
        return "Policy transition / mixed regime"
    return "Policy transition / mixed regime"


def _what_changed(candidate: str, axes: dict[str, str], axis_scores: dict[str, float], macro_axes: dict[str, str] | None = None) -> list[str]:
    macro_axes = macro_axes or {}
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
    if macro_axes.get("real_rates") == "restrictive":
        bullets.append("Audited macro data flags real rates as restrictive, so confidence remains disciplined.")
    if macro_axes.get("volatility") == "stress":
        bullets.append("Audited volatility data is stress-like, reducing risk-on confirmation.")
    return bullets[:5]


def classify_regime_shadow(
    *,
    metrics: dict[str, Any],
    macro_data_audit_summary: dict[str, Any] | None,
    thresholds: dict[str, Any],
    legacy_regime: str,
    legacy_confidence: float,
    macro_data_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a shadow deterministic regime candidate.

    The returned payload is intended for comparison and fixture replay. It must
    not drive production lane scoring or client-facing portfolio actions until a
    later control-layer decision explicitly promotes it.
    """

    axes, axis_scores, evidence = _axis_labels(metrics, thresholds)
    macro_axes, macro_scores, macro_evidence = _macro_axis_labels(macro_data_audit, thresholds)
    candidate = _classify_from_axes(axes, macro_axes)
    confidence_payload = compute_shadow_confidence(
        candidate_regime=candidate,
        axes=axes,
        axis_scores=axis_scores,
        macro_data_audit_summary=macro_data_audit_summary or {},
        config=thresholds,
        macro_axes=macro_axes,
        macro_scores=macro_scores,
    )
    confidence = float(confidence_payload["confidence"])
    legacy_confidence_float = float(legacy_confidence)
    confidence_delta = round(confidence - legacy_confidence_float, 4)
    regime_label_differs = candidate != legacy_regime
    confidence_differs = abs(confidence_delta) >= CONFIDENCE_DIFF_THRESHOLD
    differs = regime_label_differs or confidence_differs

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
        "regime_label_differs": regime_label_differs,
        "confidence_differs": confidence_differs,
        "confidence_delta": confidence_delta,
        "confidence_diff_threshold": CONFIDENCE_DIFF_THRESHOLD,
        "axes": axes,
        "axis_scores": axis_scores,
        "macro_axes": macro_axes,
        "macro_axis_scores": macro_scores,
        "evidence": evidence,
        "macro_evidence": macro_evidence,
        "confidence_decomposition": confidence_payload,
        "what_changed": _what_changed(candidate, axes, axis_scores, macro_axes),
        "notes": [
            "Shadow-only deterministic candidate; not used for production lane scoring or client-facing decisions.",
            "Legacy regime and lane_adjustments remain the production-compatible path until explicit promotion.",
            "differs_from_legacy is retained for backward compatibility and equals regime_label_differs OR confidence_differs.",
        ],
    }
