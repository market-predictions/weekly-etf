from __future__ import annotations

import re
from typing import Any

import send_report as _sr

TICKERS = {
    "SPY", "SMH", "PPA", "PAVE", "URNM", "GLD",
    "SOXX", "ITA", "GRID", "URA", "IEFA", "EFA",
    "IWM", "KWEB", "TLT", "ICLN",
    "QUAL", "GSG", "BIL", "MOO", "FIW", "INDA", "XBI", "FINX",
    "CIBR", "BUG", "REMX", "PICK", "XLU", "VPU", "NLR", "NUCL",
    "DBA", "CORN", "PHO", "CGW", "MCHI", "FXI", "EPI", "IBB",
    "XLV", "VHT", "KCE", "IAI", "BOTZ", "ROBO", "IRBO", "COPX",
    "DBC", "DFEN", "NATO",
}

ORIGINAL_BUILD_REPORT_HTML = _sr.build_report_html


def _tv_url(ticker: str) -> str:
    return f"https://www.tradingview.com/chart/?symbol={ticker}"


def _anchor(ticker: str) -> str:
    return f'<a href="{_tv_url(ticker)}" target="_blank" rel="noopener noreferrer">{ticker}</a>'


def _escape(text: Any) -> str:
    raw = str(text or "")
    return raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _section_lines(md_text: str, number: int) -> list[str]:
    lines = md_text.splitlines()
    out: list[str] = []
    in_section = False
    section_re = re.compile(r"^##\s+(\d+)\.")
    for line in lines:
        m = section_re.match(line.strip())
        if m:
            if int(m.group(1)) == number:
                in_section = True
                out.append(line)
                continue
            if in_section:
                break
        elif in_section:
            out.append(line)
    return out


def _parse_position_review(md_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in _section_lines(md_text, 10):
        clean = line.strip()
        if not clean.startswith("### "):
            continue
        # Example: ### SPY — Hold — Score 3.53 — Fresh cash: Smaller / under review
        payload = clean[4:].strip()
        parts = [p.strip() for p in payload.split("—")]
        if len(parts) < 4:
            continue
        ticker = parts[0].strip()
        if ticker not in TICKERS:
            continue
        action = parts[1].strip()
        score = parts[2].replace("Score", "").strip()
        fresh = parts[3].replace("Fresh cash:", "").strip()
        rows.append({"ticker": ticker, "action": action, "score": score, "fresh_cash": fresh})
    return rows


def _position_review_table(md_text: str) -> str:
    rows = _parse_position_review(md_text)
    if not rows:
        return ""
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{_anchor(row['ticker'])}</td>"
            f"<td>{_escape(row['action'])}</td>"
            f"<td>{_escape(row['score'])}</td>"
            f"<td>{_escape(row['fresh_cash'])}</td>"
            "</tr>"
        )
    return (
        "<table class='data-table current-position-review-table'>"
        "<thead><tr><th>Ticker</th><th>Action</th><th>Score</th><th>Fresh cash</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def _replace_position_review_panel(html: str, md_text: str) -> str:
    table_html = _position_review_table(md_text)
    if not table_html:
        return html
    heading = "CURRENT POSITION REVIEW"
    idx = html.find(heading)
    if idx == -1:
        return html
    panel_start = html.rfind("<div class='panel", 0, idx)
    if panel_start == -1:
        return html
    header_end = html.find("</table>", idx)
    if header_end == -1:
        return html
    header_end += len("</table>")
    panel_end = html.find("</div>", header_end)
    if panel_end == -1:
        return html
    return html[:header_end] + table_html + html[panel_end:]


def _link_plain_tickers(segment: str) -> str:
    # Work only on visible text portions outside existing anchor tags.
    parts = re.split(r"(<a\b.*?</a>)", segment, flags=re.IGNORECASE | re.DOTALL)
    pattern = re.compile(r"\b(" + "|".join(sorted(TICKERS, key=len, reverse=True)) + r")\b")
    out: list[str] = []
    for part in parts:
        if part.lower().startswith("<a"):
            out.append(part)
        else:
            out.append(pattern.sub(lambda m: _anchor(m.group(1)), part))
    return "".join(out)


def _link_action_snapshot_panel(html: str) -> str:
    heading = "PORTFOLIO ACTION SNAPSHOT"
    idx = html.find(heading)
    if idx == -1:
        return html
    panel_start = html.rfind("<div class='panel", 0, idx)
    if panel_start == -1:
        return html
    panel_end = html.find("</div>", idx)
    if panel_end == -1:
        return html
    fragment = html[panel_start:panel_end]
    linked_fragment = _link_plain_tickers(fragment)
    return html[:panel_start] + linked_fragment + html[panel_end:]


def build_report_html(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
    html = ORIGINAL_BUILD_REPORT_HTML(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
    html = _link_action_snapshot_panel(html)
    html = _replace_position_review_panel(html, md_text)
    return html


_sr.build_report_html = build_report_html

if __name__ == "__main__":
    _sr.main()
