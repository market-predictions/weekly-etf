from __future__ import annotations

from typing import Any


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


def _short(value: Any, fallback: str = "", max_len: int = 160) -> str:
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


def action_label(action_code: Any) -> str:
    mapping = {
        "hold": "Hold",
        "hold_with_override": "Hold with override",
        "reduce": "Reduce",
        "replace_partial": "Replace partial",
        "replace_full": "Replace full",
        "close": "Close",
        "add_from_cash": "Add from cash",
    }
    return mapping.get(_text(action_code), _text(action_code, "Hold"))


def action_label_nl(action_code: Any) -> str:
    mapping = {
        "hold": "Aanhouden",
        "hold_with_override": "Aanhouden met override",
        "reduce": "Verlagen",
        "replace_partial": "Gedeeltelijk vervangen",
        "replace_full": "Volledig vervangen",
        "close": "Sluiten",
        "add_from_cash": "Toevoegen vanuit cash",
    }
    return mapping.get(_text(action_code), _text(action_code, "Aanhouden"))


def _reason_text(decision: dict[str, Any]) -> str:
    reasons = decision.get("reason_codes") or []
    if isinstance(reasons, list):
        return ", ".join(str(r) for r in reasons[:4])
    return _text(reasons)


def _override_text(decision: dict[str, Any]) -> str:
    status = _text(decision.get("override_status"), "none")
    reason = _text(decision.get("override_reason_code"))
    if status == "none":
        return "No"
    return f"{status}: {reason}" if reason else status


def _override_text_nl(decision: dict[str, Any]) -> str:
    status = _text(decision.get("override_status"), "none")
    reason = _text(decision.get("override_reason_code"))
    if status == "none":
        return "Nee"
    prefix = "Engine" if status == "engine" else "Operator"
    return f"{prefix}: {reason}" if reason else prefix


def final_action_table_from_rotation(state: dict[str, Any], etf_names: dict[str, str]) -> str:
    decisions = _decision_by_ticker(state)
    targets = _target_weights(state)
    lines = [
        "| Ticker | ETF | Current weight | Target weight | Delta weight | Action code | Capital destination | Release score | Reason codes | Override? |",
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
            f"{_f2(decision.get('release_score'))} | {_short(_reason_text(decision), '-')} | {_override_text(decision)} |"
        )
    for ticker, target in sorted(targets.items()):
        if ticker and not any(_ticker(p.get("ticker")) == ticker for p in state.get("positions", []) or []):
            decision = next((d for d in decisions.values() if _ticker(d.get("destination_ticker")) == ticker), {})
            lines.append(f"| {ticker} | {etf_names.get(ticker, ticker)} | 0.00 | {_f2(target)} | {_f2(target)} | Add from rotation | - | - | destination from trade_intents | No |")
    return "\n".join(lines)


def final_action_table_from_rotation_nl(state: dict[str, Any], etf_names: dict[str, str]) -> str:
    decisions = _decision_by_ticker(state)
    targets = _target_weights(state)
    lines = [
        "| Ticker | ETF | Huidig gewicht | Doelgewicht | Delta gewicht | Actiecode | Kapitaalbestemming | Vrijmaakscores | Redencodes | Override? |",
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
            f"{_f2(decision.get('release_score'))} | {_short(_reason_text(decision), '-')} | {_override_text_nl(decision)} |"
        )
    for t, target in sorted(targets.items()):
        if t and not any(_ticker(p.get("ticker")) == t for p in state.get("positions", []) or []):
            lines.append(f"| {t} | {etf_names.get(t, t)} | 0.00 | {_f2(target)} | {_f2(target)} | Toevoegen uit rotatie | - | - | bestemming uit trade_intents | Nee |")
    return "\n".join(lines)


