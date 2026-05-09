from __future__ import annotations

import argparse
import os
import re
import sys
from html import unescape
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report as report_module
from runtime.build_etf_report_state import build_runtime_state
from runtime.delivery_html_overrides import build_report_html_with_state

report_module.build_report_html = build_report_html_with_state(report_module.build_report_html, report_module._base)

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
RAW_MARKDOWN_LINK_RE = re.compile(r"\[[A-Z][A-Z0-9.-]{0,14}\]\(https?://[^\)]+\)")
FORBIDDEN_CONTENT_TOKENS = [
    "Placeholder for runtime replacement",
    "runtime rebuild required",
    "Pending classification",
    "None / None:",
]
STRICT_TITLES = [
    "Portfolio Action Snapshot",
    "Regime Dashboard",
    "Structural Opportunity Radar",
    "Key Risks / Invalidators",
    "Equity Curve and Portfolio Development",
    "Asset Allocation Map",
    "Second-Order Effects Map",
    "Current Position Review",
    "Final Action Table",
    "Current Portfolio Holdings and Cash",
    "Continuity Input for Next Run",
    "Replacement Duel Table v2",
]


def _canonical_report_key(path: Path) -> tuple[str, int] | None:
    match = PRO_REPORT_RE.match(path.name)
    if not match:
        return None
    return match.group(1), int(match.group(2) or "1")


def _explicit_report_path() -> Path | None:
    raw = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.exists():
        raise RuntimeError(f"Explicit report path does not exist: {path}")
    if _canonical_report_key(path) is None:
        raise RuntimeError(f"Explicit report path is not a canonical English ETF pro report: {path}")
    return path


def _latest_canonical_english_report(output_dir: Path) -> Path:
    explicit = _explicit_report_path()
    if explicit is not None:
        return explicit
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        key = _canonical_report_key(path)
        if key is not None:
            candidates.append((key[0], key[1], path))
    if not candidates:
        raise RuntimeError(f"No canonical English ETF pro reports found in {output_dir}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def _latest_reports(output_dir: Path) -> list[Path]:
    latest_en = _latest_canonical_english_report(output_dir)
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
    return report_module.build_report_html(md_text, _report_date_from_filename(report_path), image_src=None, render_mode="email")


def _strip_html(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", value)).strip()


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _current_holdings_from_state(state: dict[str, Any]) -> list[str]:
    tickers: list[str] = []
    for position in state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if ticker and ticker != "CASH" and ticker not in tickers:
            tickers.append(ticker)
    if not tickers:
        raise RuntimeError("Delivery HTML contract validation failed: no current holdings found in runtime state.")
    return tickers


def _anchor_for_ticker_exists(html: str, ticker: str) -> bool:
    ticker_re = re.escape(ticker)
    return bool(re.search(rf"<a\b[^>]*href=[\"'][^\"']*tradingview\.com/chart/\?symbol={ticker_re}[^\"']*[\"'][^>]*>\s*{ticker_re}\s*</a>", html, flags=re.IGNORECASE))


def _section_between_titles(html: str, start_title: str, end_titles: list[str]) -> str:
    start = html.find(start_title)
    if start == -1:
        raise RuntimeError(f"Delivery HTML contract validation failed: missing section title: {start_title}")
    candidates = [html.find(title, start + len(start_title)) for title in end_titles]
    candidates = [idx for idx in candidates if idx != -1]
    end = min(candidates) if candidates else len(html)
    return html[start:end]


def _validate_no_forbidden_content(html: str, report_name: str) -> None:
    lower = html.lower()
    for token in FORBIDDEN_CONTENT_TOKENS:
        if token.lower() in lower:
            raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: forbidden placeholder token found: {token!r}")
    match = RAW_MARKDOWN_LINK_RE.search(html)
    if match:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: raw markdown link found: {match.group(0)}")


def _validate_required_titles(html: str, report_name: str) -> None:
    plain = _strip_html(html)
    missing = [title for title in STRICT_TITLES if title not in plain]
    if missing:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing rendered section titles: {', '.join(missing)}")


def _validate_structural_radar(html: str, report_name: str) -> None:
    section = _section_between_titles(html, "Structural Opportunity Radar", ["Short Opportunity Radar", "Key Risks / Invalidators"])
    plain = _strip_html(section).lower()
    if len(plain) < 240:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar is too thin after rendering.")
    if "placeholder" in plain or "runtime replacement" in plain:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar still contains placeholder text.")


def _validate_strict_tables_and_anchors(html: str, report_name: str, holdings: list[str]) -> None:
    required_classes = ["action-table", "position-review-table", "rotation-plan-table", "replacement-duel-v2-table"]
    missing_classes = [klass for klass in required_classes if klass not in html]
    if missing_classes:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing strict delivery table classes: {', '.join(missing_classes)}")
    for ticker in holdings:
        if not _anchor_for_ticker_exists(html, ticker):
            raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing TradingView anchor for current holding {ticker}.")


def validate(output_dir: Path) -> None:
    state = build_runtime_state()
    holdings = _current_holdings_from_state(state)
    reports = _latest_reports(output_dir)
    for report_path in reports:
        html = _render_delivery_html(report_path)
        _validate_no_forbidden_content(html, report_path.name)
        _validate_required_titles(html, report_path.name)
        _validate_structural_radar(html, report_path.name)
        _validate_strict_tables_and_anchors(html, report_path.name, holdings)
        print(f"ETF_DELIVERY_HTML_CONTRACT_OK | report={report_path.name} | dynamic_holdings={','.join(holdings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
