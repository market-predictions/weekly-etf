from __future__ import annotations

from html import escape
from typing import Any, Callable

from runtime.build_etf_report_state import build_runtime_state
from runtime.render_etf_report_from_state import f2, position_rows

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
    .position-review-table tr {
      page-break-inside: avoid;
      break-inside: avoid;
    }
  }
</style>
"""


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


def _action_snapshot_html(base: Any, state: dict[str, Any]) -> str:
    classified = _classified_positions(state)

    return "".join([
        "<div class='panel panel-action-snapshot'>",
        _section_header(base, 2, "Portfolio Action Snapshot"),
        "<table class='action-table'><thead><tr><th>Recommendation</th><th>Tickers / notes</th></tr></thead><tbody>",
        f"<tr><th>Add</th><td>{_ticker_join(base, classified['add'])}</td></tr>",
        f"<tr><th>Hold</th><td>{_ticker_join(base, classified['hold'])}</td></tr>",
        f"<tr><th>Hold but replaceable</th><td>{_ticker_join(base, classified['replace'])} remain under explicit review.</td></tr>",
        f"<tr><th>Reduce</th><td>{_ticker_join(base, classified['reduce'])}</td></tr>",
        f"<tr><th>Close</th><td>{_ticker_join(base, classified['close'])}</td></tr>",
        "</tbody></table>",
        "<div class='note-box'><h4>Best replacements to fund</h4>",
        "<ul><li>No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel.</li></ul>",
        "</div></div>",
    ])


def _position_review_html(base: Any, state: dict[str, Any]) -> str:
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
        _section_header(base, 3, "Current Position Review"),
        "<table class='data-table position-review-table'>",
        "<thead><tr><th>Ticker</th><th>Action</th><th>Score</th><th>Fresh cash</th><th>Role</th><th>Required next action</th></tr></thead>",
        "<tbody>",
        "".join(rows),
        "</tbody></table></div>",
    ])


def _rotation_plan_html(base: Any, state: dict[str, Any]) -> str:
    classified = _classified_positions(state)
    return "".join([
        "<div class='panel panel-rotation-plan'>",
        _section_header(base, 5, "Portfolio Rotation Plan"),
        "<table class='data-table rotation-plan-table'>",
        "<thead><tr><th>Close</th><th>Reduce</th><th>Hold</th><th>Add</th><th>Replace</th></tr></thead>",
        "<tbody><tr>",
        f"<td>{_ticker_join(base, classified['close'])}</td>",
        f"<td>{_ticker_join(base, classified['reduce'])}</td>",
        f"<td>{_ticker_join(base, classified['hold'])}</td>",
        f"<td>{_ticker_join(base, classified['add'])}</td>",
        f"<td>{_ticker_join(base, classified['replace'])}</td>",
        "</tr></tbody></table>",
        "</div>",
    ])


def _replace_panel_by_title(html: str, title: str, replacement: str) -> str:
    marker_options = [
        f"<span class='section-label'>{escape(title)}</span>",
        f'<span class="section-label">{escape(title)}</span>',
        escape(title),
    ]
    label_idx = -1
    for marker in marker_options:
        label_idx = html.find(marker)
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


def _inject_print_table_pagination_css(html: str) -> str:
    if "etf-table-pagination-guard" in html:
        return html
    if "</head>" in html:
        return html.replace("</head>", PRINT_TABLE_PAGINATION_CSS + "\n</head>", 1)
    return PRINT_TABLE_PAGINATION_CSS + html


def apply_etf_delivery_html_overrides(html: str, base: Any, md_text: str) -> str:
    try:
        state = build_runtime_state()
    except Exception:
        return _inject_print_table_pagination_css(html)

    html = _replace_panel_by_title(html, "Portfolio Action Snapshot", _action_snapshot_html(base, state))
    html = _replace_panel_by_title(html, "Current Position Review", _position_review_html(base, state))
    html = _replace_panel_by_title(html, "Portfolio Rotation Plan", _rotation_plan_html(base, state))
    return _inject_print_table_pagination_css(html)


def build_report_html_with_state(base_build_report_html: Callable[..., str], base: Any) -> Callable[..., str]:
    def _wrapped(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
        html = base_build_report_html(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
        return apply_etf_delivery_html_overrides(html, base, md_text)

    return _wrapped
