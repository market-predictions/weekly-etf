from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from macro_sources.build_macro_data_audit import build_macro_data_audit
from runtime.regime_memory import update_regime_memory
from tools.validate_macro_data_audit import validate as validate_macro_data_audit
from tools.validate_macro_policy_pack import _validate_pack

PRICING_DIR = Path("output/pricing")
MACRO_DIR = Path("output/macro")
RS_PATH = Path("output/market_history/etf_relative_strength.json")
MACRO_CONTEXT_PATH = Path("config/etf_macro_fundamental_context.yml")
MACRO_AUDIT_POINTER = Path("output/macro/latest_macro_data_audit_path.txt")
MACRO_SOURCE_CONFIG = Path("config/macro_data_sources.yml")
CB_CALENDAR_PATH = Path("config/cb_calendar.yml")
ECB_JUNE_2026_HIKE_DATE = "2026-06-11"


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_macro_audit(payload: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_date = str(payload.get("reference_date") or "unknown")
    run_id = str(payload.get("run_id") or "unknown")
    out_path = output_dir / f"macro_data_audit_{reference_date}_{run_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "latest_macro_data_audit_path.txt").write_text(str(out_path) + "\n", encoding="utf-8")
    return out_path


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def resolve_macro_data_audit_path(path_value: str | None, *, reference_date: str, run_id: str, output_dir: Path) -> Path | None:
    if path_value:
        path = Path(path_value)
        if not path.exists():
            raise RuntimeError(f"Explicit macro data audit path does not exist: {path}")
        validate_macro_data_audit(path)
        return path

    fixture = os.environ.get("MRKT_RPRTS_MACRO_DATA_AUDIT_FIXTURE", "").strip()
    try:
        payload = build_macro_data_audit(
            config_path=MACRO_SOURCE_CONFIG,
            cb_calendar_path=CB_CALENDAR_PATH,
            reference_date=reference_date,
            run_id=run_id,
            fixture_path=Path(fixture) if fixture else None,
        )
        path = _write_macro_audit(payload, output_dir)
        validate_macro_data_audit(path)
        return path
    except Exception as exc:
        # Phase 2 macro data audit is shadow-only. It must not block production
        # pricing/report delivery until the later deterministic regime and
        # compliance gates explicitly promote it to authority.
        print(
            "ETF_MACRO_DATA_AUDIT_SHADOW_UNAVAILABLE | "
            f"reference_date={reference_date} | run_id={run_id} | reason={exc}"
        )
        return None


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


def _date_or_none(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _ecb_june_2026_hike_applies(report_date: str | None) -> bool:
    report = _date_or_none(report_date)
    hike = _date_or_none(ECB_JUNE_2026_HIKE_DATE)
    return bool(report and hike and report >= hike)


def classify_regime(metrics: dict[str, Any]) -> tuple[str, float, list[str]]:
    smh = _return_3m(metrics, "SMH")
    spy = _return_3m(metrics, "SPY")
    gld = _return_3m(metrics, "GLD")
    tlt = _return_3m(metrics, "TLT")
    iwm = _rs_3m(metrics, "IWM")

    changes: list[str] = []
    if smh > spy + 4:
        changes.append("AI / semiconductor leadership remains the dominant equity impulse.")
    if iwm < -2:
        changes.append("Small-cap breadth still does not confirm a broad risk-on regime.")
    if tlt < 0:
        changes.append("Duration is not yet giving a clean easing confirmation.")
    if gld < 0:
        changes.append("Gold hedge behavior remains under review rather than automatic ballast.")

    if smh > 8 and iwm < 0:
        return "Risk-on narrow leadership", 0.72, changes[:3]
    if tlt < -3 and gld > 3:
        return "Rate-hike repricing", 0.62, changes[:3]
    if spy > 4 and iwm > 0:
        return "Risk-on growth", 0.66, changes[:3]
    return "Policy transition / mixed regime", 0.64, changes[:3] or ["No decisive full-regime break; allocation discipline remains more important than theme expansion."]


def central_banks_for_regime(regime: str, report_date: str | None = None) -> dict[str, dict[str, Any]]:
    restrictive_note = "Restrictive / data-dependent"
    neutral_note = "Neutral / transition"
    ecb = {
        "stance": neutral_note,
        "likely_direction": "Gradual easing bias if inflation and growth allow",
        "main_risk": "Europe may not outperform without earnings breadth and currency support.",
        "etf_implication": "Non-U.S. developed exposure remains watchlist, not automatic add.",
        "confidence": 0.55,
    }
    if _ecb_june_2026_hike_applies(report_date):
        ecb = {
            "stance": "Tightening / inflation-sensitive",
            "likely_direction": "Rate hike delivered; the next step remains data- and inflation-dependent.",
            "main_risk": "Renewed energy-led inflation pressure can raise the hurdle for rate-sensitive and non-U.S. developed-market exposure.",
            "etf_implication": "IEFA exposure is now present, but further non-U.S. developed allocations still require relative-strength, pricing and portfolio-discipline confirmation.",
            "confidence": 0.70,
            "event_date": ECB_JUNE_2026_HIKE_DATE,
            "event_status": "verified_report_week_policy_event",
        }
    return {
        "fed": {"stance": restrictive_note if regime != "Rate-cut anticipation" else neutral_note, "likely_direction": "Hold-to-ease path, but timing remains data-dependent", "main_risk": "Real-rate repricing or delayed easing can pressure duration and speculative beta.", "etf_implication": "Prefer quality, profitable growth and cash discipline over weak balance-sheet beta.", "confidence": 0.65},
        "ecb": ecb,
        "boe": {"stance": neutral_note, "likely_direction": "Cautious easing bias", "main_risk": "Sticky services inflation keeps UK duration and cyclicals mixed.", "etf_implication": "No direct portfolio action unless UK exposure enters the universe.", "confidence": 0.45},
        "boj": {"stance": "Gradual normalization risk", "likely_direction": "Slow tightening / balance-sheet normalization risk", "main_risk": "A yield or yen shock can tighten global financial conditions.", "etf_implication": "Avoid treating long-duration exposure as automatically defensive.", "confidence": 0.50},
        "pboc": {"stance": "Supportive but credibility-sensitive", "likely_direction": "Targeted support rather than broad reflation unless confidence improves", "main_risk": "China stimulus disappointment can weigh on China beta and commodities.", "etf_implication": "China exposure remains tactical watchlist unless price confirmation improves.", "confidence": 0.55},
    }


def policy_catalysts(metrics: dict[str, Any], report_date: str | None = None) -> list[dict[str, Any]]:
    catalysts = [
        {"policy_area": "AI infrastructure and semiconductor supply chains", "latest_signal": "Capital spending and strategic supply-chain policy continue to support semiconductor and infrastructure lanes.", "affected_lanes": ["AI compute infrastructure", "Grid buildout / electrification"], "direction": "supportive", "time_horizon": "3-12 months", "confidence": 0.72, "transfer_to_report": True},
        {"policy_area": "Defense and sovereign resilience", "latest_signal": "Defense-budget durability remains a structural support, but ETF vehicle choice still matters.", "affected_lanes": ["Defense innovation / sovereign resilience"], "direction": "supportive but implementation-sensitive", "time_horizon": "6-18 months", "confidence": 0.65, "transfer_to_report": True},
        {"policy_area": "Energy security and nuclear policy", "latest_signal": "Energy-security policy keeps uranium and nuclear infrastructure relevant, but timing remains price-confirmation dependent.", "affected_lanes": ["Uranium / nuclear fuel cycle"], "direction": "supportive but cyclical", "time_horizon": "6-24 months", "confidence": 0.60, "transfer_to_report": False},
        {"policy_area": "China stimulus and platform regulation", "latest_signal": "Support remains watchlist-relevant, but confidence and earnings confirmation are still required.", "affected_lanes": ["China platform beta", "EM equity beta"], "direction": "mixed", "time_horizon": "1-6 months", "confidence": 0.52, "transfer_to_report": False},
    ]
    if _ecb_june_2026_hike_applies(report_date):
        catalysts.insert(
            0,
            {
                "policy_area": "ECB rate-policy tightening",
                "latest_signal": "The ECB raised rates this week in response to renewed inflation pressure; this raises the hurdle for rate-sensitive and non-U.S. developed-market exposure but does not override pricing, relative-strength or portfolio-discipline gates.",
                "affected_lanes": ["Non-U.S. developed diversification", "Rate-sensitive small caps", "Long-duration bonds"],
                "direction": "restrictive / inflation-sensitive",
                "time_horizon": "1-6 months",
                "confidence": 0.70,
                "event_date": ECB_JUNE_2026_HIKE_DATE,
                "event_status": "verified_report_week_policy_event",
                "transfer_to_report": True,
            },
        )
    return catalysts


def lane_adjustments(regime: str, metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "AI compute infrastructure": {"score_adjustment": 0.16 if regime in {"Risk-on narrow leadership", "Risk-on growth"} else 0.08, "reason": "Regime and price leadership still support AI compute exposure, but concentration discipline applies."},
        "Grid buildout / electrification": {"score_adjustment": 0.10, "reason": "AI power demand and infrastructure policy support the grid lane; funding still depends on PAVE-vs-GRID duel evidence."},
        "Defense innovation / sovereign resilience": {"score_adjustment": 0.08, "reason": "Policy support is durable, but implementation quality remains the main decision bottleneck."},
        "Gold hedge review": {"score_adjustment": -0.06 if _return_3m(metrics, "GLD") < 0 else 0.04, "reason": "Gold must prove hedge behavior; macro status alone is not enough for fresh capital."},
        "Non-U.S. developed diversification": {"score_adjustment": 0.04, "reason": "Non-U.S. developed exposure is now present through IEFA, but additional allocation still needs policy, pricing and relative-strength confirmation."},
        "China platform beta": {"score_adjustment": -0.08, "reason": "Policy support is not yet enough to offset confidence and price-confirmation risk."},
        "Rate-sensitive small caps": {"score_adjustment": -0.10, "reason": "Current regime does not yet confirm broad small-cap risk appetite."},
    }


def portfolio_implications(regime: str) -> list[str]:
    if regime == "Risk-on narrow leadership":
        return ["Keep SMH as the earned leader, but do not confuse narrow leadership with broad diversification.", "Require replacement duels for SPY overlap, PPA implementation quality and PAVE versus GRID before funding challengers.", "Keep cash discipline because the regime supports selectivity more than broad risk expansion."]
    if regime == "Risk-on growth":
        return ["Risk appetite is supportive, but fresh adds still need position-size room and pricing confirmation.", "Growth and infrastructure lanes can be considered if they do not worsen concentration.", "Defensive hedges should be reviewed for opportunity cost."]
    return ["Stay invested, but make new capital pass a stricter macro and relative-strength filter.", "Treat SPY, PPA, PAVE and GLD as active review items rather than passive holds.", "Do not fund replacement candidates until the pricing basis and direct duel evidence are visible."]


def _field_authority_contract() -> dict[str, dict[str, Any]]:
    return {
        "regime": {"authority_class": "client_safe_descriptive_legacy", "client_surface_allowed": True, "decision_authority": "descriptive_only", "notes": ["May be shown as current descriptive regime wording through the client-safe macro report surface.", "Does not by itself authorize lane scoring, fundability, or trades."]},
        "confidence_decomposition": {"authority_class": "shadow_explanation", "client_surface_allowed": False, "decision_authority": "none_shadow_explanation_only", "notes": ["Internal explanation of legacy confidence only; do not expose components directly in client reports."]},
        "central_banks": {"authority_class": "client_safe_descriptive_policy_context", "client_surface_allowed": True, "decision_authority": "descriptive_only", "notes": ["May be paraphrased as policy context; it cannot create portfolio action by itself."]},
        "macro_signals": {"authority_class": "internal_evidence_context", "client_surface_allowed": False, "decision_authority": "none_internal_evidence_only", "notes": ["Internal evidence layer; only sanitized summaries may transfer through report_transfer and macro_report_surface."]},
        "policy_catalysts": {"authority_class": "client_safe_descriptive_catalyst_context", "client_surface_allowed": True, "decision_authority": "descriptive_only", "notes": ["Only catalysts explicitly marked transfer_to_report=true may be surfaced."]},
        "portfolio_implications": {"authority_class": "client_safe_discipline_context", "client_surface_allowed": True, "decision_authority": "descriptive_only", "notes": ["May describe discipline and review implications; does not authorize trades without portfolio gates."]},
        "lane_adjustments": {"authority_class": "legacy_compatibility_decision_input", "client_surface_allowed": False, "decision_authority": "legacy_lane_adjustments_only", "notes": ["Maintained for backward-compatible lane discovery only; not a promotion of deterministic regime output."]},
        "macro_data_audit_summary": {"authority_class": "shadow_provenance_only", "client_surface_allowed": False, "decision_authority": "none_phase2_audit_only", "notes": ["Audit summary may support provenance review but cannot set regime or portfolio authority."]},
        "deterministic_regime_shadow": {"authority_class": "shadow_comparison_only", "client_surface_allowed": False, "decision_authority": "none_shadow_comparison_only", "notes": ["Raw macro_axes, macro_axis_scores, macro_evidence and shadow regime output must not enter client reports or decisions."]},
        "active_drivers": {"authority_class": "stage1_thesis_shadow_only", "client_surface_allowed": False, "decision_authority": "none_wp9_not_promoted", "notes": ["Stage-1 drivers are internal only until Stage-2 confirmation and explicit promotion."]},
        "report_transfer": {"authority_class": "client_surface_filter", "client_surface_allowed": True, "decision_authority": "output_contract_only", "notes": ["Limits what descriptive macro content can reach the report; does not add investment authority."]},
    }


def _promotion_gates_contract() -> dict[str, Any]:
    return {
        "status": "not_promoted",
        "client_surface_status": "descriptive_surface_only",
        "decision_authority_status": "legacy_lane_adjustments_only",
        "required_before_decision_authority": [
            "macro_policy_pack_schema_contract_green",
            "deterministic_regime_fixture_replay_green",
            "macro_audit_fixture_replay_green",
            "macro_compliance_validator_green",
            "bilingual_report_surface_validation_green",
            "production_report_validation_green",
            "explicit_control_layer_promotion_decision",
        ],
        "blocked_authority": [
            "raw_macro_axes_client_surface",
            "raw_macro_axis_scores_client_surface",
            "deterministic_regime_shadow_client_surface",
            "stage1_thesis_candidates_client_surface",
            "macro_direct_lane_scoring_authority",
            "macro_direct_fundability_authority",
            "macro_direct_portfolio_trade_authority",
        ],
    }


def _macro_audit_summary(macro_data_audit_path: Path | None, macro_data_audit: dict[str, Any]) -> dict[str, Any]:
    if macro_data_audit_path is None:
        return {"present": False, "status": "shadow_unavailable", "mode": "none", "reference_date": None, "observation_count": 0, "shadow_only": True, "client_facing_authority": False, "decision_impact": "none_phase2_audit_only"}
    return {"present": bool(macro_data_audit), "status": macro_data_audit.get("status"), "mode": macro_data_audit.get("mode"), "reference_date": macro_data_audit.get("reference_date"), "observation_count": (macro_data_audit.get("summary") or {}).get("observation_count"), "shadow_only": True, "client_facing_authority": False, "decision_impact": "none_phase2_audit_only"}


def _confidence_decomposition(regime: str, confidence: float, metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "method": "legacy_proxy_static_explained_for_schema_v1",
        "shadow_only": True,
        "client_facing_authority": False,
        "decision_impact": "none_shadow_explanation_only",
        "components": {"legacy_confidence": confidence, "SMH_return_3m_pct": _return_3m(metrics, "SMH"), "SPY_return_3m_pct": _return_3m(metrics, "SPY"), "IWM_rs_vs_SPY_3m_pct": _rs_3m(metrics, "IWM"), "GLD_return_3m_pct": _return_3m(metrics, "GLD"), "TLT_return_3m_pct": _return_3m(metrics, "TLT")},
        "notes": ["This is a compatibility decomposition for the legacy proxy regime path.", "Deterministic derived confidence is planned for Phase 3 and is not yet production authority.", f"Current legacy regime label: {regime}"],
    }


def _active_drivers_placeholder() -> list[dict[str, Any]]:
    return []


def build_pack(pricing_audit_path: Path, relative_strength_path: Path, macro_context_path: Path, macro_data_audit_path: Path | None = None) -> dict[str, Any]:
    pricing = load_json(pricing_audit_path)
    rs_payload = load_json(relative_strength_path)
    metrics = dict(rs_payload.get("metrics", {}) or {})
    macro_context = load_yaml(macro_context_path)
    macro_data_audit = load_json(macro_data_audit_path)
    report_date = str(pricing.get("requested_close_date") or datetime.utcnow().date().isoformat())
    regime, confidence, what_changed = classify_regime(metrics)

    pack = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "report_date": report_date,
        "source_files": {"pricing_audit": str(pricing_audit_path), "relative_strength": str(relative_strength_path) if relative_strength_path.exists() else None, "macro_context": str(macro_context_path) if macro_context_path.exists() else None, "macro_data_audit": str(macro_data_audit_path) if macro_data_audit_path else None},
        "authority": {
            "authority_class": "legacy_compatibility_pack",
            "client_surface_allowed": True,
            "decision_authority": "legacy_lane_adjustments_only",
            "decision_framework": "Legacy macro lane adjustments remain available for backward-compatible lane discovery only.",
            "input_state_contract": "Pricing audit and relative-strength artifacts remain production inputs; macro audit is metadata-only until promoted.",
            "output_contract": "Client-facing macro content is allowed only through the client-safe macro report surface and must not expose shadow-only fields.",
            "operational_runbook": "Validate schema and compatibility before lane discovery; later phases may replace legacy regime logic after fixture/shadow review and explicit promotion.",
            "shadow_only": True,
            "client_facing_authority": False,
            "decision_impact": "legacy_lane_adjustments_only",
        },
        "field_authority": _field_authority_contract(),
        "promotion_gates": _promotion_gates_contract(),
        "macro_data_audit_summary": _macro_audit_summary(macro_data_audit_path, macro_data_audit),
        "regime": {"current": regime, "previous": macro_context.get("previous_regime", "Unknown"), "confidence": confidence, "confidence_source": "legacy_proxy_static", "what_changed": what_changed},
        "confidence_decomposition": _confidence_decomposition(regime, confidence, metrics),
        "central_banks": central_banks_for_regime(regime, report_date),
        "macro_signals": {
            "equity_leadership": {"signal": "narrow_ai_leadership" if regime == "Risk-on narrow leadership" else "mixed", "evidence": {"SMH_return_3m_pct": _return_3m(metrics, "SMH"), "SPY_return_3m_pct": _return_3m(metrics, "SPY"), "IWM_rs_vs_SPY_3m_pct": _rs_3m(metrics, "IWM")}},
            "duration": {"signal": "not_confirmed_as_tailwind" if _return_3m(metrics, "TLT") <= 0 else "supportive", "evidence": {"TLT_return_3m_pct": _return_3m(metrics, "TLT")}},
            "hedge_ballast": {"signal": "under_review" if _return_3m(metrics, "GLD") <= 0 else "supportive", "evidence": {"GLD_return_3m_pct": _return_3m(metrics, "GLD")}},
        },
        "policy_catalysts": policy_catalysts(metrics, report_date),
        "cross_asset_confirmation": ["Semiconductor leadership supports SMH, but SPY overlap must remain explicit.", "Small-cap and duration signals are not strong enough to justify broad beta expansion.", "Gold is treated as a hedge review item unless price behavior improves."],
        "portfolio_implications": portfolio_implications(regime),
        "lane_adjustments": lane_adjustments(regime, metrics),
        "active_drivers": _active_drivers_placeholder(),
        "report_transfer": {"max_what_changed_bullets": 3, "max_portfolio_implications": 3, "max_policy_catalysts": 3, "style_rule": "Transfer only decision-relevant macro information. Do not dump the full research pack into the report."},
    }
    pack["regime_memory"] = update_regime_memory(pack)
    _validate_pack(pack)
    return pack


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--relative-strength", default=str(RS_PATH))
    parser.add_argument("--macro-context", default=str(MACRO_CONTEXT_PATH))
    parser.add_argument("--macro-data-audit", default=None)
    parser.add_argument("--output-dir", default=str(MACRO_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--reference-date", default=None)
    args = parser.parse_args()

    pricing_audit_path = Path(args.pricing_audit) if args.pricing_audit else latest_file(PRICING_DIR, "price_audit_*.json")
    pricing = load_json(pricing_audit_path)
    reference_date = args.reference_date or os.environ.get("REQUESTED_CLOSE_DATE") or str(pricing.get("requested_close_date") or datetime.now(timezone.utc).date().isoformat())
    run_id = args.run_id or os.environ.get("ETF_PRICING_RUN_ID") or os.environ.get("MRKT_RPRTS_RUN_ID") or _default_run_id()
    output_dir = Path(args.output_dir)
    macro_data_audit_path = resolve_macro_data_audit_path(args.macro_data_audit, reference_date=reference_date, run_id=run_id, output_dir=output_dir)
    pack = build_pack(pricing_audit_path, Path(args.relative_strength), Path(args.macro_context), macro_data_audit_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = str(pack.get("report_date", "unknown")).replace("-", "")
    out_path = output_dir / f"etf_macro_policy_pack_{suffix}_{run_id}.json"
    latest_path = output_dir / "latest.json"
    out_path.write_text(json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8")
    latest_path.write_text(json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8")

    memory = pack.get("regime_memory", {})
    audit_summary = pack.get("macro_data_audit_summary", {})
    promotion = pack.get("promotion_gates", {})
    print(
        "ETF_MACRO_POLICY_PACK_OK | "
        f"report_date={pack.get('report_date')} | regime={pack.get('regime', {}).get('current')} | "
        f"transition={memory.get('transition_state')} | weeks={memory.get('weeks_in_regime')} | "
        f"macro_audit_present={audit_summary.get('present')} | schema={pack.get('schema_version')} | "
        f"promotion_status={promotion.get('status')} | macro_audit={macro_data_audit_path} | output={out_path}"
    )


if __name__ == "__main__":
    main()
