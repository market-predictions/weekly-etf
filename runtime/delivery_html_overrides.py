from __future__ import annotations

import json
import os
import re
from html import escape
from pathlib import Path
from typing import Any, Callable

from runtime.build_etf_report_state import build_runtime_state
from runtime.render_etf_report_from_state import f2, position_rows
from runtime.replacement_duel_v2 import replacement_duel_v2_html

PRINT_TABLE_PAGINATION_CSS = """
<style id="etf-table-pagination-guard">
  @media print {
    table { page-break-inside: auto; break-inside: auto; border-collapse: collapse; }
    thead { display: table-header-group; }
    tfoot { display: table-footer-group; }
    tr, th, td { page-break-inside: avoid; break-inside: avoid; }
    .panel table tr, .panel table th, .panel table td,
    .data-table tr, .action-table tr, .rotation-plan-table tr,
    .position-review-table tr, .replacement-duel-v2-table tr {
      page-break-inside: avoid; break-inside: avoid;
    }
  }
</style>
"""

NL_MARKERS = ["belangrijkste conclusie", "wat is er deze week veranderd", "beschikbare cash", "kernsamenvatting", "portefeuille-acties"]
SUMMARY_STRIP_RE = re.compile(
    r"(<div\s+class=['\"]summary-strip['\"]>)(.*?)(</div>\s*<div\s+class=['\"]client-grid['\"]>)",
    re.DOTALL | re.IGNORECASE,
)
MINI_CARD_TRIPLE_RE = re.compile(
    r"(?:<div class=['\"]mini-card['\"]>\s*"
    r"<div class=['\"]mini-label['\"]>.*?</div>\s*"
    r"<div class=['\"]mini-value['\"]>.*?</div>\s*"
    r"</div>\s*){3}",
    re.DOTALL | re.IGNORECASE,
)
RUNTIME_POINTER = Path("output/runtime/latest_etf_report_state_path.txt")

FORBIDDEN_POST_EXECUTION_PHRASES = {
    "Rotation plan artifact is active": "Guarded model rotation is reflected in the official portfolio state",
    "target weights and trade intents are proposed until the trade ledger and portfolio state record execution": "the official portfolio state and trade ledger already reflect the guarded model rotation",
    "proposed until": "already reflected",
    "pending execution and portfolio-state persistence": "already reflected in official portfolio state",
    "pending portfolio-state persistence": "already reflected in official portfolio state",
    "pending execution": "already reflected in official portfolio state",
    "Proposed rotation": "Reflected rotation",
    "proposed rotation": "reflected rotation",
    "trade intents are proposed": "the guarded model rotation is reflected",
    "not executed trades until": "already reflected in official state",
}

LABELS = {
    "en": {
        "portfolio_action_snapshot": "Portfolio Action Snapshot",
        "current_position_review": "Current Position Review",
        "portfolio_rotation_plan": "Portfolio Rotation Plan",
        "replacement_duel_table": "Replacement Duel Table",
        "recommendation": "Recommendation",
        "tickers_notes": "Tickers / notes",
        "add": "Add",
        "add_destination": "Add / destination",
        "hold": "Hold",
        "hold_override": "Hold with override",
        "hold_replaceable": "Hold but replaceable",
        "reflected_replace_reduce": "Reflected replace / reduce",
        "reduce": "Reduce",
        "close": "Close",
        "none": "None",
        "replaceable_note": "remain under explicit review.",
        "best_replacements": "Best replacements to fund",
        "best_replacements_note": "No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel.",
        "post_execution_best_replacements_note": "The guarded model rotation is already reflected in the official portfolio state and trade ledger; no duplicate state or ledger mutation was performed by this report render.",
        "ticker": "Ticker",
        "action": "Action",
        "score": "Score",
        "fresh_cash": "Fresh cash",
        "role": "Role",
        "required_next_action": "Required next action",
        "replace": "Replace",
        "primary_regime": "Primary regime",
        "geopolitical_regime": "Geopolitical regime",
        "main_takeaway": "Main takeaway",
        "rotation_status": "Rotation execution status",
        "rotation_reflected_note": "Guarded model rotation is already reflected in the official portfolio state and trade ledger; this run performed no duplicate state or ledger mutation.",
    },
    "nl": {
        "portfolio_action_snapshot": "Portefeuille-acties",
        "current_position_review": "Review huidige posities",
        "portfolio_rotation_plan": "Rotatieplan portefeuille",
        "replacement_duel_table": "Vervangingsanalyse",
        "recommendation": "Advies",
        "tickers_notes": "Tickers / toelichting",
        "add": "Toevoegen",
        "add_destination": "Toevoegen / bestemming",
        "hold": "Aanhouden",
        "hold_override": "Aanhouden met override",
        "hold_replaceable": "Aanhouden, maar vervangbaar",
        "reflected_replace_reduce": "Verwerkte vervanging / verlaging",
        "reduce": "Verlagen",
        "close": "Sluiten",
        "none": "Geen",
        "replaceable_note": "blijven expliciet onder herbeoordeling.",
        "best_replacements": "Beste alternatieven om te financieren",
        "best_replacements_note": "Nog geen alternatief is sterk genoeg om direct te financieren. Elk genoemd alternatief moet eerst dezelfde prijsbasis en relatieve-sterkteanalyse doorstaan.",
        "post_execution_best_replacements_note": "De bewaakte modelrotatie is al verwerkt in de officiële portefeuillestaat en het handelslogboek; deze rapport-render heeft geen dubbele staat- of handelslogboekmutatie uitgevoerd.",
        "ticker": "Ticker",
        "action": "Actie",
        "score": "Score",
        "fresh_cash": "Vers kapitaal",
        "role": "Rol",
        "required_next_action": "Volgende toets",
        "replace": "Vervangen",
        "primary_regime": "Primair regime",
        "geopolitical_regime": "Geopolitiek regime",
        "main_takeaway": "Kernconclusie",
        "rotation_status": "Status rotatie-uitvoering",
        "rotation_reflected_note": "De bewaakte modelrotatie is al verwerkt in de officiële portefeuillestaat en het handelslogboek; deze run heeft geen dubbele staat- of handelslogboekmutatie uitgevoerd.",
    },
}