def position_changes_table_from_rotation(state: dict[str, Any]) -> str:
    trades = _trade_intents(state)
    if not trades:
        return "\n".join([
            "| Source | Destination | Source delta % | Destination delta % | Estimated notional EUR | Action | Reason |",
            "|---|---|---:|---:|---:|---|---|",
            "| None | None | 0.00 | 0.00 | 0.00 | No rotation trade intent | Rotation engine produced no executable trade intent. |",
        ])
    lines = [
        "| Source | Destination | Source delta % | Destination delta % | Estimated notional EUR | Action | Reason |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for trade in trades:
        reasons = trade.get("reason_codes") or []
        if isinstance(reasons, list):
            reason = ", ".join(str(r) for r in reasons[:4])
        else:
            reason = _text(reasons)
        lines.append(
            f"| {_ticker(trade.get('source_ticker'))} | {_ticker(trade.get('destination_ticker')) or 'CASH'} | "
            f"{_f2(trade.get('delta_weight_pct'))} | {_f2(trade.get('destination_delta_weight_pct'))} | "
            f"{_f2(trade.get('estimated_notional_eur'))} | {action_label(trade.get('action_code'))} | {_short(reason, '-')} |"
        )
    return "\n".join(lines)


def position_changes_table_from_rotation_nl(state: dict[str, Any]) -> str:
    trades = _trade_intents(state)
    if not trades:
        return "\n".join([
            "| Bron | Bestemming | Delta bron % | Delta bestemming % | Geschatte waarde EUR | Actie | Reden |",
            "|---|---|---:|---:|---:|---|---|",
            "| Geen | Geen | 0.00 | 0.00 | 0.00 | Geen rotatie-intentie | De rotatie-engine leverde geen uitvoerbare trade-intentie op. |",
        ])
    lines = [
        "| Bron | Bestemming | Delta bron % | Delta bestemming % | Geschatte waarde EUR | Actie | Reden |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for trade in trades:
        reasons = trade.get("reason_codes") or []
        reason = ", ".join(str(r) for r in reasons[:4]) if isinstance(reasons, list) else _text(reasons)
        lines.append(
            f"| {_ticker(trade.get('source_ticker'))} | {_ticker(trade.get('destination_ticker')) or 'CASH'} | "
            f"{_f2(trade.get('delta_weight_pct'))} | {_f2(trade.get('destination_delta_weight_pct'))} | "
            f"{_f2(trade.get('estimated_notional_eur'))} | {action_label_nl(trade.get('action_code'))} | {_short(reason, '-')} |"
        )
    return "\n".join(lines)


def rotation_plan_summary_from_rotation(state: dict[str, Any]) -> str:
    decisions = _decisions(state)
    buckets = {"Close": [], "Reduce": [], "Hold": [], "Add": [], "Replace": [], "Override": []}
    for row in decisions:
        ticker = _ticker(row.get("ticker"))
        action = _text(row.get("action_code"))
        if action == "close":
            buckets["Close"].append(ticker)
        elif action == "reduce":
            buckets["Reduce"].append(ticker)
        elif action == "hold_with_override":
            buckets["Override"].append(ticker)
        elif action in {"replace_partial", "replace_full"}:
            dest = _ticker(row.get("destination_ticker"))
            buckets["Replace"].append(f"{ticker}→{dest}" if dest else ticker)
        elif action == "add_from_cash":
            buckets["Add"].append(ticker)
        else:
            buckets["Hold"].append(ticker)
    return "\n".join([
        "| Close | Reduce | Hold | Add | Replace | Override |",
        "|---|---|---|---|---|---|",
        "| " + " | ".join(", ".join(buckets[key]) if buckets[key] else "None" for key in ["Close", "Reduce", "Hold", "Add", "Replace", "Override"]) + " |",
    ])


def rotation_plan_summary_from_rotation_nl(state: dict[str, Any]) -> str:
    decisions = _decisions(state)
    buckets = {"Sluiten": [], "Verlagen": [], "Aanhouden": [], "Toevoegen": [], "Vervangen": [], "Override": []}
    for row in decisions:
        t = _ticker(row.get("ticker"))
        action = _text(row.get("action_code"))
        if action == "close":
            buckets["Sluiten"].append(t)
        elif action == "reduce":
            buckets["Verlagen"].append(t)
        elif action == "hold_with_override":
            buckets["Override"].append(t)
        elif action in {"replace_partial", "replace_full"}:
            dest = _ticker(row.get("destination_ticker"))
            buckets["Vervangen"].append(f"{t}→{dest}" if dest else t)
        elif action == "add_from_cash":
            buckets["Toevoegen"].append(t)
        else:
            buckets["Aanhouden"].append(t)
    return "\n".join([
        "| Sluiten | Verlagen | Aanhouden | Toevoegen | Vervangen | Override |",
        "|---|---|---|---|---|---|",
        "| " + " | ".join(", ".join(buckets[key]) if buckets[key] else "Geen" for key in ["Sluiten", "Verlagen", "Aanhouden", "Toevoegen", "Vervangen", "Override"]) + " |",
    ])
