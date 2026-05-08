from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report as report_module
from runtime.build_etf_report_state import build_runtime_state
from runtime.delivery_html_overrides import build_report_html_with_state

report_module.build_report_html = build_report_html_with_state(
    report_module.build_report_html,
    report_module._base,
)

RAW_MARKDOWN_LINK_RE = re.compile(r"\[[A-Z][A-Z0-9.-]{0,14}\]\(https?://[^\)]+\)")


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _current_holdings_from_state() -> list[str]:
    state = build_runtime_state()
    tickers: list[str] = []
    for position in state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if ticker and ticker != "CASH" and ticker not in tickers:
            tickers.append(ticker)
    if not tickers:
        raise RuntimeError("Delivery HTML contract validation failed: no current holdings found in runtime state.")
    return tickers


def _latest_reports(output_dir: Path) -> list[Path]:
    latest_en = report_module.latest_report_file(output_dir, mode="pro")
    reports = [latest_en]
    if report_module.has_matching_dutch_report(latest_en):
        reports.append(report_module.matching_dutch_report_path(latest_en))
    return reports


def _report_date_from_filename(path: Path) -> str:
    match = re.search(r"(\d{6})(?:_\d{2})?\.md$", path.name)
    if not match:
        return "unknown"
    suffix = match.group(1)
    return f"20{suffix[:2]}-{suffix[2:4]}-{suffix[4:6]}"


def _render_delivery_html(report_path: Path) -> str:
    md_text = report_path.read_text(encoding="utf-8")
    return report_module.build_report_html(
        md_text,
        _report_date_from_filename(report_path),
        image_src=None,
        render_mode="email",
    )


def _anchor_for_ticker_exists(html: str, ticker: str) -> bool:
    ticker = re.escape(ticker)
    patterns = [
        rf"<a\b[^>]*href=[\"'][^\"']*TradingView[^\"']*symbol={ticker}[^\"']*[\"'][^>]*>\s*{ticker}\s*</a>",
        rf"<a\b[^>]*href=[\"'][^\"']*tradingview\.com/chart/\?symbol={ticker}[^\"']*[\"'][^>]*>\s*{ticker}\s*</a>",
    ]
    return any(re.search(pattern, html, flags=re.IGNORECASE) for pattern in patterns)


def _section_panel(html: str, title: str) -> str:
    idx = html.find(title)
    if idx == -1:
        raise RuntimeError(f"Delivery HTML contract validation failed: missing section title: {title}")
    start_candidates = [html.rfind("<div class='panel", 0, idx), html.rfind('<div class="panel', 0, idx)]
    start = max(start_candidates)
    if start == -1:
        start = max(0, idx - 500)
    end_candidates = []
    for token in ("<div class='panel", '<div class="panel'):
        pos = html.find(token, idx + len(title))
        if pos != -1:
            end_candidates.append(pos)
    end = min(end_candidates) if end_candidates else len(html)
    return html[start:end]


def _validate_no_raw_markdown_links(html: str, report_name: str) -> None:
    match = RAW_MARKDOWN_LINK_RE.search(html)
    if match:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: raw markdown link found: {match.group(0)}"
        )


def _validate_action_snapshot(html: str, report_name: str, holdings: list[str]) -> None:
    panel = _section_panel(html, "Portfolio Action Snapshot")
    if "action-table" not in panel:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: action snapshot table missing.")
    missing = [ticker for ticker in holdings if not _anchor_for_ticker_exists(panel, ticker)]
    if missing:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: action snapshot missing TradingView anchors for: {', '.join(missing)}"
        )


def _validate_position_review(html: str, report_name: str, holdings: list[str]) -> None:
    panel = _section_panel(html, "Current Position Review")
    required_bits = [
        "position-review-table",
        ">Ticker<",
        ">Action<",
        ">Score<",
        ">Fresh cash<",
        ">Role<",
        ">Required next action<",
    ]
    missing_bits = [bit for bit in required_bits if bit not in panel]
    if missing_bits:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Current Position Review table missing required HTML bits: {', '.join(missing_bits)}"
        )
    missing = [ticker for ticker in holdings if not _anchor_for_ticker_exists(panel, ticker)]
    if missing:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Current Position Review missing TradingView anchors for: {', '.join(missing)}"
        )


def validate(output_dir: Path) -> None:
    holdings = _current_holdings_from_state()
    reports = _latest_reports(output_dir)
    for report_path in reports:
        html = _render_delivery_html(report_path)
        _validate_no_raw_markdown_links(html, report_path.name)
        _validate_action_snapshot(html, report_path.name, holdings)
        _validate_position_review(html, report_path.name, holdings)
        print(f"ETF_DELIVERY_HTML_CONTRACT_OK | report={report_path.name} | dynamic_holdings={','.join(holdings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
