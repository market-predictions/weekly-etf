from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

import yaml

from runtime.nl_localization import localized_pricing_basis

DEFAULT_TARGET_MAP: dict[str, list[str]] = {
    "SPY": ["QUAL", "IEFA", "EFA", "IWM"],
    "PPA": ["ITA", "DFEN", "NATO"],
    "PAVE": ["GRID", "XLU", "VPU"],
    "GLD": ["GSG", "DBC", "BIL"],
    "URNM": ["URA", "NLR", "NUCL"],
    "SMH": ["SOXX", "IRBO", "BOTZ", "ROBO"],
}

PRIORITY_DUEL_PAIRS: set[tuple[str, str]] = {
    ("SPY", "QUAL"),
    ("SPY", "IEFA"),
    ("SPY", "EFA"),
    ("SPY", "IWM"),
    ("PPA", "ITA"),
    ("PAVE", "GRID"),
    ("GLD", "GSG"),
    ("GLD", "BIL"),
    ("URNM", "URA"),
    ("SMH", "SOXX"),
}

STRATEGIC_HOLDING_ORDER = ["SPY", "PPA", "PAVE", "GLD", "URNM", "SMH"]
STRATEGIC_HOLDING_RANK = {ticker: idx for idx, ticker in enumerate(STRATEGIC_HOLDING_ORDER)}
DEFAULT_MACRO_CONTEXT = Path("config/etf_macro_fundamental_context.yml")
DEFAULT_RS_PATH = Path("output/market_history/etf_relative_strength.json")
INVESTOR_REPLACEMENT_DUEL_LIMIT = 8
PRICED_STATUSES = {"fresh_close", "fresh_fallback_source", "fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}
VALUATION_GRADE = "valuation_grade"

DECISION_LABELS: dict[str, dict[str, str]] = {
    "close_proof_incomplete": {
        "en": "Not fundable - close proof incomplete.",
        "nl": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig.",
    },
    "valuation_grade_required": {
        "en": "Not fundable - valuation-grade challenger pricing required.",
        "nl": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist.",
    },
    "rs_duel_incomplete": {
        "en": "Priced valuation-grade, but direct RS duel incomplete.",
        "nl": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
    },
    "replacement_trigger_watch": {
        "en": "Replacement trigger watch - challenger leading over 3m.",
        "nl": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden.",
    },
    "challenger_improving": {
        "en": "Challenger improving; keep duel active.",
        "nl": "Het alternatief verbetert; houd de vervangingsanalyse actief.",
    },
    "early_1m_only": {
        "en": "Early 1m improvement only; wait for 3m confirmation.",
        "nl": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging.",
    },
    "current_still_leads": {
        "en": "Current holding still leads; no replacement.",
        "nl": "Huidige positie blijft sterker; geen vervanging.",
    },
}

TRIGGER_LABELS: dict[str, dict[str, str]] = {
    "resolve_closes": {
        "en": "Resolve both close prices before decision.",
        "nl": "Los beide slotkoersen op vóór een besluit.",
    },
    "upgrade_valuation_grade": {
        "en": "Upgrade challenger to valuation-grade pricing before any funding decision.",
        "nl": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit.",
    },
    "confirm_thesis_liquidity_funding": {
        "en": "Confirm thesis fit, liquidity and funding source.",
        "nl": "Bevestig aansluiting op de beleggingscase, liquiditeit en financieringsbron.",
    },
    "repeat_3m_edge_and_capital": {
        "en": "Needs repeat 3m edge and capital source.",
        "nl": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron.",
    },
    "needs_3m_confirmation": {
        "en": "Needs 3m confirmation.",
        "nl": "Vereist 3-maands bevestiging.",
    },
    "sustained_outperformance": {
        "en": "Needs sustained relative outperformance.",
        "nl": "Vereist aanhoudende relatieve outperformance.",
    },
}


def _label(mapping: dict[str, dict[str, str]], code: str, language: str = "en") -> str:
    labels = mapping.get(code) or {}
    return labels.get(language) or labels.get("en") or code


def decision_label(code: str, language: str = "en") -> str:
    return _label(DECISION_LABELS, code, language)


def trigger_label(code: str, language: str = "en") -> str:
    return _label(TRIGGER_LABELS, code, language)


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _edge_text(value: Any) -> str:
    value_f = _num(value)
    if value_f is None:
        return "n/a"
    sign = "+" if value_f > 0 else ""
    return f"{sign}{value_f:.2f}%"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _target_map() -> dict[str, list[str]]:
    macro = _load_yaml(DEFAULT_MACRO_CONTEXT)
    target_map = ((macro.get("replacement_duel_policy") or {}).get("target_map") or {})
    if not target_map:
        return DEFAULT_TARGET_MAP
    out: dict[str, list[str]] = {}
    for holding, payload in target_map.items():
        holding_ticker = _ticker(holding)
        if isinstance(payload, dict):
            challengers = payload.get("challengers", []) or []
        else:
            challengers = payload or []
        out[holding_ticker] = [_ticker(challenger) for challenger in challengers if _ticker(challenger)]
    return out


def _rs_metrics(state: dict[str, Any]) -> dict[str, Any]:
    embedded = state.get("market_history", {}).get("metrics") if isinstance(state.get("market_history"), dict) else None
    if embedded:
        return embedded
    return (_load_json(DEFAULT_RS_PATH).get("metrics") or {})


def _index_prices(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in state.get("pricing", []) or []:
        symbol = _ticker(item.get("symbol"))
        if symbol:
            out[symbol] = item
    return out


def _index_positions(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in state.get("positions", []) or []:
        symbol = _ticker(item.get("ticker"))
        if symbol:
            out[symbol] = item
    return out


def _holding_close(state: dict[str, Any], holding: str) -> dict[str, Any]:
    position = _index_positions(state).get(_ticker(holding), {})
    price = _num(position.get("previous_price_local") or position.get("current_price_local"))
    currency = position.get("currency", "USD")
    returned_date = position.get("previous_price_date") or position.get("current_price_date") or state.get("requested_close_date") or state.get("report_date")
    return {
        "price": price,
        "currency": currency,
        "returned_close_date": returned_date,
        "source": position.get("pricing_source") or "portfolio_state_pricing_audit",
        "status": position.get("pricing_status") or ("priced" if price is not None else "missing_current_holding_close"),
        "pricing_tier": position.get("pricing_tier") or VALUATION_GRADE,
    }


def _price_close(price: dict[str, Any]) -> dict[str, Any]:
    selected = price.get("selected_close") if price.get("selected_close") is not None else price.get("price")
    return {
        "price": _num(selected),
        "currency": price.get("currency", "USD"),
        "returned_close_date": price.get("returned_close_date") or price.get("date"),
        "source": price.get("source") or price.get("source_detail") or "pricing_audit",
        "status": price.get("status") or "unresolved",
        "pricing_tier": price.get("pricing_tier") or "unclassified",
    }


def _return_edge(metrics: dict[str, Any], challenger: str, holding: str, key: str) -> float | None:
    challenger_return = (metrics.get(challenger) or {}).get(key)
    holding_return = (metrics.get(holding) or {}).get(key)
    try:
        if challenger_return is None or holding_return is None:
            return None
        return round(float(challenger_return) - float(holding_return), 2)
    except (TypeError, ValueError):
        return None


def _pricing_basis(current_close: dict[str, Any], challenger_close: dict[str, Any]) -> str:
    current_date = current_close.get("returned_close_date") or "missing current close"
    challenger_date = challenger_close.get("returned_close_date") or "missing challenger close"
    tier = challenger_close.get("pricing_tier") or "unclassified"
    if current_date and challenger_date and current_date == challenger_date:
        return f"Current and challenger closes validated on {current_date}; challenger pricing tier: {tier}."
    return f"Current validated on {current_date}; challenger validated on {challenger_date}; challenger pricing tier: {tier}."


def _pricing_complete(current_close: dict[str, Any], challenger_close: dict[str, Any]) -> bool:
    return current_close.get("price") is not None and challenger_close.get("price") is not None


def _valuation_grade_complete(current_close: dict[str, Any], challenger_close: dict[str, Any]) -> bool:
    return _pricing_complete(current_close, challenger_close) and str(challenger_close.get("status") or "") in PRICED_STATUSES and str(challenger_close.get("pricing_tier") or "") == VALUATION_GRADE


def _decision_code(pricing_complete: bool, valuation_grade_complete: bool, edge_1m: Any, edge_3m: Any) -> str:
    if not pricing_complete:
        return "close_proof_incomplete"
    if not valuation_grade_complete:
        return "valuation_grade_required"
    e1 = _num(edge_1m)
    e3 = _num(edge_3m)
    if e1 is None and e3 is None:
        return "rs_duel_incomplete"
    if e3 is not None and e3 >= 5.0:
        return "replacement_trigger_watch"
    if e3 is not None and e3 > 0:
        return "challenger_improving"
    if e1 is not None and e1 > 0 and (e3 is None or e3 <= 0):
        return "early_1m_only"
    return "current_still_leads"


def _trigger_code(pricing_complete: bool, valuation_grade_complete: bool, edge_1m: Any, edge_3m: Any) -> str:
    if not pricing_complete:
        return "resolve_closes"
    if not valuation_grade_complete:
        return "upgrade_valuation_grade"
    e1 = _num(edge_1m)
    e3 = _num(edge_3m)
    if e3 is not None and e3 >= 5.0:
        return "confirm_thesis_liquidity_funding"
    if e3 is not None and e3 > 0:
        return "repeat_3m_edge_and_capital"
    if e1 is not None and e1 > 0:
        return "needs_3m_confirmation"
    return "sustained_outperformance"


def _row_payload(state: dict[str, Any], holding: str, challenger: str, edge_1m: Any, edge_3m: Any, source: str) -> dict[str, Any]:
    prices = _index_prices(state)
    holding = _ticker(holding)
    challenger = _ticker(challenger)
    current_close = _holding_close(state, holding)
    challenger_close = _price_close(prices.get(challenger) or {})
    complete = _pricing_complete(current_close, challenger_close)
    valuation_complete = _valuation_grade_complete(current_close, challenger_close)
    decision_code = _decision_code(complete, valuation_complete, edge_1m, edge_3m)
    trigger_code = _trigger_code(complete, valuation_complete, edge_1m, edge_3m)
    row = {
        "current_holding": holding,
        "current_close": current_close.get("price"),
        "current_close_currency": current_close.get("currency", "USD"),
        "current_close_date": current_close.get("returned_close_date"),
        "current_pricing_tier": current_close.get("pricing_tier"),
        "challenger": challenger,
        "challenger_close": challenger_close.get("price"),
        "challenger_close_currency": challenger_close.get("currency", "USD"),
        "challenger_close_date": challenger_close.get("returned_close_date"),
        "challenger_pricing_tier": challenger_close.get("pricing_tier"),
        "challenger_price_status": challenger_close.get("status"),
        "edge_1m_pct": edge_1m,
        "edge_3m_pct": edge_3m,
        "pricing_complete": complete,
        "valuation_grade_pricing_complete": valuation_complete,
        "is_priority_duel": (holding, challenger) in PRIORITY_DUEL_PAIRS,
        "decision_code": decision_code,
        "decision": decision_label(decision_code, "en"),
        "required_trigger_code": trigger_code,
        "required_trigger": trigger_label(trigger_code, "en"),
        "source": source,
    }
    row["pricing_basis"] = _pricing_basis(current_close, challenger_close)
    return row


def _strategic_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = _rs_metrics(state)
    holdings = {_ticker(p.get("ticker")) for p in state.get("positions", []) or []}
    rows: list[dict[str, Any]] = []
    for holding, challengers in _target_map().items():
        if holding not in holdings:
            continue
        for challenger in challengers:
            edge_1m = _return_edge(metrics, challenger, holding, "return_1m_pct")
            edge_3m = _return_edge(metrics, challenger, holding, "return_3m_pct")
            rows.append(_row_payload(state, holding, challenger, edge_1m, edge_3m, "strategic_target_map"))
    return rows


def _lane_rows(state: dict[str, Any], existing: set[tuple[str, str]]) -> list[dict[str, Any]]:
    lanes = state.get("lane_assessment", {}).get("assessed_lanes", []) or []
    rows: list[dict[str, Any]] = []
    for lane in lanes:
        holding = _ticker(lane.get("direct_rs_vs_holding"))
        challenger = _ticker(lane.get("primary_etf"))
        if not holding or not challenger or holding == challenger:
            continue
        key = (holding, challenger)
        if key in existing:
            continue
        existing.add(key)
        rows.append(_row_payload(state, holding, challenger, lane.get("direct_rs_vs_holding_1m_pct"), lane.get("direct_rs_vs_holding_3m_pct"), "lane_artifact_direct_rs"))
    return rows


def _row_rank(row: dict[str, Any]) -> tuple[int, int, int, int, int, float, str]:
    priority_rank = 0 if row.get("is_priority_duel") else 1
    source_rank = 0 if row.get("source") == "strategic_target_map" else 1
    funding_rank = 0 if row.get("valuation_grade_pricing_complete") else 1
    holding = _ticker(row.get("current_holding"))
    holding_rank = STRATEGIC_HOLDING_RANK.get(holding, 99)
    edge = _num(row.get("edge_3m_pct"))
    missing_edge_rank = 1 if edge is None else 0
    edge_value = edge if edge is not None else -999.0
    return (priority_rank, source_rank, funding_rank, holding_rank, missing_edge_rank, -edge_value, _ticker(row.get("challenger")))


def replacement_duel_v2_rows(state: dict[str, Any], limit: int = INVESTOR_REPLACEMENT_DUEL_LIMIT) -> list[dict[str, Any]]:
    rows = _strategic_rows(state)
    existing = {(_ticker(row.get("current_holding")), _ticker(row.get("challenger"))) for row in rows}
    rows.extend(_lane_rows(state, existing))
    return sorted(rows, key=_row_rank)[:limit]


def replacement_duel_v2_markdown(state: dict[str, Any], language: str = "en") -> str:
    if language == "nl":
        lines = ["<!-- ETF_REPLACEMENT_DUEL_V2_EMBEDDED -->", "| Huidige positie | Alternatief | 1m relatieve sterkte | 3m relatieve sterkte | Prijsbasis | Beoordeling | Benodigde bevestiging |", "|---|---|---:|---:|---|---|---|"]
    else:
        lines = ["<!-- ETF_REPLACEMENT_DUEL_V2_EMBEDDED -->", "| Current holding | Challenger | 1m edge | 3m edge | Pricing basis | Decision | Required trigger |", "|---|---|---:|---:|---|---|---|"]
    for row in replacement_duel_v2_rows(state):
        lines.append(
            f"| {row['current_holding']} | {row['challenger']} | "
            f"{_edge_text(row.get('edge_1m_pct'))} | {_edge_text(row.get('edge_3m_pct'))} | "
            f"{localized_pricing_basis(row, language)} | "
            f"{decision_label(str(row.get('decision_code')), language)} | "
            f"{trigger_label(str(row.get('required_trigger_code')), language)} |"
        )
    return "\n".join(lines)


def replacement_duel_v2_html(state: dict[str, Any], base: Any, language: str = "en") -> str:
    def anchor(ticker: str) -> str:
        try:
            return base.ticker_anchor_html(ticker)
        except Exception:
            url = f"https://www.tradingview.com/chart/?symbol={escape(ticker)}"
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{escape(ticker)}</a>'

    labels = {"en": ["Current holding", "Challenger", "1m edge", "3m edge", "Pricing basis", "Decision", "Required trigger"], "nl": ["Huidige positie", "Alternatief", "1m relatieve sterkte", "3m relatieve sterkte", "Prijsbasis", "Beoordeling", "Benodigde bevestiging"]}.get(language, ["Current holding", "Challenger", "1m edge", "3m edge", "Pricing basis", "Decision", "Required trigger"])

    body = []
    for row in replacement_duel_v2_rows(state):
        row_class = " priority-duel" if row.get("is_priority_duel") else ""
        body.append(
            f"<tr class='{row_class.strip()}'>"
            f"<td>{anchor(str(row['current_holding']))}</td>"
            f"<td>{anchor(str(row['challenger']))}</td>"
            f"<td class='num'>{escape(_edge_text(row.get('edge_1m_pct')))}</td>"
            f"<td class='num'>{escape(_edge_text(row.get('edge_3m_pct')))}</td>"
            f"<td>{escape(localized_pricing_basis(row, language))}</td>"
            f"<td>{escape(decision_label(str(row.get('decision_code')), language))}</td>"
            f"<td>{escape(trigger_label(str(row.get('required_trigger_code')), language))}</td>"
            "</tr>"
        )
    return "".join(["<table class='data-table replacement-duel-v2-table'>", "<thead><tr>" + "".join(f"<th>{escape(label)}</th>" for label in labels) + "</tr></thead>", "<tbody>", "".join(body), "</tbody></table>"])