ACTION_NL = {
    "hold": "Aanhouden",
    "add": "Toevoegen",
    "buy": "Kopen",
    "increase": "Toevoegen",
    "reduce": "Verlagen",
    "decrease": "Verlagen",
    "close": "Sluiten",
    "sell": "Verkopen",
    "hold under review": "Aanhouden, onder herbeoordeling",
    "already reflected": "Al verwerkt",
}
ROTATION_ACTION_LABELS = {
    "en": {
        "hold": "Hold",
        "hold_with_override": "Hold with override",
        "reduce": "Reduce",
        "replace_partial": "Replace partial",
        "replace_full": "Replace full",
        "close": "Close",
        "add_from_cash": "Add from cash",
    },
    "nl": {
        "hold": "Aanhouden",
        "hold_with_override": "Aanhouden met override",
        "reduce": "Verlagen",
        "replace_partial": "Gedeeltelijk vervangen",
        "replace_full": "Volledig vervangen",
        "close": "Sluiten",
        "add_from_cash": "Toevoegen vanuit cash",
    },
}
FRESH_CASH_NL = {
    "smaller / under review": "Kleiner / onder herbeoordeling",
    "smaller": "Kleiner",
    "reduce": "Verlagen",
    "hold": "Aanhouden",
    "hold / monitor": "Aanhouden / monitoren",
}
ROLE_NL = {
    "Core beta": "Kernbeta",
    "Growth engine": "Groeimotor",
    "Resilience": "Weerbaarheid",
    "Real-asset capex": "Reële activa / capex",
    "Strategic energy": "Strategische energie",
    "Hedge ballast": "Hedgepositie",
    "Rotation destination": "Rotatiebestemming",
}
NEXT_ACTION_NL = {
    "SPY": "Toets overlap met SMH voordat extra kapitaal wordt toegewezen.",
    "SMH": "Aanhouden binnen de maximale positiegrootte en opnieuw toetsen op concentratie.",
    "PPA": "Voer de vervangingsanalyse tegenover ITA opnieuw uit.",
    "PAVE": "Voer de vervangingsanalyse tegenover GRID opnieuw uit.",
    "URNM": "Aanhouden en vergelijken met URA/NLR als uraniumbreedte verbetert.",
    "GLD": "Voer de hedge-validiteitstest opnieuw uit tegenover GSG en BIL.",
    "GSG": "Monitor commodity-breedte en bijdrage aan de hedgefunctie.",
}


def _language(md_text: str) -> str:
    lower = md_text.lower()
    return "nl" if any(marker in lower for marker in NL_MARKERS) else "en"


def _labels(language: str) -> dict[str, str]:
    return LABELS.get(language, LABELS["en"])


def _clean(value: Any, language: str = "en") -> str:
    fallback = LABELS[language].get("none", "None")
    raw = str(value or "").strip()
    if not raw or raw.lower() in {"none", "null", "nan"}:
        return fallback
    return raw


