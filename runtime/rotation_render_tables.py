from __future__ import annotations

from typing import Any


WEIGHT_BASIS_NOTE_EN = (
    "Weight basis note: action-table weights are model/action weights; current-holdings weights are live "
    "market-value weights including cash. Small differences can occur when cash, rounding or override handling is included."
)
WEIGHT_BASIS_NOTE_NL = (
    "Toelichting gewichtsbasis: gewichten in de actietabel zijn model-/actiegewichten; gewichten bij huidige posities zijn actuele "
    "marktwaardegewichten inclusief cash. Kleine verschillen kunnen ontstaan door cash, afronding of override-verwerking."
)
HOLD_OVERRIDE_NOTE_EN = (
    "Hold-with-override note: The model would normally force reduce/replace review, but the position is too small or "
    "operationally impractical to trade this run."
)
HOLD_OVERRIDE_NOTE_NL = (
    "Override-toelichting: Het model dwingt normaal een verklein-/vervangingsreview af, maar de positie is deze run te klein "
    "of operationeel niet zinvol om te verhandelen."
)


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw if raw else fallback


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def _short(value: Any, fallback: str = "", max_len: int = 180) -> str:
    raw = _text(value, fallback)
    return raw if len(raw) <= max_len else raw[: max_len - 1].rstrip() + "…"


def has_rotation_plan(state: dict[str, Any]) -> bool:
    return bool(state.get("rotation_decisions") or state.get("trade_intents") or (state.get("rotation_plan") or {}).get("rotation_decisions"))


def _decisions(state: dict[str, Any]) -> list[dict[str, Any]]:
    if state.get("rotation_decisions"):
        return list(state.get("rotation_decisions") or [])
    return list((state.get("rotation_plan") or {}).get("rotation_decisions") or [])


def _target_weights(state: dict[str, Any]) -> dict[str, float]:
    rows = state.get("target_weights") or (state.get("rotation_plan") or {}).get("target_weights") or []
    out: dict[str, float] = {}
    for row in rows:
        ticker = _ticker(row.get("ticker"))
        try:
            out[ticker] = float(row.get("target_weight_pct"))
        except (TypeError, ValueError):
            continue
    return out


def _trade_intents(state: dict[str, Any]) -> list[dict[str, Any]]:
    if state.get("trade_intents"):
        return list(state.get("trade_intents") or [])
    return list((state.get("rotation_plan") or {}).get("trade_intents") or [])


def _decision_by_ticker(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): row for row in _decisions(state) if _ticker(row.get("ticker"))}


REASON_TEXT = {
    "fresh_cash_smaller_or_review": "Fresh capital only after review or at smaller size",
    "failed_fresh_cash_test": "Position does not pass the fresh-capital test",
    "replaceable_status": "Position is under replacement review",
    "review_age_ge_2": "Review has persisted for multiple report cycles",
    "review_age_ge_3": "Review has persisted for several report cycles",
    "negative_pnl_gt_5": "Position has become a material performance drag",
    "negative_pnl_gt_10": "Position has become a large performance drag",
    "better_alternative_exists": "A stronger alternative is available for comparison",
    "negative_contribution": "Portfolio contribution is negative",
    "role_impaired": "Role under review",
    "role_failed": "Role no longer justifies current capital",
    "factor_or_concentration_flag": "Concentration or factor-overlap discipline is active",
    "destination from trade_intents": "Proposed destination from the rotation plan",
    "destination_score": "Destination score confirmed by the rotation engine",
}

REASON_TEXT_NL = {
    "fresh_cash_smaller_or_review": "Vers kapitaal alleen kleiner of na herbeoordeling inzetten",
    "failed_fresh_cash_test": "Positie voldoet niet aan de vers-kapitaaltoets",
    "replaceable_status": "Positie staat onder vervangingsreview",
    "review_age_ge_2": "Review loopt al meerdere rapportcycli",
    "review_age_ge_3": "Review loopt al meerdere rapportcycli",
    "negative_pnl_gt_5": "Positie drukt materieel op het rendement",
    "negative_pnl_gt_10": "Positie drukt zwaar op het rendement",
    "better_alternative_exists": "Sterker alternatief is beschikbaar voor vergelijking",
    "negative_contribution": "Portefeuillebĳdrage is negatief",
    "role_impaired": "Rol onder herbeoordeling",
    "role_failed": "Rol rechtvaardigt huidige allocatie niet meer",
    "factor_or_concentration_flag": "Concentratie- of factoroverlapdiscipline is actief",
    "destination from trade_intents": "Voorgestelde bestemming uit het rotatieplan",
    "destination_score": "Bestemmingsscore bevestigd door de rotatie-engine",
}

