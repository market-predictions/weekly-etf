from __future__ import annotations

from typing import Any


def _number(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def executed_model_change_present(state: dict[str, Any]) -> bool:
    """Return True when the authoritative replay artifact records execution.

    Historical executed states may keep the immutable trade evidence under
    ``executed_model_changes`` rather than duplicating action/delta fields into
    every current position row. Either non-zero share delta or explicit executed
    action is sufficient evidence that the review is not a no-action run.
    """

    for row in state.get("executed_model_changes") or []:
        if not isinstance(row, dict):
            continue
        shares_delta = abs(
            _number(
                row.get("shares_delta")
                if row.get("shares_delta") is not None
                else row.get("shares_delta_this_run")
            )
        )
        action = str(
            row.get("action")
            or row.get("action_executed")
            or row.get("action_executed_this_run")
            or ""
        ).strip().lower()
        if shares_delta > 1e-9:
            return True
        if action not in {"", "none", "no change", "hold"}:
            return True
    return False
