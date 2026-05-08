from __future__ import annotations

from html import escape
from typing import Any

DEFAULT_TARGET_MAP: dict[str, list[str]] = {
    "SPY": ["QUAL", "IEFA", "EFA", "IWM"],
    "PPA": ["ITA", "DFEN", "NATO"],
    "PAVE": ["GRID", "XLU", "VPU"],
    "GLD": ["GSG", "DBC", "BIL"],
    "URNM": ["URA", "NLR", "NUCL"],
    "SMH": ["SOXX", "IRBO", "BOTZ", "ROBO"],
}


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "n/a"


def _edge_text(value: Any) -> str:
    try:
        value_f = float(value)
    except (TypeError, ValueError):
        return "n/a"
    sign = "+" if value_f > 0 else ""
    return f"{sign}{value_f:.2f}%"


def _index_prices(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in state.get("pricing", []) or []:
        symbol = _ticker(item.get("symbol"))
        if symbol:
            out[symbol] = item
    return out


def _lane_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    prices = _index_prices(state)
    lanes = state.get("lane_assessment", {}).get("assessed_lanes", []) or []
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for lane in lanes:
        holding = _ticker(lane.get("direct_rs_vs_holding"))
        challenger = _ticker(lane.get("primary_etf"))
        if not holding or not challenger or holding == challenger:
            continue
        key = (holding, challenger)
        if key in seen:
            continue
        seen.add(key)
        price = prices.get(challenger) or {}
        rows.append(
            {
                "current_holding": holding,
                "challenger": challenger,
                "edge_1m_pct": lane.get("direct_rs_vs_holding_1m_pct"),
                "edge_3m_pct": lane.get("direct_rs_vs_holding_3m_pct"),
                "pricing_status": _pricing_status(challenger, price),
                "decision": _decision(price, lane.get("direct_rs_vs_holding_1m_pct"), lane.get("direct_rs_vs_holding_3m_pct")),
                "source": "lane_artifact_direct_rs",
            }
        )
    return rows


def _fallback_rows(state: dict[str, Any], existing_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prices = _index_prices(state)
    holdings = {_ticker(p.get("ticker")) for p in state.get("positions", []) or []}
    existing = {(_ticker(row.get("current_holding")), _ticker(row.get("challenger"))) for row in existing_rows}
    rows: list[dict[str, Any]] = []

    for holding, challengers in DEFAULT_TARGET_MAP.items():
        if holding not in holdings:
            continue
        for challenger in challengers:
            key = (holding, challenger)
            if key in existing:
                continue
            price = prices.get(challenger) or {}
            rows.append(
                {
                    "current_holding": holding,
                    "challenger": challenger,
                    "edge_1m_pct": None,
                    "edge_3m_pct": None,
                    "pricing_status": _pricing_status(challenger, price),
                    "decision": "Mapped challenger; direct relative-strength evidence not yet available.",
                    "source": "fallback_target_map",
                }
            )
    return rows


def _pricing_status(challenger: str, price: dict[str, Any]) -> str:
    if not price:
        return "not priced in latest audit"
    returned_date = price.get("returned_close_date") or price.get("date") or "latest verified close"
    px = _f2(price.get("price"))
    if px == "n/a":
        return "pricing row present but close missing"
    return f"priced {px} ({returned_date})"


def _decision(price: dict[str, Any], edge_1m: Any, edge_3m: Any) -> str:
    if not price or price.get("price") is None:
        return "Not fundable — close missing."
    try:
        e1 = None if edge_1m is None else float(edge_1m)
        e3 = None if edge_3m is None else float(edge_3m)
    except (TypeError, ValueError):
        e1, e3 = None, None
    if e1 is None and e3 is None:
        return "Priced, but direct RS duel incomplete."
    if e3 is not None and e3 >= 5.0:
        return "Replacement trigger watch — challenger leading over 3m."
    if e3 is not None and e3 > 0:
        return "Challenger improving; keep duel active."
    if e1 is not None and e1 > 0 and (e3 is None or e3 <= 0):
        return "Early 1m improvement only; wait for 3m confirmation."
    return "Current holding still leads; no replacement."


def replacement_duel_v2_rows(state: dict[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    rows = _lane_rows(state)
    rows.extend(_fallback_rows(state, rows))

    def sort_key(row: dict[str, Any]) -> tuple[int, float, str, str]:
        has_direct = 0 if row.get("source") == "lane_artifact_direct_rs" else 1
        try:
            edge = float(row.get("edge_3m_pct"))
        except (TypeError, ValueError):
            edge = -999.0
        return (has_direct, -edge, str(row.get("current_holding")), str(row.get("challenger")))

    return sorted(rows, key=sort_key)[:limit]


def replacement_duel_v2_markdown(state: dict[str, Any]) -> str:
    lines = [
        "| Current holding | Challenger | 1m edge | 3m edge | Pricing status | Decision |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in replacement_duel_v2_rows(state):
        lines.append(
            f"| {row['current_holding']} | {row['challenger']} | {_edge_text(row.get('edge_1m_pct'))} | "
            f"{_edge_text(row.get('edge_3m_pct'))} | {row['pricing_status']} | {row['decision']} |"
        )
    return "\n".join(lines)


def replacement_duel_v2_html(state: dict[str, Any], base: Any) -> str:
    def anchor(ticker: str) -> str:
        try:
            return base.ticker_anchor_html(ticker)
        except Exception:
            url = f"https://www.tradingview.com/chart/?symbol={escape(ticker)}"
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{escape(ticker)}</a>'

    body = []
    for row in replacement_duel_v2_rows(state):
        body.append(
            "<tr>"
            f"<td>{anchor(str(row['current_holding']))}</td>"
            f"<td>{anchor(str(row['challenger']))}</td>"
            f"<td class='num'>{escape(_edge_text(row.get('edge_1m_pct')))}</td>"
            f"<td class='num'>{escape(_edge_text(row.get('edge_3m_pct')))}</td>"
            f"<td>{escape(str(row['pricing_status']))}</td>"
            f"<td>{escape(str(row['decision']))}</td>"
            "</tr>"
        )
    return "".join(
        [
            "<table class='data-table replacement-duel-v2-table'>",
            "<thead><tr><th>Current holding</th><th>Challenger</th><th>1m edge</th><th>3m edge</th><th>Pricing status</th><th>Decision</th></tr></thead>",
            "<tbody>",
            "".join(body),
            "</tbody></table>",
        ]
    )