OVERRIDE_TEXT = {
    "churn_budget_used": "Rotation budget for this run is already used",
    "no_fundable_destination": "No destination cleared the funding constraints",
    "min_trade_size_not_met": "Minimum trade size was not met",
    "insufficient_confirming_window": "More confirmation is required before action",
    "candidate_not_valuation_grade": "Candidate pricing quality is not high enough",
    "max_position_cap_hit": "Maximum position size would be breached",
    "role_preservation_required": "Role preservation constraint blocks rotation",
    "pricing_lineage_insufficient": "Pricing lineage is not sufficient for action",
    "liquidity_constraint": "Liquidity constraint blocks action",
    "portfolio_constraint_blocked": "Portfolio constraint blocks action",
}

OVERRIDE_TEXT_NL = {
    "churn_budget_used": "Rotatiebudget voor deze run is al gebruikt",
    "no_fundable_destination": "Geen bestemming voldoet aan de allocatie-eisen",
    "min_trade_size_not_met": "Minimale transactiegrootte is niet gehaald",
    "insufficient_confirming_window": "Meer bevestiging is nodig vóór actie",
    "candidate_not_valuation_grade": "Koerskwaliteit van alternatief is onvoldoende",
    "max_position_cap_hit": "Maximale positiegrootte zou worden overschreden",
    "role_preservation_required": "Portefeuillerol moet behouden blijven",
    "pricing_lineage_insufficient": "Prijsherkomst is onvoldoende voor actie",
    "liquidity_constraint": "Liquiditeitsvoorwaarde blokkeert actie",
    "portfolio_constraint_blocked": "Portefeuillerandvoorwaarde blokkeert actie",
}


def _humanize_reason_code(code: Any, *, language: str = "en") -> str:
    raw = _text(code)
    if not raw:
        return ""
    table = REASON_TEXT_NL if language == "nl" else REASON_TEXT
    if raw.startswith("destination_score"):
        return table["destination_score"]
    return table.get(raw, raw.replace("_", " ").capitalize())


def _reason_text(decision: dict[str, Any], *, language: str = "en") -> str:
    reasons = decision.get("reason_codes") or []
    if isinstance(reasons, list):
        human = [_humanize_reason_code(r, language=language) for r in reasons[:4]]
        return "; ".join(r for r in human if r)
    return _humanize_reason_code(reasons, language=language)


def _override_text(decision: dict[str, Any], *, language: str = "en") -> str:
    status = _text(decision.get("override_status"), "none")
    reason = _text(decision.get("override_reason_code"))
    if status == "none":
        return "Nee" if language == "nl" else "No"
    table = OVERRIDE_TEXT_NL if language == "nl" else OVERRIDE_TEXT
    human_reason = table.get(reason, reason.replace("_", " ").capitalize() if reason else "")
    prefix = "Systeemoverride" if language == "nl" and status == "engine" else "Operatoroverride" if language == "nl" else "System override" if status == "engine" else "Operator override"
    return f"{prefix}: {human_reason}" if human_reason else prefix


def action_label(action_code: Any) -> str:
    mapping = {
        "hold": "Hold",
        "hold_with_override": "Hold with override",
        "reduce": "Reduce",
        "replace_partial": "Partial replacement",
        "replace_full": "Full replacement",
        "close": "Close",
        "add_from_cash": "Add from cash",
    }
    return mapping.get(_text(action_code), _text(action_code, "Hold"))


def action_label_nl(action_code: Any) -> str:
    mapping = {
        "hold": "Aanhouden",
        "hold_with_override": "Aanhouden met onderbouwde override",
        "reduce": "Verlagen",
        "replace_partial": "Gedeeltelijk vervangen",
        "replace_full": "Volledig vervangen",
        "close": "Sluiten",
        "add_from_cash": "Toevoegen vanuit cash",
    }
    return mapping.get(_text(action_code), _text(action_code, "Aanhouden"))


def final_action_table_from_rotation(state: dict[str, Any], etf_names: dict[str, str]) -> str:
    decisions = _decision_by_ticker(state)
    targets = _target_weights(state)
    lines = [
        WEIGHT_BASIS_NOTE_EN,
        "",
        HOLD_OVERRIDE_NOTE_EN,
        "",
        "| Ticker | ETF | Current weight | Target weight | Delta weight | Action | Capital destination | Release score | Decision rationale | Override status |",
        "|---|---|---:|---:|---:|---|---|---:|---|---|",
    ]
    for p in state.get("positions", []) or []:
        ticker = _ticker(p.get("ticker"))
        decision = decisions.get(ticker, {})
        current = p.get("previous_weight_pct") or p.get("current_weight_pct") or 0.0
        target = targets.get(ticker, decision.get("target_weight_pct", current))
        try:
            delta = float(target) - float(current)
        except (TypeError, ValueError):
            delta = 0.0
        lines.append(
            f"| {ticker} | {etf_names.get(ticker, ticker)} | {_f2(current)} | {_f2(target)} | {_f2(delta)} | "
            f"{action_label(decision.get('action_code'))} | {_text(decision.get('destination_ticker'), '-')} | "
            f"{_f2(decision.get('release_score'))} | {_short(_reason_text(decision, language='en'), '-')} | {_override_text(decision, language='en')} |"
        )
    for ticker, target in sorted(targets.items()):
        if ticker and not any(_ticker(p.get("ticker")) == ticker for p in state.get("positions", []) or []):
            lines.append(f"| {ticker} | {etf_names.get(ticker, ticker)} | 0.00 | {_f2(target)} | {_f2(target)} | Add from rotation | - | - | Proposed destination from the rotation plan | No |")
    return "\n".join(lines)


