from __future__ import annotations

import re
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


def executed_changes(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = state.get("executed_model_changes") or []
    if not isinstance(rows, list):
        return []
    return [
        dict(row)
        for row in rows
        if isinstance(row, dict) and _ticker(row.get("ticker"))
    ]


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


def change_by_ticker(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _ticker(row.get("ticker")): row for row in executed_changes(state)
    }


def has_executed_changes(state: dict[str, Any]) -> bool:
    return bool(executed_changes(state))


def has_proposed_changes(state: dict[str, Any]) -> bool:
    return bool(proposed_trade_intents(state))


def _change_kind(change: dict[str, Any]) -> str:
    action = str(change.get("action") or "").strip().lower()
    delta = _num(change.get("shares_delta"))
    new_weight = _num(
        change.get("new_weight_pct"), _num(change.get("target_weight_pct"))
    )
    if action in {"buy", "increase", "add"} or delta > 0:
        return "add"
    if action in {"sell", "decrease", "reduce", "close"} or delta < 0:
        return "close" if new_weight <= 0.005 else "reduce"
    return "hold"


def position_action_code(
    position: dict[str, Any], state: dict[str, Any]
) -> str:
    symbol = _ticker(position.get("ticker"))
    change = change_by_ticker(state).get(symbol)
    if change:
        return f"{_change_kind(change)}_executed"
    return str(
        position.get("rotation_action_code")
        or position.get("suggested_action")
        or "hold"
    ).strip().lower()


def position_action_label_en(
    position: dict[str, Any], state: dict[str, Any]
) -> str:
    code = position_action_code(position, state)
    mapping = {
        "add_executed": "Add — executed",
        "reduce_executed": "Reduce — executed",
        "close_executed": "Close — executed",
        "replace_partial": "Replace partial",
        "replace_full": "Replace full",
        "hold_with_override": "Hold with override",
        "add_from_cash": "Add from cash",
        "hold": "Hold",
    }
    return mapping.get(code, code.replace("_", " ").title())


def position_action_label_nl(
    position: dict[str, Any], state: dict[str, Any]
) -> str:
    code = position_action_code(position, state)
    mapping = {
        "add_executed": "Toevoegen — uitgevoerd",
        "reduce_executed": "Verlagen — uitgevoerd",
        "close_executed": "Sluiten — uitgevoerd",
        "replace_partial": "Gedeeltelijk vervangen",
        "replace_full": "Volledig vervangen",
        "hold_with_override": "Aanhouden met override",
        "add_from_cash": "Toevoegen vanuit cash",
        "hold": "Aanhouden",
    }
    return mapping.get(code, code.replace("_", " "))


def action_buckets(state: dict[str, Any]) -> dict[str, list[str]]:
    buckets = {
        "add": [],
        "reduce": [],
        "close": [],
        "hold": [],
        "replaceable": [],
    }
    changes = change_by_ticker(state)
    for position in state.get("positions", []) or []:
        symbol = _ticker(position.get("ticker"))
        if not symbol:
            continue
        change = changes.get(symbol)
        if change:
            buckets[_change_kind(change)].append(symbol)
            continue
        buckets["hold"].append(symbol)
        suggested = str(position.get("suggested_action") or "").lower()
        better = str(position.get("better_alternative_exists") or "").lower()
        override = str(position.get("rotation_action_code") or "").lower()
        if (
            better == "yes"
            or "review" in suggested
            or override == "hold_with_override"
        ):
            buckets["replaceable"].append(symbol)
    return buckets


def _join(values: list[str], none: str) -> str:
    return ", ".join(values) if values else none


def executed_rotation_summary_en(state: dict[str, Any]) -> str:
    changes = executed_changes(state)
    if not changes:
        return "No guarded model mutation was executed this run."
    parts: list[str] = []
    for change in changes:
        symbol = _ticker(change.get("ticker"))
        kind = _change_kind(change)
        previous = _num(change.get("previous_weight_pct"))
        new = _num(
            change.get("new_weight_pct"),
            _num(change.get("target_weight_pct")),
        )
        verb = {
            "add": "added",
            "reduce": "reduced",
            "close": "closed",
        }.get(kind, "updated")
        if kind == "add":
            parts.append(f"{verb} {symbol} at {new:.2f}% of NAV")
        else:
            parts.append(
                f"{verb} {symbol} from {previous:.2f}% to {new:.2f}% of NAV"
            )
    return (
        "Guarded model rotation executed and persisted: "
        + "; ".join(parts)
        + "."
    )


def executed_rotation_summary_nl(state: dict[str, Any]) -> str:
    changes = executed_changes(state)
    if not changes:
        return "Deze run is geen bewaakte modelmutatie uitgevoerd."
    parts: list[str] = []
    for change in changes:
        symbol = _ticker(change.get("ticker"))
        kind = _change_kind(change)
        previous = _num(change.get("previous_weight_pct"))
        new = _num(
            change.get("new_weight_pct"),
            _num(change.get("target_weight_pct")),
        )
        if kind == "add":
            parts.append(f"{symbol} toegevoegd op {new:.2f}% van de NAV")
        elif kind == "close":
            parts.append(
                f"{symbol} gesloten van {previous:.2f}% naar {new:.2f}% van de NAV"
            )
        else:
            parts.append(
                f"{symbol} verlaagd van {previous:.2f}% naar {new:.2f}% van de NAV"
            )
    return (
        "Bewaakte modelrotatie uitgevoerd en verwerkt: "
        + "; ".join(parts)
        + "."
    )


def proposed_rotation_summary_en(state: dict[str, Any]) -> str:
    intents = proposed_trade_intents(state)
    if not intents:
        return "No portfolio change is proposed or executed this week."
    parts: list[str] = []
    for intent in intents:
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        source_delta = abs(_num(intent.get("delta_weight_pct")))
        destination_delta = abs(
            _num(intent.get("destination_delta_weight_pct"), source_delta)
        )
        parts.append(
            f"reduce {source} by {source_delta:.2f}% of NAV and allocate "
            f"{destination_delta:.2f}% to {destination}"
        )
    return "Proposed — not executed: " + "; ".join(parts) + "."


def proposed_rotation_summary_nl(state: dict[str, Any]) -> str:
    intents = proposed_trade_intents(state)
    if not intents:
        return "Deze week is geen portefeuillewijziging voorgesteld of uitgevoerd."
    parts: list[str] = []
    for intent in intents:
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        source_delta = abs(_num(intent.get("delta_weight_pct")))
        destination_delta = abs(
            _num(intent.get("destination_delta_weight_pct"), source_delta)
        )
        parts.append(
            f"verlaag {source} met {source_delta:.2f}% van de NAV en alloceer "
            f"{destination_delta:.2f}% naar {destination}"
        )
    return "Voorgesteld — niet uitgevoerd: " + "; ".join(parts) + "."


def main_takeaway_en(state: dict[str, Any]) -> str:
    if has_executed_changes(state):
        buckets = action_buckets(state)
        return (
            f"The portfolio executed one controlled rotation: reduced "
            f"{_join(buckets['reduce'] + buckets['close'], 'the funding source')} "
            f"and added {_join(buckets['add'], 'the selected destination')}; "
            "further changes remain evidence- and churn-gated."
        )
    if has_proposed_changes(state):
        return proposed_rotation_summary_en(state)
    return (
        "No portfolio change is proposed or executed this week; SMH remains "
        "the best-supported core exposure, while fresh capital and replacement "
        "decisions remain price-, relative-strength- and portfolio-discipline gated."
    )


def main_takeaway_nl(state: dict[str, Any]) -> str:
    if has_executed_changes(state):
        buckets = action_buckets(state)
        return (
            f"De portefeuille voerde één gecontroleerde rotatie uit: "
            f"{_join(buckets['reduce'] + buckets['close'], 'de financieringsbron')} "
            f"werd verlaagd en {_join(buckets['add'], 'de gekozen bestemming')} "
            "werd toegevoegd; verdere wijzigingen blijven bewijs- en churnbegrensd."
        )
    if has_proposed_changes(state):
        return proposed_rotation_summary_nl(state)
    return (
        "Deze week is geen portefeuillewijziging voorgesteld of uitgevoerd; SMH "
        "blijft de best onderbouwde kernblootstelling en nieuw kapitaal blijft "
        "afhankelijk van prijs-, relatieve-sterkte- en portefeuillediscipline."
    )


def decision_cockpit_en(state: dict[str, Any]) -> str:
    buckets = action_buckets(state)
    if has_executed_changes(state):
        this_week = executed_rotation_summary_en(state)
        fresh_capital = (
            "no additional deployment after the completed major rotation unless "
            "a future run clears all decision conditions."
        )
    elif has_proposed_changes(state):
        this_week = proposed_rotation_summary_en(state)
        fresh_capital = (
            "the stated rotation is proposal-only; no trade is executed until "
            "execution authority and portfolio-state persistence are recorded."
        )
    else:
        this_week = "No portfolio change is proposed or executed this week."
        fresh_capital = (
            "no new deployment is proposed while current position, concentration "
            "and funding constraints remain active."
        )
    return "\n".join(
        [
            "### Decision cockpit",
            "",
            f"- **This week:** {this_week}",
            "- **Main active risk:** SMH concentration remains above the soft position cap.",
            f"- **Main active reviews:** {_join(buckets['replaceable'], 'none beyond standard monitoring')} remain under explicit review.",
            "- **Next action trigger:** another mutation requires a confirmed relative-strength edge, clean pricing basis, thesis fit, a releasable funding source and available portfolio capacity.",
            f"- **Fresh capital:** {fresh_capital}",
        ]
    )


def decision_cockpit_nl(state: dict[str, Any]) -> str:
    buckets = action_buckets(state)
    if has_executed_changes(state):
        this_week = executed_rotation_summary_nl(state)
        fresh_capital = (
            "geen verdere inzet na de voltooide hoofdrotatie totdat een toekomstige "
            "run alle beslisvoorwaarden vrijgeeft."
        )
    elif has_proposed_changes(state):
        this_week = proposed_rotation_summary_nl(state)
        fresh_capital = (
            "de genoemde rotatie is uitsluitend een voorstel; er wordt niets "
            "uitgevoerd totdat uitvoeringsbevoegdheid en verwerking in de "
            "portefeuillestaat zijn vastgelegd."
        )
    else:
        this_week = (
            "Deze week is geen portefeuillewijziging voorgesteld of uitgevoerd."
        )
        fresh_capital = (
            "geen nieuwe inzet voorgesteld zolang positie-, concentratie- en "
            "financieringsbeperkingen actief blijven."
        )
    return "\n".join(
        [
            "### Besliscockpit",
            "",
            f"- **Deze week:** {this_week}",
            "- **Belangrijkste actieve risico:** SMH-concentratie blijft boven de zachte positielimiet.",
            f"- **Belangrijkste actieve reviews:** {_join(buckets['replaceable'], 'geen buiten de standaardmonitoring')} blijven expliciet onder herbeoordeling.",
            "- **Trigger voor volgende actie:** een volgende mutatie vereist bevestigde relatieve-sterktevoorsprong, schone prijsbasis, aansluiting op de thesis, een vrij te maken financieringsbron en beschikbare portefeuillecapaciteit.",
            f"- **Vers kapitaal:** {fresh_capital}",
        ]
    )


def rotation_plan_table_en(state: dict[str, Any]) -> str:
    buckets = action_buckets(state)
    return "\n".join(
        [
            "| Close | Reduce | Hold | Add | Replaceable review |",
            "|---|---|---|---|---|",
            f"| {_join(buckets['close'], 'None')} | {_join(buckets['reduce'], 'None')} | {_join(buckets['hold'], 'None')} | {_join(buckets['add'], 'None')} | {_join(buckets['replaceable'], 'None')} |",
        ]
    )


def rotation_plan_table_nl(state: dict[str, Any]) -> str:
    buckets = action_buckets(state)
    return "\n".join(
        [
            "| Sluiten | Verlagen | Aanhouden | Toevoegen | Vervangingsreview |",
            "|---|---|---|---|---|",
            f"| {_join(buckets['close'], 'Geen')} | {_join(buckets['reduce'], 'Geen')} | {_join(buckets['hold'], 'Geen')} | {_join(buckets['add'], 'Geen')} | {_join(buckets['replaceable'], 'Geen')} |",
        ]
    )


def _section(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    if start_index == -1:
        return ""
    end_index = text.find(end, start_index + len(start))
    return text[start_index:] if end_index == -1 else text[start_index:end_index]


def _contains_symbol(value: str, symbol: str) -> bool:
    return bool(
        re.search(
            rf"(?<![A-Z0-9]){re.escape(symbol)}(?![A-Z0-9])", value
        )
    )


def _markdown_table_mapping(section: str) -> dict[str, str]:
    table_lines = [line for line in section.splitlines() if line.startswith("|")]
    if len(table_lines) < 3:
        return {}
    headers = [
        cell.strip() for cell in table_lines[0].strip().strip("|").split("|")
    ]
    values = [
        cell.strip() for cell in table_lines[2].strip().strip("|").split("|")
    ]
    return dict(zip(headers, values))


def _section2_action_has_symbol(
    section: str, *, language: str, kind: str, symbol: str
) -> bool:
    if language == "nl":
        labels = {
            "add": "Toevoegen",
            "reduce": "Verlagen",
            "close": "Sluiten",
        }
        label = labels[kind]
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            cells = [
                cell.strip()
                for cell in line.strip().strip("|").split("|")
            ]
            if (
                len(cells) >= 2
                and cells[0] == label
                and _contains_symbol(cells[1], symbol)
            ):
                return True
        return False
    labels = {
        "add": "### Add — executed",
        "reduce": "### Reduce — executed",
        "close": "### Close — executed",
    }
    label = labels[kind]
    start = section.find(label)
    if start == -1:
        return False
    body_start = start + len(label)
    next_heading = section.find("\n### ", body_start)
    block = (
        section[body_start:]
        if next_heading == -1
        else section[body_start:next_heading]
    )
    return _contains_symbol(block, symbol)


def _section12_action_has_symbol(
    section: str, *, language: str, kind: str, symbol: str
) -> bool:
    mapping = _markdown_table_mapping(section)
    labels = (
        {"add": "Toevoegen", "reduce": "Verlagen", "close": "Sluiten"}
        if language == "nl"
        else {"add": "Add", "reduce": "Reduce", "close": "Close"}
    )
    return _contains_symbol(mapping.get(labels[kind], ""), symbol)


def _final_action_row(section: str, symbol: str) -> str:
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        first_cell = line.strip().strip("|").split("|", 1)[0]
        if _contains_symbol(first_cell, symbol):
            return line
    return ""


def _validate_proposed_action_consistency(
    text: str, state: dict[str, Any], *, language: str
) -> list[str]:
    intents = proposed_trade_intents(state)
    if not intents or has_executed_changes(state):
        return []

    errors: list[str] = []
    lower = text.lower()
    forbidden = ["no portfolio action", "geen portefeuilleactie"]
    for phrase in forbidden:
        if phrase in lower:
            errors.append(f"forbidden_no_action_phrase:{phrase}")

    if language == "nl":
        section1 = _section(text, "## 1. Kernsamenvatting", "## 2. Portefeuille-acties")
        section2 = _section(text, "## 2. Portefeuille-acties", "## 3. Regime-dashboard")
        section12 = _section(text, "## 12. Rotatieplan portefeuille", "## 13. Definitieve actietabel")
        section13 = _section(text, "## 13. Definitieve actietabel", "## 14.")
        section14 = _section(text, "## 14.", "## 15.")
        proposal_marker = "voorgesteld"
    else:
        section1 = _section(text, "## 1. Executive Summary", "## 2. Portfolio Action Snapshot")
        section2 = _section(text, "## 2. Portfolio Action Snapshot", "## 3. Regime Dashboard")
        section12 = _section(text, "## 12. Portfolio Rotation Plan", "## 13. Final Action Table")
        section13 = _section(text, "## 13. Final Action Table", "## 14.")
        section14 = _section(text, "## 14.", "## 15.")
        proposal_marker = "proposed"

    if proposal_marker not in section1.lower():
        errors.append("front_page_proposal_marker_missing")

    for intent in intents:
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        pair = f"{source}->{destination}"
        for name, section in (
            ("front_page", section1),
            ("action_snapshot", section2),
            ("rotation_plan", section12),
            ("position_changes", section14),
        ):
            if not _contains_symbol(section, source) or not _contains_symbol(
                section, destination
            ):
                errors.append(f"proposed_{name}_mismatch:{pair}")
        if not _final_action_row(section13, source):
            errors.append(f"proposed_final_action_source_missing:{source}")
        if not _final_action_row(section13, destination):
            errors.append(
                f"proposed_final_action_destination_missing:{destination}"
            )
    return errors


def validate_post_execution_report_consistency(
    text: str, state: dict[str, Any], *, language: str
) -> None:
    changes = executed_changes(state)
    proposal_errors = _validate_proposed_action_consistency(
        text, state, language=language
    )
    if not changes:
        if proposal_errors:
            raise RuntimeError(
                "ETF proposed-action report consistency failed: "
                + "; ".join(proposal_errors)
            )
        return

    errors: list[str] = list(proposal_errors)
    lower = text.lower()
    forbidden = ["no portfolio action", "geen portefeuilleactie"]
    for phrase in forbidden:
        if phrase in lower:
            errors.append(f"forbidden_no_action_phrase:{phrase}")

    if language == "nl":
        section2 = _section(
            text, "## 2. Portefeuille-acties", "## 3. Regime-dashboard"
        )
        section12 = _section(
            text,
            "## 12. Rotatieplan portefeuille",
            "## 13. Definitieve actietabel",
        )
        section13 = _section(text, "## 13. Definitieve actietabel", "## 14.")
        add_label, reduce_label, close_label = (
            "Toevoegen — uitgevoerd",
            "Verlagen — uitgevoerd",
            "Sluiten — uitgevoerd",
        )
    else:
        section2 = _section(
            text,
            "## 2. Portfolio Action Snapshot",
            "## 3. Regime Dashboard",
        )
        section12 = _section(
            text,
            "## 12. Portfolio Rotation Plan",
            "## 13. Final Action Table",
        )
        section13 = _section(text, "## 13. Final Action Table", "## 14.")
        add_label, reduce_label, close_label = (
            "Add — executed",
            "Reduce — executed",
            "Close — executed",
        )

    if not section2:
        errors.append("action_snapshot_section_missing")
    if not section12:
        errors.append("rotation_plan_section_missing")
    if not section13:
        errors.append("final_action_section_missing")

    for change in changes:
        symbol = _ticker(change.get("ticker"))
        kind = _change_kind(change)
        expected_label = {
            "add": add_label,
            "reduce": reduce_label,
            "close": close_label,
        }[kind]
        if not _section2_action_has_symbol(
            section2, language=language, kind=kind, symbol=symbol
        ):
            errors.append(f"action_snapshot_mismatch:{symbol}:{kind}")
        if not _section12_action_has_symbol(
            section12, language=language, kind=kind, symbol=symbol
        ):
            errors.append(f"rotation_plan_mismatch:{symbol}:{kind}")
        row = _final_action_row(section13, symbol)
        if not row or expected_label not in row:
            errors.append(f"final_action_mismatch:{symbol}:{expected_label}")

    if errors:
        raise RuntimeError(
            "ETF post-execution report consistency failed: "
            + "; ".join(errors)
        )
