from __future__ import annotations

import re
from typing import Any


def _number(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def authoritative_execution_present(state: dict[str, Any]) -> bool:
    rows = state.get("executed_model_changes") or []
    if rows:
        for row in rows:
            if not isinstance(row, dict):
                continue
            if abs(_number(row.get("shares_delta"))) > 1e-9:
                return True
            action = str(row.get("action") or row.get("action_executed") or "").strip().lower()
            if action not in {"", "none", "hold", "no change"}:
                return True
    for row in state.get("positions") or []:
        if not isinstance(row, dict):
            continue
        if abs(_number(row.get("shares_delta_this_run"))) > 1e-9:
            return True
        action = str(row.get("action_executed_this_run") or "").strip().lower()
        if action not in {"", "none", "hold", "no change", "already reflected"}:
            return True
    return False


def remove_no_action_contradictions(text: str, state: dict[str, Any], language: str) -> str:
    """Rewrite only explicit no-action claims contradicted by execution evidence."""

    if not authoritative_execution_present(state):
        return text
    language = language.lower().strip()
    if language == "nl":
        replacements = (
            (r"\bgeen portefeuilleactie\b", "portefeuilleactie uitgevoerd en verwerkt"),
            (r"\bgeen modeltransactie uitgevoerd\b", "modeltransactie uitgevoerd en verwerkt"),
            (r"\bgeen wijzigingen in de portefeuille\b", "portefeuillewijzigingen uitgevoerd en verwerkt"),
        )
    elif language == "en":
        replacements = (
            (r"\bno portfolio action\b", "portfolio action executed and reflected"),
            (r"\bno model trade executed\b", "model trade executed and reflected"),
            (r"\bno changes to the portfolio\b", "portfolio changes executed and reflected"),
        )
    else:
        raise ValueError(f"Unsupported language: {language}")
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
