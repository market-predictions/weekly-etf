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
from runtime.client_facing_sanitizer import sanitize_client_facing_html
from runtime.delivery_html_overrides import build_report_html_with_state

report_module.build_report_html = build_report_html_with_state(report_module.build_report_html, report_module._base)

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
RAW_MARKDOWN_LINK_RE = re.compile(r"\[[A-Z][A-Z0-9.-]{0,14}\]\(https?://[^\)]+\)")
FORBIDDEN_CONTENT_TOKENS = [
    "Placeholder for runtime replacement",
    "runtime rebuild required",
    "Pending classification",
    "None / None:",
    "Replacement Duel Table v2",
]
FORBIDDEN_REPLACEMENT_DUEL_HEADERS = ["Current close", "Challenger close"]

STRICT_TITLE_GROUPS = [
    ["Portfolio Action Snapshot", "Portefeuille-acties"],
    ["Regime Dashboard", "Regime-dashboard"],
    ["Structural Opportunity Radar", "Structurele kansenradar"],
    ["Key Risks / Invalidators", "Belangrijkste risico’s / invalidaties"],
    ["Equity Curve and Portfolio Development", "Portefeuillecurve en portefeuilleontwikkeling"],
    ["Asset Allocation Map", "Allocatiekaart"],
    ["Second-Order Effects Map", "Tweede-orde-effectenkaart"],
    ["Current Position Review", "Review huidige posities"],
    ["Final Action Table", "Definitieve actietabel"],
    ["Current Portfolio Holdings and Cash", "Huidige posities en cash"],
    ["Continuity Input for Next Run", "Input voor de volgende run"],
    ["Replacement Duel Table", "Vervangingsanalyse"],
]

REPLACEMENT_DUEL_REQUIRED_HEADER_GROUPS = [
    ["Current holding", "Huidige positie"],
    ["Challenger", "Alternatief"],
    ["1m edge", "1m relatieve sterkte"],
    ["3m edge", "3m relatieve sterkte"],
    ["Pricing basis", "Prijsbasis"],
    ["Decision", "Beoordeling"],
    ["Required trigger", "Benodigde bevestiging"],
]

STRUCTURAL_RADAR_TITLES = ["Structural Opportunity Radar", "Structurele kansenradar"]
STRUCTURAL_RADAR_END_TITLE_GROUPS = [
    ["Short Opportunity Radar"],
    ["Key Risks / Invalidators", "Belangrijkste risico’s / invalidaties"],
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
    html = report_module.build_report_html(md_text, _report_date_from_filename(report_path), image_src=None, render_mode="email")
    return sanitize_client_facing_html(html)


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


def _find_any(html: str, options: list[str], start: int = 0) -> tuple[int, str | None]:
    candidates = [(html.find(option, start), option) for option in options]
    candidates = [(idx, option) for idx, option in candidates if idx != -1]
    return min(candidates, key=lambda item: item[0]) if candidates else (-1, None)


def _section_between_title_groups(html: str, start_titles: list[str], end_title_groups: list[list[str]]) -> str:
    start, found = _find_any(html, start_titles)
    if start == -1:
        raise RuntimeError(f"Delivery HTML contract validation failed: missing section title from: {start_titles}")
    candidates: list[int] = []
    for group in end_title_groups:
        idx, _ = _find_any(html, group, start + len(found or ""))
        if idx != -1:
            candidates.append(idx)
    end = min(candidates) if candidates else len(html)
    return html[start:end]


def _validate_no_forbidden_content(html: str, report_name: str) -> None:
    lower = html.lower()
    for token in FORBIDDEN_CONTENT_TOKENS:
        if token.lower() in lower:
            raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: forbidden token found: {token!r}")
    match = RAW_MARKDOWN_LINK_RE.search(html)
    if match:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: raw markdown link found: {match.group(0)}")


def _validate_required_titles(html: str, report_name: str) -> None:
    plain = _strip_html(html)
    missing = [" / ".join(group) for group in STRICT_TITLE_GROUPS if not any(title in plain for title in group)]
    if missing:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing rendered section titles: {', '.join(missing)}")


def _validate_structural_radar(html: str, report_name: str) -> None:
    section = _section_between_title_groups(html, STRUCTURAL_RADAR_TITLES, STRUCTURAL_RADAR_END_TITLE_GROUPS)
    plain = _strip_html(section).lower()
    if len(plain) < 240:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar is too thin after rendering.")
    if "placeholder" in plain or "runtime replacement" in plain:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar still contains placeholder text.")


def _replacement_duel_section(html: str) -> str:
    return _section_between_title_groups(
        html,
        ["Replacement Duel Table", "Vervangingsanalyse"],
        [["Portfolio Rotation Plan", "Rotatieplan portefeuille"], ["Final Action Table", "Definitieve actietabel"]],
    )


def _validate_strict_tables_and_anchors(html: str, report_name: str, holdings: list[str]) -> None:
    required_classes = ["action-table", "position-review-table", "rotation-plan-table", "replacement-duel-v2-table"]
    missing_classes = [klass for klass in required_classes if klass not in html]
    if missing_classes:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing strict delivery table classes: {', '.join(missing_classes)}")

    duel = _replacement_duel_section(html)
    plain_duel = _strip_html(duel)
    forbidden_headers = [header for header in FORBIDDEN_REPLACEMENT_DUEL_HEADERS if header in plain_duel]
    if forbidden_headers:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: removed Replacement Duel columns still rendered: {', '.join(forbidden_headers)}")

    missing_headers = [" / ".join(group) for group in REPLACEMENT_DUEL_REQUIRED_HEADER_GROUPS if not any(header in plain_duel for header in group)]
    if missing_headers:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Replacement Duel Table missing headers: {', '.join(missing_headers)}")

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
