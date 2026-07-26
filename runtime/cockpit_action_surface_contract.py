from __future__ import annotations

from typing import Any


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def proposed_trade_intents(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = state.get("trade_intents") or (
        state.get("rotation_plan") or {}
    ).get("trade_intents") or []
    if not isinstance(rows, list):
        return []
    return [
        dict(row)
        for row in rows
        if isinstance(row, dict)
        and _ticker(row.get("source_ticker"))
        and _ticker(row.get("destination_ticker"))
    ]


def action_surface(
    state: dict[str, Any], language: str, *, cockpit_module: Any
) -> tuple[str, str]:
    executed = cockpit_module._executed_actions(state)
    if executed:
        labels: list[str] = []
        details: list[str] = []
        for item in executed:
            normalized_action = str(item["action"]).lower()
            shares_delta = float(item["shares_delta"])
            if shares_delta < 0 or normalized_action in {
                "sell",
                "reduce",
                "reduced",
                "close",
                "closed",
            }:
                verb = "afgebouwd" if language == "nl" else "reduced"
            elif shares_delta > 0 or normalized_action in {
                "buy",
                "add",
                "added",
                "open",
                "opened",
            }:
                verb = "toegevoegd" if language == "nl" else "added"
            else:
                verb = "aangepast" if language == "nl" else "adjusted"
            labels.append(f"{item['ticker']} {verb}")
            details.append(
                f"{item['ticker']} "
                f"{cockpit_module._fmt_pct(float(item['previous_weight_pct']), language)} → "
                f"{cockpit_module._fmt_pct(float(item['current_weight_pct']), language)}"
            )
        return " · ".join(labels), "; ".join(details) + "."

    proposals = proposed_trade_intents(state)
    if proposals:
        details: list[str] = []
        for intent in proposals:
            source = _ticker(intent.get("source_ticker"))
            destination = _ticker(intent.get("destination_ticker"))
            source_delta = abs(_num(intent.get("delta_weight_pct")))
            destination_delta = abs(
                _num(
                    intent.get("destination_delta_weight_pct"),
                    source_delta,
                )
            )
            if language == "nl":
                details.append(
                    f"{source} -{source_delta:.2f}% NAV; "
                    f"{destination} +{destination_delta:.2f}% NAV"
                )
            else:
                details.append(
                    f"{source} -{source_delta:.2f}% NAV; "
                    f"{destination} +{destination_delta:.2f}% NAV"
                )
        if language == "nl":
            return (
                "Voorgesteld — niet uitgevoerd",
                "; ".join(details)
                + ". Geen transactie is uitgevoerd of verwerkt in de officiële portefeuillestaat.",
            )
        return (
            "Proposed — not executed",
            "; ".join(details)
            + ". No trade was executed or persisted in the official portfolio state.",
        )

    if language == "nl":
        return (
            "Geen wijziging voorgesteld of uitgevoerd",
            "Geen positie is geopend, gesloten, vergroot of verkleind; de huidige gewichten blijven ongewijzigd.",
        )
    return (
        "No change proposed or executed",
        "No position was opened, closed, increased, or reduced; current weights remain unchanged.",
    )


def install(cockpit_module: Any) -> Any:
    def _patched_action_surface(
        state: dict[str, Any], language: str
    ) -> tuple[str, str]:
        return action_surface(
            state, language, cockpit_module=cockpit_module
        )

    cockpit_module._action_surface = _patched_action_surface
    cockpit_module._proposal_aware_action_surface_installed = True
    return cockpit_module