def _compact(value: Any, max_len: int = 90, language: str = "en") -> str:
    raw = _clean(value, language)
    return raw if len(raw) <= max_len else raw[: max_len - 1].rstrip() + "…"


def _strip_md(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", value)
    value = value.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", value).strip()


def _section_one_pairs(md_text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    in_section = False
    for raw in md_text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("## 1."):
            in_section = True
            continue
        if in_section and stripped.startswith("## 2."):
            break
        if not in_section or not stripped.startswith("-") or ":" not in stripped:
            continue
        key, value = stripped.lstrip("- ").split(":", 1)
        norm_key = _strip_md(key).lower()
        pairs[norm_key] = _strip_md(value)
    return pairs


def _summary_values(md_text: str, language: str) -> dict[str, str]:
    pairs = _section_one_pairs(md_text)
    if language == "nl":
        return {
            "primary": pairs.get("primair regime") or pairs.get("primary regime") or "",
            "geo": pairs.get("geopolitiek regime") or pairs.get("geopolitical regime") or "",
            "takeaway": pairs.get("belangrijkste conclusie") or pairs.get("kernconclusie") or pairs.get("main takeaway") or "",
        }
    return {
        "primary": pairs.get("primary regime") or pairs.get("primair regime") or "",
        "geo": pairs.get("geopolitical regime") or pairs.get("geopolitiek regime") or "",
        "takeaway": pairs.get("main takeaway") or pairs.get("belangrijkste conclusie") or pairs.get("kernconclusie") or "",
    }


def _hero_cards_html(values: dict[str, str], language: str) -> str:
    labels = _labels(language)
    primary = values.get("primary") or ("Pending classification" if language == "en" else "Nog niet geclassificeerd")
    geo = values.get("geo") or ("Pending classification" if language == "en" else "Nog niet geclassificeerd")
    takeaway = values.get("takeaway") or ("Keep the current allocation disciplined." if language == "en" else "Houd de huidige allocatie gedisciplineerd.")
    return (
        f"<div class='mini-card'><div class='mini-label'>{escape(labels['primary_regime'])}</div><div class='mini-value'>{escape(primary)}</div></div>"
        f"<div class='mini-card'><div class='mini-label'>{escape(labels['geopolitical_regime'])}</div><div class='mini-value'>{escape(geo)}</div></div>"
        f"<div class='mini-card'><div class='mini-label'>{escape(labels['main_takeaway'])}</div><div class='mini-value'>{escape(takeaway)}</div></div>"
    )


def _replace_hero_cards(html: str, md_text: str, language: str) -> str:
    values = _summary_values(md_text, language)
    replacement = _hero_cards_html(values, language)

    def replace_summary_strip(match: re.Match[str]) -> str:
        return f"{match.group(1)}{replacement}{match.group(3)}"

    updated, count = SUMMARY_STRIP_RE.subn(replace_summary_strip, html, count=1)
    if count:
        return updated
    return MINI_CARD_TRIPLE_RE.sub(replacement, html, count=1)


def _nl_action(value: Any) -> str:
    raw = str(value or "").strip()
    low = raw.lower()
    if low in ACTION_NL:
        return ACTION_NL[low]
    if "add" in low or "buy" in low:
        return "Toevoegen"
    if "reduce" in low or "decrease" in low:
        return "Verlagen"
    if "review" in low:
        return "Aanhouden, onder herbeoordeling"
    if "hold" in low:
        return "Aanhouden"
    if not raw or low == "none":
        return "Geen"
    return raw


def _nl_fresh_cash(value: Any) -> str:
    raw = str(value or "").strip()
    low = raw.lower()
    return FRESH_CASH_NL.get(low, raw or "Onder herbeoordeling")


def _nl_role(value: Any) -> str:
    raw = str(value or "").strip()
    return ROLE_NL.get(raw, raw or "Positie")


def _display_action(value: Any, language: str) -> str:
    return _nl_action(value) if language == "nl" else _clean(value, language)


def _display_fresh_cash(value: Any, language: str) -> str:
    return _nl_fresh_cash(value) if language == "nl" else _clean(value, language)


def _display_role(value: Any, language: str) -> str:
    return _nl_role(value) if language == "nl" else _compact(value, 55, language)


def _display_next_action(ticker: str, value: Any, language: str) -> str:
    if language == "nl":
        return NEXT_ACTION_NL.get(ticker, "Aanhouden en opnieuw toetsen in de volgende run.")
    return _compact(value, 95, language)


def _is_add(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    executed = _clean(p.get("action_executed_this_run")).lower()
    shares_delta = float(p.get("shares_delta_this_run") or 0.0)
    return "add" in action or "buy" in executed or "increase" in executed or shares_delta > 0


def _is_hold(p: dict[str, Any]) -> bool:
    return "hold" in _clean(p.get("suggested_action")).lower() and not _is_add(p)


def _is_replace(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    better = _clean(p.get("better_alternative_exists")).lower()
    return better == "yes" or "review" in action or "replace" in action


def _is_reduce(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    executed = _clean(p.get("action_executed_this_run")).lower()
    return "reduce" in action or "decrease" in executed or "sell" in executed


def _is_close(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    return "close" in action or "sell" in action


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _ticker_anchor(base: Any, ticker: str, language: str = "en") -> str:
    ticker = ticker.strip().upper()
    if not ticker or ticker == "NONE":
        return _labels(language)["none"]
    try:
        return base.ticker_anchor_html(ticker)
    except Exception:
        url = f"https://www.tradingview.com/chart/?symbol={escape(ticker)}"
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{escape(ticker)}</a>'


def _ticker_join(base: Any, tickers: list[str], language: str) -> str:
    values = [t.strip().upper() for t in tickers if t and t.strip().upper() != "NONE"]
    return ", ".join(_ticker_anchor(base, t, language) for t in values) if values else _labels(language)["none"]


def _ticker_expr_html(base: Any, value: str, language: str) -> str:
    if "→" not in value:
        return _ticker_anchor(base, value, language)
    left, right = value.split("→", 1)
    return f"{_ticker_anchor(base, left, language)} → {_ticker_anchor(base, right, language)}"


def _ticker_expr_join(base: Any, values: list[str], language: str) -> str:
    cleaned = [v for v in values if v and v != "NONE"]
    return ", ".join(_ticker_expr_html(base, v, language) for v in cleaned) if cleaned else _labels(language)["none"]


def _section_header(base: Any, number: int, title: str) -> str:
    try:
        return base.section_header_html(number, title)
    except Exception:
        return f"<h2>{escape(title)}</h2>"


def _read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _is_post_execution_state(state: dict[str, Any] | None) -> bool:
    if not state:
        return False
    context = state.get("execution_context") or {}
    flags = state.get("validation_flags") or {}
    return context.get("report_phase") == "post_execution" or bool(flags.get("already_executed_noop")) or bool(flags.get("post_execution_report"))


def _runtime_state_from_pointer() -> dict[str, Any] | None:
    # Prefer the latest finalized post-execution state over the earlier pre-execution runtime state left in GitHub env.
    pointer_state: dict[str, Any] | None = None
    if RUNTIME_POINTER.exists():
        raw = RUNTIME_POINTER.read_text(encoding="utf-8").strip()
        if raw:
            path = Path(raw)
            pointer_state = _read_json_file(path) or _read_json_file(RUNTIME_POINTER.parent / path.name)
    if _is_post_execution_state(pointer_state):
        return pointer_state
    for raw in (os.environ.get("MRKT_RPRTS_RUNTIME_STATE_PATH"), os.environ.get("ETF_RUNTIME_STATE_PATH")):
        if not raw:
            continue
        env_state = _read_json_file(Path(raw))
        if env_state:
            return env_state
    return pointer_state


def _load_state() -> dict[str, Any]:
    state = _runtime_state_from_pointer()
    if state:
        return state
    return build_runtime_state()


def _rotation_decisions(state: dict[str, Any]) -> list[dict[str, Any]]:
    if _is_post_execution_state(state):
        return []
    rows = state.get("rotation_decisions") or (state.get("rotation_plan") or {}).get("rotation_decisions") or []
    return list(rows) if isinstance(rows, list) else []


def _trade_intents(state: dict[str, Any]) -> list[dict[str, Any]]:
    if _is_post_execution_state(state):
        return []
    rows = state.get("trade_intents") or (state.get("rotation_plan") or {}).get("trade_intents") or []
    return list(rows) if isinstance(rows, list) else []


def _has_rotation_plan(state: dict[str, Any]) -> bool:
    return bool(_rotation_decisions(state) or _trade_intents(state))


def _decision_by_ticker(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): row for row in _rotation_decisions(state) if _ticker(row.get("ticker"))}


def _rotation_action(value: Any, language: str) -> str:
    raw = str(value or "").strip()
    return ROTATION_ACTION_LABELS.get(language, ROTATION_ACTION_LABELS["en"]).get(raw, raw or _labels(language)["none"])


def _rotation_bucket_summary(state: dict[str, Any]) -> dict[str, list[str]]:
    buckets = {"add": [], "hold": [], "override": [], "replace": [], "reduce": [], "close": []}
    for row in _rotation_decisions(state):
        ticker = _ticker(row.get("ticker"))
        action = str(row.get("action_code") or "").strip()
        destination = _ticker(row.get("destination_ticker"))
        if not ticker:
            continue
        if action == "close":
            buckets["close"].append(ticker)
        elif action == "reduce":
            buckets["reduce"].append(ticker)
        elif action in {"replace_partial", "replace_full"}:
            buckets["replace"].append(f"{ticker}→{destination}" if destination else ticker)
        elif action == "hold_with_override":
            buckets["override"].append(ticker)
        elif action == "add_from_cash":
            buckets["add"].append(ticker)
        else:
            buckets["hold"].append(ticker)
    for trade in _trade_intents(state):
        destination = _ticker(trade.get("destination_ticker"))
        if destination and destination not in buckets["add"]:
            buckets["add"].append(destination)
    return buckets


def _post_execution_pairs(state: dict[str, Any]) -> list[str]:
    pairs: list[str] = []
    buys: dict[str, str] = {}
    sells: dict[str, str] = {}
    for position in position_rows(state):
        ticker = _ticker(position.get("ticker"))
        action = _clean(position.get("action_executed_this_run")).lower()
        note = _clean(position.get("funding_source_note"))
        if not ticker or action in {"", "none"}:
            continue
        if "buy" in action:
            match = re.search(r"\bfunded by\s+([A-Z][A-Z0-9.]*)\b", note, flags=re.IGNORECASE)
            if match:
                buys[ticker] = _ticker(match.group(1))
        if "sell" in action or "reduce" in action:
            match = re.search(r"\bfund\s+([A-Z][A-Z0-9.]*)\b", note, flags=re.IGNORECASE)
            if match:
                sells[ticker] = _ticker(match.group(1))

    for destination, source in buys.items():
        if source:
            pair = f"{source}→{destination}"
            if pair not in pairs:
                pairs.append(pair)
    for source, destination in sells.items():
        if destination:
            pair = f"{source}→{destination}"
            if pair not in pairs:
                pairs.append(pair)

    if pairs:
        return pairs

    for trade in _trade_intents(state):
        source = _ticker(trade.get("source_ticker"))
        destination = _ticker(trade.get("destination_ticker"))
        if source and destination:
            pair = f"{source}→{destination}"
            if pair not in pairs:
                pairs.append(pair)
    return pairs


def _post_execution_best_replacements_note_html(base: Any, state: dict[str, Any], language: str) -> str:
    pairs = _post_execution_pairs(state)
    if not pairs:
        return escape(_labels(language)["post_execution_best_replacements_note"])
    pair_html = _ticker_expr_join(base, pairs, language)
    if language == "nl":
        return (
            "De bewaakte modelrotatie "
            + pair_html
            + " is al verwerkt in de officiële portefeuillestaat en het handelslogboek; "
            + "deze rapport-render heeft geen dubbele staat- of handelslogboekmutatie uitgevoerd."
        )
    return (
        "The guarded model rotation "
        + pair_html
        + " is already reflected in the official portfolio state and trade ledger; "
        + "no duplicate state or ledger mutation was performed by this report render."
    )


def _trade_summary_html(base: Any, state: dict[str, Any], language: str) -> str:
    if _is_post_execution_state(state):
        return _post_execution_best_replacements_note_html(base, state, language)
    intents = _trade_intents(state)
    if not intents:
        return escape(_labels(language)["best_replacements_note"])
    parts: list[str] = []
    for trade in intents:
        source = _ticker(trade.get("source_ticker"))
        destination = _ticker(trade.get("destination_ticker")) or "CASH"
        source_delta = f2(trade.get("delta_weight_pct")) or "0.00"
        dest_delta = f2(trade.get("destination_delta_weight_pct")) or "0.00"
        if language == "nl":
            parts.append(f"verlaag {_ticker_anchor(base, source, language)} met {escape(source_delta)}% NAV en alloceer {escape(dest_delta)}% NAV naar {_ticker_anchor(base, destination, language)}")
        else:
            parts.append(f"reduce {_ticker_anchor(base, source, language)} by {escape(source_delta)}% NAV and allocate {escape(dest_delta)}% NAV to {_ticker_anchor(base, destination, language)}")
    suffix = "in afwachting van uitvoering en verwerking in de portefeuille-staat." if language == "nl" else "pending execution and portfolio-state persistence."
    return "; ".join(parts) + ", " + escape(suffix)


def _classified_positions(state: dict[str, Any]) -> dict[str, list[str]]:
    positions = position_rows(state)
    return {
        "add": [str(p.get("ticker", "")).upper() for p in positions if _is_add(p)],
        "hold": [str(p.get("ticker", "")).upper() for p in positions if _is_hold(p) or _is_add(p)],
        "replace": [str(p.get("ticker", "")).upper() for p in positions if _is_replace(p)],
        "reduce": [str(p.get("ticker", "")).upper() for p in positions if _is_reduce(p)],
        "close": [str(p.get("ticker", "")).upper() for p in positions if _is_close(p)],
    }


def _post_execution_action_snapshot_html(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    c = _classified_positions(state)
    reflected = _post_execution_pairs(state)
    return "".join([
        "<div class='panel panel-action-snapshot'>", _section_header(base, 2, l["portfolio_action_snapshot"]),
        "<table class='action-table'><thead><tr>",
        f"<th>{escape(l['recommendation'])}</th><th>{escape(l['tickers_notes'])}</th></tr></thead><tbody>",
        f"<tr><th>{escape(l['add_destination'])}</th><td>{_ticker_join(base, c['add'], language)}</td></tr>",
        f"<tr><th>{escape(l['hold'])}</th><td>{_ticker_join(base, c['hold'], language)}</td></tr>",
        f"<tr><th>{escape(l['hold_override'])}</th><td>{_ticker_join(base, c['replace'], language)} {escape(l['replaceable_note'])}</td></tr>",
        f"<tr><th>{escape(l['reflected_replace_reduce'])}</th><td>{_ticker_expr_join(base, reflected, language)}</td></tr>",
        f"<tr><th>{escape(l['close'])}</th><td>{_ticker_join(base, c['close'], language)}</td></tr>",
        "</tbody></table>",
        f"<div class='note-box'><h4>{escape(l['rotation_status'])}</h4><ul><li>{escape(l['rotation_reflected_note'])}</li></ul></div>",
        f"<div class='note-box'><h4>{escape(l['best_replacements'])}</h4><ul><li>{_trade_summary_html(base, state, language)}</li></ul></div>",
        "</div>",
    ])


def _action_snapshot_html(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    if _is_post_execution_state(state):
        return _post_execution_action_snapshot_html(base, state, language)
    if _has_rotation_plan(state):
        c = _rotation_bucket_summary(state)
        return "".join([
            "<div class='panel panel-action-snapshot'>", _section_header(base, 2, l["portfolio_action_snapshot"]),
            "<table class='action-table'><thead><tr>",
            f"<th>{escape(l['recommendation'])}</th><th>{escape(l['tickers_notes'])}</th></tr></thead><tbody>",
            f"<tr><th>{escape(l['add_destination'])}</th><td>{_ticker_join(base, c['add'], language)}</td></tr>",
            f"<tr><th>{escape(l['hold'])}</th><td>{_ticker_join(base, c['hold'], language)}</td></tr>",
            f"<tr><th>{escape(l['hold_override'])}</th><td>{_ticker_join(base, c['override'], language)}</td></tr>",
            f"<tr><th>{escape(l['reflected_replace_reduce'])}</th><td>{_ticker_expr_join(base, c['replace'] + c['reduce'], language)}</td></tr>",
            f"<tr><th>{escape(l['close'])}</th><td>{_ticker_join(base, c['close'], language)}</td></tr>",
            "</tbody></table>",
            f"<div class='note-box'><h4>{escape(l['rotation_status'])}</h4><ul><li>{escape(l['rotation_reflected_note'])}</li></ul></div>",
            f"<div class='note-box'><h4>{escape(l['best_replacements'])}</h4><ul><li>{_trade_summary_html(base, state, language)}</li></ul></div>",
            "</div>",
        ])

    c = _classified_positions(state)
    return "".join([
        "<div class='panel panel-action-snapshot'>", _section_header(base, 2, l["portfolio_action_snapshot"]),
        "<table class='action-table'><thead><tr>",
        f"<th>{escape(l['recommendation'])}</th><th>{escape(l['tickers_notes'])}</th></tr></thead><tbody>",
        f"<tr><th>{escape(l['add'])}</th><td>{_ticker_join(base, c['add'], language)}</td></tr>",
        f"<tr><th>{escape(l['hold'])}</th><td>{_ticker_join(base, c['hold'], language)}</td></tr>",
        f"<tr><th>{escape(l['hold_replaceable'])}</th><td>{_ticker_join(base, c['replace'], language)} {escape(l['replaceable_note'])}</td></tr>",
        f"<tr><th>{escape(l['reduce'])}</th><td>{_ticker_join(base, c['reduce'], language)}</td></tr>",
        f"<tr><th>{escape(l['close'])}</th><td>{_ticker_join(base, c['close'], language)}</td></tr>",
        "</tbody></table>", f"<div class='note-box'><h4>{escape(l['best_replacements'])}</h4>",
        f"<ul><li>{escape(l['best_replacements_note'])}</li></ul>", "</div></div>",
    ])


def _position_review_html(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    decisions = _decision_by_ticker(state)
    rows: list[str] = []
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        decision = decisions.get(ticker, {})
        if decision:
            action = _rotation_action(decision.get("action_code"), language)
            destination = _ticker(decision.get("destination_ticker"))
            if destination:
                action = f"{action} → {destination}"
            release_score = f2(decision.get("release_score")) or ""
            next_action = (f"Release score {release_score}. " if language == "en" else f"Vrijmaakscore {release_score}. ") + _display_next_action(ticker, p.get("required_next_action"), language)
        else:
            action = _display_action(p.get("suggested_action"), language)
            next_action = _display_next_action(ticker, p.get("required_next_action"), language)
        rows.append(
            "<tr>"
            f"<td>{_ticker_anchor(base, ticker, language)}</td>"
            f"<td>{escape(action)}</td>"
            f"<td class='num'>{escape(f2(p.get('total_score')) or 'n/a')}</td>"
            f"<td>{escape(_display_fresh_cash(p.get('fresh_cash_test'), language))}</td>"
            f"<td>{escape(_display_role(p.get('portfolio_role'), language))}</td>"
            f"<td>{escape(next_action)}</td>"
            "</tr>"
        )
    return "".join([
        "<div class='panel panel-position-review'>", _section_header(base, 3, l["current_position_review"]),
        "<table class='data-table position-review-table'><thead><tr>",
        f"<th>{escape(l['ticker'])}</th><th>{escape(l['action'])}</th><th>{escape(l['score'])}</th><th>{escape(l['fresh_cash'])}</th><th>{escape(l['role'])}</th><th>{escape(l['required_next_action'])}</th></tr></thead>",
        "<tbody>", "".join(rows), "</tbody></table></div>",
    ])


def _rotation_plan_html(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    if _is_post_execution_state(state):
        c = _classified_positions(state)
        reflected = _post_execution_pairs(state)
        return "".join([
            "<div class='panel panel-rotation-plan'>", _section_header(base, 5, l["portfolio_rotation_plan"]),
            "<table class='data-table rotation-plan-table'><thead><tr>",
            f"<th>{escape(l['close'])}</th><th>{escape(l['reduce'])}</th><th>{escape(l['hold'])}</th><th>{escape(l['add'])}</th><th>{escape(l['replace'])}</th></tr></thead>",
            "<tbody><tr>",
            f"<td>{_ticker_join(base, c['close'], language)}</td><td>{_ticker_join(base, c['reduce'], language)}</td><td>{_ticker_join(base, c['hold'], language)}</td><td>{_ticker_join(base, c['add'], language)}</td><td>{_ticker_expr_join(base, reflected, language)}</td>",
            "</tr></tbody></table>",
            f"<div class='note-box'><ul><li>{escape(l['rotation_reflected_note'])}</li></ul></div></div>",
        ])
    if _has_rotation_plan(state):
        c = _rotation_bucket_summary(state)
        return "".join([
            "<div class='panel panel-rotation-plan'>", _section_header(base, 5, l["portfolio_rotation_plan"]),
            "<table class='data-table rotation-plan-table'><thead><tr>",
            f"<th>{escape(l['close'])}</th><th>{escape(l['reduce'])}</th><th>{escape(l['hold'])}</th><th>{escape(l['hold_override'])}</th><th>{escape(l['add_destination'])}</th><th>{escape(l['replace'])}</th></tr></thead>",
            "<tbody><tr>",
            f"<td>{_ticker_join(base, c['close'], language)}</td><td>{_ticker_join(base, c['reduce'], language)}</td><td>{_ticker_join(base, c['hold'], language)}</td><td>{_ticker_join(base, c['override'], language)}</td><td>{_ticker_join(base, c['add'], language)}</td><td>{_ticker_expr_join(base, c['replace'], language)}</td>",
            "</tr></tbody></table></div>",
        ])
    c = _classified_positions(state)
    return "".join([
        "<div class='panel panel-rotation-plan'>", _section_header(base, 5, l["portfolio_rotation_plan"]),
        "<table class='data-table rotation-plan-table'><thead><tr>",
        f"<th>{escape(l['close'])}</th><th>{escape(l['reduce'])}</th><th>{escape(l['hold'])}</th><th>{escape(l['add'])}</th><th>{escape(l['replace'])}</th></tr></thead>",
        "<tbody><tr>",
        f"<td>{_ticker_join(base, c['close'], language)}</td><td>{_ticker_join(base, c['reduce'], language)}</td><td>{_ticker_join(base, c['hold'], language)}</td><td>{_ticker_join(base, c['add'], language)}</td><td>{_ticker_join(base, c['replace'], language)}</td>",
        "</tr></tbody></table></div>",
    ])


def _replacement_duel_panel(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    return "".join(["<div class='panel panel-replacement-duel'>", _section_header(base, 11, l["replacement_duel_table"]), replacement_duel_v2_html(state, base, language=language), "</div>"])


def _replace_panel_by_title(html: str, titles: list[str], replacement: str) -> str:
    label_idx = -1
    for title in titles:
        for marker in (f"<span class='section-label'>{escape(title)}</span>", f'<span class="section-label">{escape(title)}</span>', escape(title)):
            label_idx = html.find(marker)
            if label_idx != -1:
                break
        if label_idx != -1:
            break
    if label_idx == -1:
        return html
    start = max(html.rfind("<div class='panel", 0, label_idx), html.rfind('<div class="panel', 0, label_idx))
    if start == -1:
        return html
    next_candidates = [pos for token in ("<div class='panel", '<div class="panel') if (pos := html.find(token, label_idx + 1)) != -1]
    end = min(next_candidates) if next_candidates else html.find("</body>", label_idx)
    if end == -1:
        end = len(html)
    return html[:start] + replacement + html[end:]


def _append_replacement_duel_after_best_opportunities(html: str, base: Any, state: dict[str, Any], language: str) -> str:
    if "replacement-duel-v2-table" in html:
        return html.replace("Replacement Duel Table v2", _labels(language)["replacement_duel_table"])
    idx = -1
    marker_len = 0
    for marker in ("Best New Opportunities", "Beste nieuwe kansen"):
        idx = html.find(marker)
        if idx != -1:
            marker_len = len(marker)
            break
    if idx == -1:
        return html
    next_candidates = [pos for token in ("<div class='panel", '<div class="panel') if (pos := html.find(token, idx + marker_len)) != -1]
    insert_at = min(next_candidates) if next_candidates else html.find("</body>", idx)
    if insert_at == -1:
        insert_at = len(html)
    return html[:insert_at] + _replacement_duel_panel(base, state, language) + html[insert_at:]


def _inject_print_table_pagination_css(html: str) -> str:
    if "etf-table-pagination-guard" in html:
        return html
    if "</head>" in html:
        return html.replace("</head>", PRINT_TABLE_PAGINATION_CSS + "\n</head>", 1)
    return PRINT_TABLE_PAGINATION_CSS + html


def _sanitize_post_execution_copy(html: str, state: dict[str, Any]) -> str:
    if not _is_post_execution_state(state):
        return html
    for old, new in FORBIDDEN_POST_EXECUTION_PHRASES.items():
        html = html.replace(old, new)
    return html


def apply_etf_delivery_html_overrides(html: str, base: Any, md_text: str) -> str:
    language = _language(md_text)
    try:
        state = _load_state()
    except Exception:
        return _inject_print_table_pagination_css(html)
    html = _replace_hero_cards(html, md_text, language)
    html = _replace_panel_by_title(html, ["Portfolio Action Snapshot", "Portefeuille-acties"], _action_snapshot_html(base, state, language))
    html = _replace_panel_by_title(html, ["Current Position Review", "Review huidige posities"], _position_review_html(base, state, language))
    html = _replace_panel_by_title(html, ["Portfolio Rotation Plan", "Rotatieplan portefeuille"], _rotation_plan_html(base, state, language))
    html = _append_replacement_duel_after_best_opportunities(html, base, state, language)
    html = html.replace("Replacement Duel Table v2", _labels(language)["replacement_duel_table"])
    html = _sanitize_post_execution_copy(html, state)
    return _inject_print_table_pagination_css(html)


def build_report_html_with_state(base_build_report_html: Callable[..., str], base: Any) -> Callable[..., str]:
    def _wrapped(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
        html = base_build_report_html(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
        return apply_etf_delivery_html_overrides(html, base, md_text)
    return _wrapped
