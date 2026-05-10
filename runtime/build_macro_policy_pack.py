from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from runtime.regime_memory import update_regime_memory

PRICING_DIR = Path("output/pricing")
MACRO_DIR = Path("output/macro")
RS_PATH = Path("output/market_history/etf_relative_strength.json")
MACRO_CONTEXT_PATH = Path("config/etf_macro_fundamental_context.yml")


def latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


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


def _rs_3m(metrics: dict[str, Any], symbol: str) -> float:
    return _num(_metric(metrics, symbol).get("rs_vs_spy_3m_pct"), 0.0)


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


def central_banks_for_regime(regime: str) -> dict[str, dict[str, Any]]:
    restrictive_note = "Restrictive / data-dependent"
    neutral_note = "Neutral / transition"
    return {
        "fed": {
            "stance": restrictive_note if regime != "Rate-cut anticipation" else neutral_note,
            "likely_direction": "Hold-to-ease path, but timing remains data-dependent",
            "main_risk": "Real-rate repricing or delayed easing can pressure duration and speculative beta.",
            "etf_implication": "Prefer quality, profitable growth and cash discipline over weak balance-sheet beta.",
            "confidence": 0.65,
        },
        "ecb": {
            "stance": neutral_note,
            "likely_direction": "Gradual easing bias if inflation and growth allow",
            "main_risk": "Europe may not outperform without earnings breadth and currency support.",
            "etf_implication": "Non-U.S. developed exposure remains watchlist, not automatic add.",
            "confidence": 0.55,
        },
        "boe": {
            "stance": neutral_note,
            "likely_direction": "Cautious easing bias",
            "main_risk": "Sticky services inflation keeps UK duration and cyclicals mixed.",
            "etf_implication": "No direct portfolio action unless UK exposure enters the universe.",
            "confidence": 0.45,
        },
        "boj": {
            "stance": "Gradual normalization risk",
            "likely_direction": "Slow tightening / balance-sheet normalization risk",
            "main_risk": "A yield or yen shock can tighten global financial conditions.",
            "etf_implication": "Avoid treating long-duration exposure as automatically defensive.",
            "confidence": 0.50,
        },
        "pboc": {
            "stance": "Supportive but credibility-sensitive",
            "likely_direction": "Targeted support rather than broad reflation unless confidence improves",
            "main_risk": "China stimulus disappointment can weigh on China beta and commodities.",
            "etf_implication": "China exposure remains tactical watchlist unless price confirmation improves.",
            "confidence": 0.55,
        },
    }


def policy_catalysts(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "policy_area": "AI infrastructure and semiconductor supply chains",
            "latest_signal": "Capital spending and strategic supply-chain policy continue to support semiconductor and infrastructure lanes.",
            "affected_lanes": ["AI compute infrastructure", "Grid buildout / electrification"],
            "direction": "supportive",
            "time_horizon": "3-12 months",
            "confidence": 0.72,
            "transfer_to_report": True,
        },
        {
            "policy_area": "Defense and sovereign resilience",
            "latest_signal": "Defense-budget durability remains a structural support, but ETF vehicle choice still matters.",
            "affected_lanes": ["Defense innovation / sovereign resilience"],
            "direction": "supportive but implementation-sensitive",
            "time_horizon": "6-18 months",
            "confidence": 0.65,
            "transfer_to_report": True,
        },
        {
            "policy_area": "Energy security and nuclear policy",
            "latest_signal": "Energy-security policy keeps uranium and nuclear infrastructure relevant, but timing remains price-confirmation dependent.",
            "affected_lanes": ["Uranium / nuclear fuel cycle"],
            "direction": "supportive but cyclical",
            "time_horizon": "6-24 months",
            "confidence": 0.60,
            "transfer_to_report": False,
        },
        {
            "policy_area": "China stimulus and platform regulation",
            "latest_signal": "Support remains watchlist-relevant, but confidence and earnings confirmation are still required.",
            "affected_lanes": ["China platform beta", "EM equity beta"],
            "direction": "mixed",
            "time_horizon": "1-6 months",
            "confidence": 0.52,
            "transfer_to_report": False,
        },
    ]


def lane_adjustments(regime: str, metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "AI compute infrastructure": {
            "score_adjustment": 0.16 if regime in {"Risk-on narrow leadership", "Risk-on growth"} else 0.08,
            "reason": "Regime and price leadership still support AI compute exposure, but concentration discipline applies.",
        },
        "Grid buildout / electrification": {
            "score_adjustment": 0.10,
            "reason": "AI power demand and infrastructure policy support the grid lane; funding still depends on PAVE-vs-GRID duel evidence.",
        },
        "Defense innovation / sovereign resilience": {
            "score_adjustment": 0.08,
            "reason": "Policy support is durable, but implementation quality remains the main decision bottleneck.",
        },
        "Gold hedge review": {
            "score_adjustment": -0.06 if _return_3m(metrics, "GLD") < 0 else 0.04,
            "reason": "Gold must prove hedge behavior; macro status alone is not enough for fresh capital.",
        },
        "Non-U.S. developed diversification": {
            "score_adjustment": 0.04,
            "reason": "Diversification gap is real, but policy and relative-strength confirmation are not yet decisive.",
        },
        "China platform beta": {
            "score_adjustment": -0.08,
            "reason": "Policy support is not yet enough to offset confidence and price-confirmation risk.",
        },
        "Rate-sensitive small caps": {
            "score_adjustment": -0.10,
            "reason": "Current regime does not yet confirm broad small-cap risk appetite.",
        },
    }