def final_action_table_from_rotation_nl(state: dict[str, Any], etf_names: dict[str, str]) -> str:
    decisions = _decision_by_ticker(state)
    targets = _target_weights(state)
    lines = [
        WEIGHT_BASIS_NOTE_NL,
        "",
        HOLD_OVERRIDE_NOTE_NL,
        "",
        "| Ticker | ETF | Huidig gewicht | Doelgewicht | Delta gewicht | Actie | Kapitaalbestemming | Vrijmaakscore | Toelichting | Override-status |",
        "|---|---|---:|---:|---:|---|---|---:|---|---|",
    ]
    for p in state.get("positions", []) or []:
        t = _ticker(p.get("ticker"))
        decision = decisions.get(t, {})
        current = p.get("previous_weight_pct") or p.get("current_weight_pct") or 0.0
        target = targets.get(t, decision.get("target_weight_pct", current))
        try:
            delta = float(target) - float(current)
        except (TypeError, ValueError):
            delta = 0.0
        lines.append(
            f"| {t} | {etf_names.get(t, t)} | {_f2(current)} | {_f2(target)} | {_f2(delta)} | "
            f"{action_label_nl(decision.get('action_code'))} | {_text(decision.get('destination_ticker'), '-')} | "
            f"{_f2(decision.get('release_score'))} | {_short(_reason_text(decision, language='nl'), '-')} | {_override_text(decision, language='nl')} |"
        )
    for t, target in sorted(targets.items()):
        if t and not any(_ticker(p.get("ticker")) == t for p in state.get("positions", []) or []):
            lines.append(f"| {t} | {etf_names.get(t, t)} | 0.00 | {_f2(target)} | {_f2(target)} | Toevoegen uit rotatie | - | - | Voorgestelde bestemming uit het rotatieplan | Nee |")
    return "\n".join(lines)


def position_changes_table_from_rotation(state: dict[str, Any]) -> str:
    trades = _trade_intents(state)
    if not trades:
        return "\n".join([
            "| Source | Destination | Source delta % | Destination delta % | Estimated notional EUR | Intent status | Rationale |",
            "|---|---|---:|---:|---:|---|---|",
            "| None | None | 0.00 | 0.00 | 0.00 | No proposed rotation | No actionable rotation proposal was generated this run. |",
        ])
    lines = [
        "| Source | Destination | Source delta % | Destination delta % | Estimated notional EUR | Intent status | Rationale |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for trade in trades:
        lines.append(
            f"| {_ticker(trade.get('source_ticker'))} | {_ticker(trade.get('destination_ticker'))} | "
            f"{_f2(trade.get('delta_weight_pct'))} | {_f2(trade.get('destination_delta_weight_pct'))} | {_f2(trade.get('estimated_notional_eur'))} | "
            f"{_short(trade.get('intent_status'), 'proposed')} | {_short(trade.get('rationale'), '-')} |"
        )
    return "\n".join(lines)


def position_changes_table_from_rotation_nl(state: dict[str, Any]) -> str:
    trades = _trade_intents(state)
    if not trades:
        return "\n".join([
            "| Bron | Bestemming | Delta bron % | Delta bestemming % | Geschatte waarde EUR | Intentiestatus | Toelichting |",
            "|---|---|---:|---:|---:|---|---|",
            "| Geen | Geen | 0.00 | 0.00 | 0.00 | Geen voorgestelde rotatie | Deze run is geen rotatie voorgesteld. |",
        ])
    lines = [
        "| Bron | Bestemming | Delta bron % | Delta bestemming % | Geschatte waarde EUR | Intentiestatus | Toelichting |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for trade in trades:
        lines.append(
            f"| {_ticker(trade.get('source_ticker'))} | {_ticker(trade.get('destination_ticker'))} | "
            f"{_f2(trade.get('delta_weight_pct'))} | {_f2(trade.get('destination_delta_weight_pct'))} | {_f2(trade.get('estimated_notional_eur'))} | "
            f"{_short(trade.get('intent_status'), 'voorgesteld')} | {_short(trade.get('rationale'), '-')} |"
        )
    return "\n".join(lines)
