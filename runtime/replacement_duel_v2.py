from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

import yaml

DEFAULT_TARGET_MAP: dict[str, list[str]] = {
    "SPY": ["QUAL", "IEFA", "EFA", "IWM"],
    "PPA": ["ITA", "DFEN", "NATO"],
    "PAVE": ["GRID", "XLU", "VPU"],
    "GLD": ["GSG", "DBC", "BIL"],
    "URNM": ["URA", "NLR", "NUCL"],
    "SMH": ["SOXX", "IRBO", "BOTZ", "ROBO"],
}

STRATEGIC_HOLDING_ORDER = ["SPY", "PPA", "PAVE", "GLD", "URNM", "SMH"]
STRATEGIC_HOLDING_RANK = {ticker: idx for idx, ticker in enumerate(STRATEGIC_HOLDING_ORDER)}
DEFAULT_MACRO_CONTEXT = Path("config/etf_macro_fundamental_context.yml")
DEFAULT_RS_PATH = Path("output/market_history/etf_relative_strength.json")


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


def _return_edge(metrics: dict[str, Any], challenger: str, holding: str, key: str) -> float | None:
    challenger_return = (metrics.get(challenger) or {}).get(key)
    holding_return = (metrics.get(holding) or {}).get(key)
    try:
        if challenger_return is None or holding_return is None:
            return None
        return round(float(challenger_return) - float(holding_return), 2)
    except (TypeError, ValueError):
        return None


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


def _strategic_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    prices = _index_prices(state)
    metrics = _rs_metrics(state)
    holdings = {_ticker(p.get("ticker")) for p in state.get("positions", []) or []}
    rows: list[dict[str, Any]] = []
    for holding, challengers in _target_map().items():
        if holding not in holdings:
            continue
        for challenger in challengers:
            price = prices.get(challenger) or {}
            edge_1m = _return_edge(metrics, challenger, holding, "return_1m_pct")
            edge_3m = _return_edge(metrics, challenger, holding, "return_3m_pct")
            rows.append(
                {
                    "current_holding": holding,
                    "challenger": challenger,
                    "edge_1m_pct": edge_1m,
                    "edge_3m_pct": edge_3m,
                    "pricing_status": _pricing_status(challenger, price),
                    "decision": _decision(price, edge_1m, edge_3m),
                    "source": "strategic_target_map",
                }
            )
    return rows


def _lane_rows(state: dict[str, Any], existing: set[tuple[str, str]]) -> list[dict[str, Any]]:
    prices = _index_prices(state)
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
        price = prices.get(challenger) or {}
        edge_1m = lane.get("direct_rs_vs_holding_1m_pct")
        edge_3m = lane.get("direct_rs_vs_holding_3m_pct")
        rows.append(
            {
                "current_holding": holding,
                "challenger": challenger,
                "edge_1m_pct": edge_1m,
                "edge_3m_pct": edge_3m,
                "pricing_status": _pricing_status(challenger, price),
                "decision": _decision(price, edge_1m, edge_3m),
                "source": "lane_artifact_direct_rs",
            }
        )
    return rows


def _row_rank(row: dict[str, Any]) -> tuple[int, int, int, float, str]:
    source_rank = 0 if row.get("source") == "strategic_target_map" else 1
    holding = _ticker(row.get("current_holding"))
    holding_rank = STRATEGIC_HOLDING_RANK.get(holding, 99)
    try:
        edge = float(row.get("edge_3m_pct"))
    except (TypeError, ValueError):
        edge = -999.0
    missing_edge_rank = 1 if edge == -999.0 else 0
    return (source_rank, holding_rank, missing_edge_rank, -edge, _ticker(row.get("challenger")))


def replacement_duel_v2_rows(state: dict[str, Any], limit: int = 16) -> list[dict[str, Any]]:
    rows = _strategic_rows(state)
    existing = {(_ticker(row.get("current_holding")), _ticker(row.get("challenger"))) for row in rows}
    rows.extend(_lane_rows(state, existing))
    return sorted(rows, key=_row_rank)[:limit]


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
