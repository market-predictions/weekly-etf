from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

MACRO_DIR = Path("output/macro")
REGIME_MEMORY_PATH = MACRO_DIR / "regime_memory.json"


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_regime_memory(path: Path = REGIME_MEMORY_PATH) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _confidence_trend(previous: float | None, current: float) -> str:
    if previous is None:
        return "new"
    delta = current - previous
    if delta >= 0.05:
        return "rising"
    if delta <= -0.05:
        return "falling"
    return "flat"


def _transition_state(previous_regime: str, current_regime: str, weeks_in_regime: int, confidence: float) -> str:
    if not previous_regime or previous_regime == "Unknown":
        return "new_baseline"
    if previous_regime != current_regime:
        return "transition_candidate" if confidence < 0.75 else "confirmed_transition"
    if weeks_in_regime <= 1:
        return "newly_confirmed"
    return "stable"


def _breadth_trend(pack: dict[str, Any]) -> str:
    evidence = (((pack.get("macro_signals") or {}).get("equity_leadership") or {}).get("evidence") or {})
    iwm_rs = _num(evidence.get("IWM_rs_vs_SPY_3m_pct"), 0.0)
    if iwm_rs >= 2:
        return "improving"
    if iwm_rs <= -2:
        return "weakening"
    return "mixed"


def _cross_asset_status(pack: dict[str, Any]) -> str:
    signals = pack.get("macro_signals") or {}
    duration = ((signals.get("duration") or {}).get("signal") or "").lower()
    hedge = ((signals.get("hedge_ballast") or {}).get("signal") or "").lower()
    equity = ((signals.get("equity_leadership") or {}).get("signal") or "").lower()

    negatives = sum(
        1
        for item in (duration, hedge, equity)
        if item in {"not_confirmed_as_tailwind", "under_review", "mixed"}
    )
    if negatives >= 2:
        return "mixed"
    if "narrow_ai_leadership" in equity and negatives <= 1:
        return "confirmed_but_narrow"
    return "diverging"


def update_regime_memory(pack: dict[str, Any], path: Path = REGIME_MEMORY_PATH) -> dict[str, Any]:
    regime = pack.get("regime") or {}
    current_regime = str(regime.get("current") or "Unknown")
    current_confidence = _num(regime.get("confidence"), 0.0)
    report_date = str(pack.get("report_date") or datetime.utcnow().date().isoformat())
    now = datetime.utcnow().isoformat() + "Z"

    previous = load_regime_memory(path)
    previous_regime = str(previous.get("current_regime") or regime.get("previous") or "Unknown")
    previous_confidence = previous.get("current_confidence")
    weeks_in_regime = int(previous.get("weeks_in_regime") or 0)

    regime_changed = previous_regime not in {"", "Unknown"} and previous_regime != current_regime
    if regime_changed:
        new_weeks = 1
        last_major_shift = report_date
        failed_rotation_count = int(previous.get("failed_rotation_count") or 0)
    else:
        new_weeks = weeks_in_regime + 1 if weeks_in_regime else 1
        last_major_shift = previous.get("last_major_shift") or report_date
        failed_rotation_count = int(previous.get("failed_rotation_count") or 0)

    memory = {
        "updated_at_utc": now,
        "report_date": report_date,
        "current_regime": current_regime,
        "prior_regime": previous_regime,
        "regime_changed_this_run": regime_changed,
        "weeks_in_regime": new_weeks,
        "transition_state": _transition_state(previous_regime, current_regime, new_weeks, current_confidence),
        "current_confidence": current_confidence,
        "previous_confidence": previous_confidence,
        "confidence_trend": _confidence_trend(_num(previous_confidence, None) if previous_confidence is not None else None, current_confidence),
        "breadth_trend": _breadth_trend(pack),
        "cross_asset_confirmation": _cross_asset_status(pack),
        "last_major_shift": last_major_shift,
        "failed_rotation_count": failed_rotation_count,
        "decision_rule": (
            "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad."
        ),
        "report_transfer": {
            "show_in_report": True,
            "max_lines": 2,
            "summary": None,
        },
    }

    memory["report_transfer"]["summary"] = regime_memory_summary(memory)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, indent=2, sort_keys=True), encoding="utf-8")
    return memory


def regime_memory_summary(memory: dict[str, Any]) -> str:
    regime = memory.get("current_regime", "Unknown")
    weeks = memory.get("weeks_in_regime", 1)
    transition = memory.get("transition_state", "stable")
    breadth = memory.get("breadth_trend", "mixed")
    cross = memory.get("cross_asset_confirmation", "mixed")
    return (
        f"{regime} has persisted for {weeks} run(s); transition state is {transition}, "
        f"breadth is {breadth}, and cross-asset confirmation is {cross}."
    )
