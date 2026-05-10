from __future__ import annotations

from html import escape
from typing import Any, Callable

from runtime.build_etf_report_state import build_runtime_state
from runtime.render_etf_report_from_state import f2, position_rows
from runtime.replacement_duel_v2 import replacement_duel_v2_html

PRINT_TABLE_PAGINATION_CSS = """
<style id="etf-table-pagination-guard">
  @media print {
    table {
      page-break-inside: auto;
      break-inside: auto;
      border-collapse: collapse;
    }

    thead {
      display: table-header-group;
    }

    tfoot {
      display: table-footer-group;
    }

    tr,
    th,
    td {
      page-break-inside: avoid;
      break-inside: avoid;
    }

    .panel table tr,
    .panel table th,
    .panel table td,
    .data-table tr,
    .action-table tr,
    .rotation-plan-table tr,
    .position-review-table tr,
    .replacement-duel-v2-table tr {
      page-break-inside: avoid;
      break-inside: avoid;
    }
  }
</style>
"""

NL_MARKERS = ["belangrijkste conclusie", "wat is er deze week veranderd", "beschikbare cash", "nederlands"]

LABELS = {
    "en": {
        "portfolio_action_snapshot": "Portfolio Action Snapshot",
        "current_position_review": "Current Position Review",
        "portfolio_rotation_plan": "Portfolio Rotation Plan",
        "replacement_duel_table": "Replacement Duel Table",
        "recommendation": "Recommendation",
        "tickers_notes": "Tickers / notes",
        "add": "Add",
        "hold": "Hold",
        "hold_replaceable": "Hold but replaceable",
        "reduce": "Reduce",
        "close": "Close",
        "replaceable_note": "remain under explicit review.",
        "best_replacements": "Best replacements to fund",
        "best_replacements_note": "No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel.",
        "ticker": "Ticker",
        "action": "Action",
        "score": "Score",
        "fresh_cash": "Fresh cash",
        "role": "Role",
        "required_next_action": "Required next action",
        "replace": "Replace",
    },
    "nl": {
        "portfolio_action_snapshot": "Portefeuille-acties",
        "current_position_review": "Review huidige posities",
        "portfolio_rotation_plan": "Rotatieplan portefeuille",
        "replacement_duel_table": "Vervangingsanalyse",
        "recommendation": "Advies",
        "tickers_notes": "Tickers / toelichting",
        "add": "Toevoegen",
        "hold": "Aanhouden",
        "hold_replaceable": "Aanhouden, maar vervangbaar",
        "reduce": "Verlagen",
        "close": "Sluiten",
        "replaceable_note": "blijven expliciet onder review.",
        "best_replacements": "Beste alternatieven om te financieren",
        "best_replacements_note": "Nog geen alternatief is sterk genoeg om direct te financieren. Elk genoemd alternatief moet eerst dezelfde prijsbasis en relatieve-sterkteanalyse doorstaan.",
        "ticker": "Ticker",
        "action": "Actie",
        "score": "Score",
        "fresh_cash": "Vers kapitaal",
        "role": "Rol",
        "required_next_action": "Volgende toets",
        "replace": "Vervangen",
    },
}


def _language(md_text: str) -> str:
    lower = md_text.lower()
    return "nl" if any(marker in lower for marker in NL_MARKERS) or "weekly_analysis_pro_nl" in lower else "en"


def _labels(language: str) -> dict[str, str]:
    return LABELS.get(language, LABELS["en"])


def _clean(value: Any) -> str:
    return str(value or "").strip() or "None"


def _compact(value: Any, max_len: int = 90) -> str:
    raw = _clean(value)
    if len(raw) <= max_len:
        return raw
    return raw[: max_len - 1].rstrip() + "…"