def portfolio_implications(regime: str) -> list[str]:
    if regime == "Risk-on narrow leadership":
        return [
            "Keep SMH as the earned leader, but do not confuse narrow leadership with broad diversification.",
            "Require replacement duels for SPY overlap, PPA implementation quality and PAVE versus GRID before funding challengers.",
            "Keep cash discipline because the regime supports selectivity more than broad risk expansion.",
        ]
    if regime == "Risk-on growth":
        return [
            "Risk appetite is supportive, but fresh adds still need position-size room and pricing confirmation.",
            "Growth and infrastructure lanes can be considered if they do not worsen concentration.",
            "Defensive hedges should be reviewed for opportunity cost.",
        ]
    return [
        "Stay invested, but make new capital pass a stricter macro and relative-strength filter.",
        "Treat SPY, PPA, PAVE and GLD as active review items rather than passive holds.",
        "Do not fund replacement candidates until the pricing basis and direct duel evidence are visible.",
    ]


def build_pack(pricing_audit_path: Path, relative_strength_path: Path, macro_context_path: Path) -> dict[str, Any]:
    pricing = load_json(pricing_audit_path)
    rs_payload = load_json(relative_strength_path)
    metrics = dict(rs_payload.get("metrics", {}) or {})
    macro_context = load_yaml(macro_context_path)
    report_date = str(pricing.get("requested_close_date") or datetime.utcnow().date().isoformat())
    regime, confidence, what_changed = classify_regime(metrics)

    pack = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "report_date": report_date,
        "source_files": {
            "pricing_audit": str(pricing_audit_path),
            "relative_strength": str(relative_strength_path) if relative_strength_path.exists() else None,
            "macro_context": str(macro_context_path) if macro_context_path.exists() else None,
        },
        "regime": {
            "current": regime,
            "previous": macro_context.get("previous_regime", "Unknown"),
            "confidence": confidence,
            "what_changed": what_changed,
        },
        "central_banks": central_banks_for_regime(regime),
        "macro_signals": {
            "equity_leadership": {
                "signal": "narrow_ai_leadership" if regime == "Risk-on narrow leadership" else "mixed",
                "evidence": {
                    "SMH_return_3m_pct": _return_3m(metrics, "SMH"),
                    "SPY_return_3m_pct": _return_3m(metrics, "SPY"),
                    "IWM_rs_vs_SPY_3m_pct": _rs_3m(metrics, "IWM"),
                },
            },
            "duration": {
                "signal": "not_confirmed_as_tailwind" if _return_3m(metrics, "TLT") <= 0 else "supportive",
                "evidence": {"TLT_return_3m_pct": _return_3m(metrics, "TLT")},
            },
            "hedge_ballast": {
                "signal": "under_review" if _return_3m(metrics, "GLD") <= 0 else "supportive",
                "evidence": {"GLD_return_3m_pct": _return_3m(metrics, "GLD")},
            },
        },
        "policy_catalysts": policy_catalysts(metrics),
        "cross_asset_confirmation": [
            "Semiconductor leadership supports SMH, but SPY overlap must remain explicit.",
            "Small-cap and duration signals are not strong enough to justify broad beta expansion.",
            "Gold is treated as a hedge review item unless price behavior improves.",
        ],
        "portfolio_implications": portfolio_implications(regime),
        "lane_adjustments": lane_adjustments(regime, metrics),
        "report_transfer": {
            "max_what_changed_bullets": 3,
            "max_portfolio_implications": 3,
            "max_policy_catalysts": 2,
            "style_rule": "Transfer only decision-relevant macro information. Do not dump the full research pack into the report.",
        },
    }
    pack["regime_memory"] = update_regime_memory(pack)
    return pack


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--relative-strength", default=str(RS_PATH))
    parser.add_argument("--macro-context", default=str(MACRO_CONTEXT_PATH))
    parser.add_argument("--output-dir", default=str(MACRO_DIR))
    args = parser.parse_args()

    pricing_audit_path = Path(args.pricing_audit) if args.pricing_audit else latest_file(PRICING_DIR, "price_audit_*.json")
    pack = build_pack(pricing_audit_path, Path(args.relative_strength), Path(args.macro_context))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = str(pack.get("report_date", "unknown")).replace("-", "")
    out_path = output_dir / f"etf_macro_policy_pack_{suffix}.json"
    latest_path = output_dir / "latest.json"
    out_path.write_text(json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8")
    latest_path.write_text(json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8")

    memory = pack.get("regime_memory", {})
    print(
        "ETF_MACRO_POLICY_PACK_OK | "
        f"report_date={pack.get('report_date')} | regime={pack.get('regime', {}).get('current')} | "
        f"transition={memory.get('transition_state')} | weeks={memory.get('weeks_in_regime')} | output={out_path}"
    )


if __name__ == "__main__":
    main()