def _is_add(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    executed = _clean(p.get("action_executed_this_run")).lower()
    shares_delta = float(p.get("shares_delta_this_run") or 0.0)
    return "add" in action or "buy" in executed or shares_delta > 0


def _is_hold(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    return "hold" in action and not _is_add(p)


def _is_replace(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    better = _clean(p.get("better_alternative_exists")).lower()
    return better == "yes" or "review" in action or "replace" in action


def _is_reduce(p: dict[str, Any]) -> bool:
    return "reduce" in _clean(p.get("suggested_action")).lower()


def _is_close(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action")).lower()
    return "close" in action or "sell" in action


def _ticker_anchor(base: Any, ticker: str) -> str:
    ticker = ticker.strip().upper()
    if not ticker or ticker == "NONE":
        return "None"
    try:
        return base.ticker_anchor_html(ticker)
    except Exception:
        url = f"https://www.tradingview.com/chart/?symbol={escape(ticker)}"
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{escape(ticker)}</a>'


def _ticker_join(base: Any, tickers: list[str]) -> str:
    values = [t.strip().upper() for t in tickers if t and t.strip().upper() != "NONE"]
    return ", ".join(_ticker_anchor(base, t) for t in values) if values else "None"


def _section_header(base: Any, number: int, title: str) -> str:
    try:
        return base.section_header_html(number, title)
    except Exception:
        return f"<h2>{escape(title)}</h2>"


def _classified_positions(state: dict[str, Any]) -> dict[str, list[str]]:
    positions = position_rows(state)
    return {
        "add": [str(p.get("ticker", "")).upper() for p in positions if _is_add(p)],
        "hold": [str(p.get("ticker", "")).upper() for p in positions if _is_hold(p) or _is_add(p)],
        "replace": [str(p.get("ticker", "")).upper() for p in positions if _is_replace(p)],
        "reduce": [str(p.get("ticker", "")).upper() for p in positions if _is_reduce(p)],
        "close": [str(p.get("ticker", "")).upper() for p in positions if _is_close(p)],
    }


def _action_snapshot_html(base: Any, state: dict[str, Any], language: str) -> str:
    classified = _classified_positions(state)
    l = _labels(language)

    return "".join([
        "<div class='panel panel-action-snapshot'>",
        _section_header(base, 2, l["portfolio_action_snapshot"]),
        "<table class='action-table'><thead><tr>"
        f"<th>{escape(l['recommendation'])}</th><th>{escape(l['tickers_notes'])}</th></tr></thead><tbody>",
        f"<tr><th>{escape(l['add'])}</th><td>{_ticker_join(base, classified['add'])}</td></tr>",
        f"<tr><th>{escape(l['hold'])}</th><td>{_ticker_join(base, classified['hold'])}</td></tr>",
        f"<tr><th>{escape(l['hold_replaceable'])}</th><td>{_ticker_join(base, classified['replace'])} {escape(l['replaceable_note'])}</td></tr>",
        f"<tr><th>{escape(l['reduce'])}</th><td>{_ticker_join(base, classified['reduce'])}</td></tr>",
        f"<tr><th>{escape(l['close'])}</th><td>{_ticker_join(base, classified['close'])}</td></tr>",
        "</tbody></table>",
        f"<div class='note-box'><h4>{escape(l['best_replacements'])}</h4>",
        f"<ul><li>{escape(l['best_replacements_note'])}</li></ul>",
        "</div></div>",
    ])


def _position_review_html(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    rows: list[str] = []
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        rows.append(
            "<tr>"
            f"<td>{_ticker_anchor(base, ticker)}</td>"
            f"<td>{escape(_clean(p.get('suggested_action')))}</td>"
            f"<td class='num'>{escape(f2(p.get('total_score')) or 'n/a')}</td>"
            f"<td>{escape(_clean(p.get('fresh_cash_test')))}</td>"
            f"<td>{escape(_compact(p.get('portfolio_role'), 55))}</td>"
            f"<td>{escape(_compact(p.get('required_next_action'), 95))}</td>"
            "</tr>"
        )

    return "".join([
        "<div class='panel panel-position-review'>",
        _section_header(base, 3, l["current_position_review"]),
        "<table class='data-table position-review-table'>",
        "<thead><tr>"
        f"<th>{escape(l['ticker'])}</th><th>{escape(l['action'])}</th><th>{escape(l['score'])}</th><th>{escape(l['fresh_cash'])}</th><th>{escape(l['role'])}</th><th>{escape(l['required_next_action'])}</th></tr></thead>",
        "<tbody>",
        "".join(rows),
        "</tbody></table></div>",
    ])


def _rotation_plan_html(base: Any, state: dict[str, Any], language: str) -> str:
    classified = _classified_positions(state)
    l = _labels(language)
    return "".join([
        "<div class='panel panel-rotation-plan'>",
        _section_header(base, 5, l["portfolio_rotation_plan"]),
        "<table class='data-table rotation-plan-table'>",
        "<thead><tr>"
        f"<th>{escape(l['close'])}</th><th>{escape(l['reduce'])}</th><th>{escape(l['hold'])}</th><th>{escape(l['add'])}</th><th>{escape(l['replace'])}</th></tr></thead>",
        "<tbody><tr>",
        f"<td>{_ticker_join(base, classified['close'])}</td>",
        f"<td>{_ticker_join(base, classified['reduce'])}</td>",
        f"<td>{_ticker_join(base, classified['hold'])}</td>",
        f"<td>{_ticker_join(base, classified['add'])}</td>",
        f"<td>{_ticker_join(base, classified['replace'])}</td>",
        "</tr></tbody></table>",
        "</div>",
    ])


def _replacement_duel_panel(base: Any, state: dict[str, Any], language: str) -> str:
    l = _labels(language)
    return "".join([
        "<div class='panel panel-replacement-duel'>",
        _section_header(base, 11, l["replacement_duel_table"]),
        replacement_duel_v2_html(state, base, language=language),
        "</div>",
    ])


def _replace_panel_by_title(html: str, titles: list[str], replacement: str) -> str:
    label_idx = -1
    for title in titles:
        marker_options = [
            f"<span class='section-label'>{escape(title)}</span>",
            f'<span class="section-label">{escape(title)}</span>',
            escape(title),
        ]
        for marker in marker_options:
            label_idx = html.find(marker)
            if label_idx != -1:
                break
        if label_idx != -1:
            break
    if label_idx == -1:
        return html

    starts = [html.rfind("<div class='panel", 0, label_idx), html.rfind('<div class="panel', 0, label_idx)]
    start = max(starts)
    if start == -1:
        return html

    next_candidates = []
    for token in ("<div class='panel", '<div class="panel'):
        pos = html.find(token, label_idx + 1)
        if pos != -1:
            next_candidates.append(pos)
    end = min(next_candidates) if next_candidates else html.find("</body>", label_idx)
    if end == -1:
        end = len(html)
    return html[:start] + replacement + html[end:]


def _append_replacement_duel_after_best_opportunities(html: str, base: Any, state: dict[str, Any], language: str) -> str:
    if "replacement-duel-v2-table" in html:
        return html.replace("Replacement Duel Table v2", _labels(language)["replacement_duel_table"])
    marker_options = ["Best New Opportunities", "Beste nieuwe kansen"]
    idx = -1
    marker_len = 0
    for marker in marker_options:
        idx = html.find(marker)
        if idx != -1:
            marker_len = len(marker)
            break
    if idx == -1:
        return html
    next_candidates = []
    for token in ("<div class='panel", '<div class="panel'):
        pos = html.find(token, idx + marker_len)
        if pos != -1:
            next_candidates.append(pos)
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


def apply_etf_delivery_html_overrides(html: str, base: Any, md_text: str) -> str:
    language = _language(md_text)
    try:
        state = build_runtime_state()
    except Exception:
        return _inject_print_table_pagination_css(html)

    html = _replace_panel_by_title(html, ["Portfolio Action Snapshot", "Portefeuille-acties"], _action_snapshot_html(base, state, language))
    html = _replace_panel_by_title(html, ["Current Position Review", "Review huidige posities"], _position_review_html(base, state, language))
    html = _replace_panel_by_title(html, ["Portfolio Rotation Plan", "Rotatieplan portefeuille"], _rotation_plan_html(base, state, language))
    html = _append_replacement_duel_after_best_opportunities(html, base, state, language)
    html = html.replace("Replacement Duel Table v2", _labels(language)["replacement_duel_table"])
    return _inject_print_table_pagination_css(html)


def build_report_html_with_state(base_build_report_html: Callable[..., str], base: Any) -> Callable[..., str]:
    def _wrapped(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
        html = base_build_report_html(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
        return apply_etf_delivery_html_overrides(html, base, md_text)

    return _wrapped
