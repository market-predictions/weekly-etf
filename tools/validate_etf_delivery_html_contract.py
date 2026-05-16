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

import send_report_runtime_html as runtime_delivery
from runtime.build_etf_report_state import build_runtime_state
from runtime.client_facing_sanitizer import looks_dutch_markdown, sanitize_client_facing_html, validate_dutch_delivery_language

report_module = runtime_delivery.report_module

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
RAW_MARKDOWN_LINK_RE = re.compile(r"\[[A-Z][A-Z0-9.-]{0,14}\]\(https?://[^\)]+\)")
STYLE_OR_SCRIPT_RE = re.compile(r"<(style|script)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
HIDDEN_EXEC_MARKER_RE = re.compile(r"<div class=['\"](?:exec-summary-suppressed|exec-summary-render-marker)['\"][^>]*>.*?</div>", re.DOTALL | re.IGNORECASE)
VISIBLE_PANEL_EXEC_RE = re.compile(r"<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bpanel-exec\b)[^>]*>", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
HTML_START_TAG_RE = re.compile(r"<([a-zA-Z0-9]+)\b[^>]*>")
SECTION_LABEL_RE = re.compile(r"<span\b[^>]*class=['\"][^'\"]*section-label[^'\"]*['\"][^>]*>(.*?)</span>", re.DOTALL | re.IGNORECASE)
MINI_LABEL_RE = re.compile(r"<div\b[^>]*class=['\"][^'\"]*mini-label[^'\"]*['\"][^>]*>(.*?)</div>", re.DOTALL | re.IGNORECASE)
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
EXECUTIVE_DUPLICATE_PHRASES = [
    "SMH remains the earned leader, but fresh capital and replacement decisions must pass regime, pricing and duel-evidence checks.",
    "SMH blijft de best onderbouwde kernpositie, maar nieuw kapitaal en vervangingsbeslissingen moeten koersbevestiging, relatieve sterkte en steun vanuit het macrobeeld doorstaan.",
    "Houd de huidige allocatie gedisciplineerd.",
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
    return sanitize_client_facing_html(html, md_text=md_text, language="nl" if looks_dutch_markdown(md_text) else "en")


def _visible_html(html: str) -> str:
    """Return HTML that represents visible body content, not CSS/script/hidden markers."""
    html = STYLE_OR_SCRIPT_RE.sub("", html)
    html = HIDDEN_EXEC_MARKER_RE.sub("", html)
    return html


def _strip_html(value: str) -> str:
    value = _visible_html(value)
    return unescape(re.sub(r"<[^>]+>", " ", value)).strip()


def _plain_text_with_offsets(html: str) -> tuple[str, list[int]]:
    """Convert HTML to plain text while mapping each text character back to HTML offset."""
    chunks: list[str] = []
    offsets: list[int] = []
    cursor = 0
    for tag in HTML_TAG_RE.finditer(html):
        if tag.start() > cursor:
            segment = unescape(html[cursor:tag.start()])
            chunks.append(segment)
            offsets.extend(range(cursor, cursor + len(segment)))
        cursor = tag.end()
    if cursor < len(html):
        segment = unescape(html[cursor:])
        chunks.append(segment)
        offsets.extend(range(cursor, cursor + len(segment)))
    return "".join(chunks), offsets


def _compact(value: str, limit: int = 360) -> str:
    value = re.sub(r"\s+", " ", unescape(value)).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _html_snippet(html: str, offset: int, radius: int = 260) -> str:
    start = max(0, offset - radius)
    end = min(len(html), offset + radius)
    return _compact(html[start:end], limit=520)


def _nearest_start_tag(html: str, offset: int) -> str:
    matches = list(HTML_START_TAG_RE.finditer(html[:offset]))
    return _compact(matches[-1].group(0), limit=260) if matches else "unknown"


def _nearest_label(html: str, offset: int) -> str:
    labels: list[tuple[int, str, str]] = []
    for match in SECTION_LABEL_RE.finditer(html[:offset]):
        labels.append((match.start(), "section-label", _strip_html(match.group(1))))
    for match in MINI_LABEL_RE.finditer(html[:offset]):
        labels.append((match.start(), "mini-label", _strip_html(match.group(1))))
    if not labels:
        return "unknown"
    _, kind, value = sorted(labels, key=lambda row: row[0])[-1]
    return f"{kind}: {_compact(value, 140)}"


def _nearest_title_from_known_titles(plain: str, plain_offset: int) -> str:
    candidates: list[tuple[int, str]] = []
    known_titles = [title for group in STRICT_TITLE_GROUPS + REPLACEMENT_DUEL_REQUIRED_HEADER_GROUPS for title in group]
    known_titles += STRUCTURAL_RADAR_TITLES + ["Primary regime", "Primair regime", "Geopolitical regime", "Geopolitiek regime", "Main takeaway", "Kernconclusie"]
    for title in known_titles:
        idx = plain.rfind(title, 0, plain_offset)
        if idx != -1:
            candidates.append((idx, title))
    if not candidates:
        return "unknown"
    return sorted(candidates, key=lambda row: row[0])[-1][1]


def _phrase_context_report(html: str, phrase: str) -> str:
    visible = _visible_html(html)
    plain, offsets = _plain_text_with_offsets(visible)
    occurrences: list[int] = []
    start = 0
    while True:
        idx = plain.find(phrase, start)
        if idx == -1:
            break
        occurrences.append(idx)
        start = idx + max(1, len(phrase))

    lines = [
        "DUPLICATE_TAKEAWAY_CONTEXT_BEGIN",
        f"phrase={phrase}",
        f"plain_occurrences={len(occurrences)}",
    ]
    for number, plain_idx in enumerate(occurrences, start=1):
        html_idx = offsets[plain_idx] if plain_idx < len(offsets) else -1
        plain_before = plain[max(0, plain_idx - 220):plain_idx]
        plain_after = plain[plain_idx + len(phrase):plain_idx + len(phrase) + 220]
        lines.extend([
            f"occurrence={number}",
            f"plain_offset={plain_idx}",
            f"html_offset={html_idx}",
            f"nearest_label={_nearest_label(visible, html_idx) if html_idx >= 0 else 'unknown'}",
            f"nearest_title={_nearest_title_from_known_titles(plain, plain_idx)}",
            f"nearest_start_tag={_nearest_start_tag(visible, html_idx) if html_idx >= 0 else 'unknown'}",
            f"plain_context={_compact(plain_before + ' >>> ' + phrase + ' <<< ' + plain_after, 520)}",
            f"html_context={_html_snippet(visible, html_idx) if html_idx >= 0 else 'unknown'}",
        ])
    lines.append("DUPLICATE_TAKEAWAY_CONTEXT_END")
    return "\n".join(lines)


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


def _validate_no_duplicate_executive_summary(html: str, report_name: str) -> None:
    visible_html = _visible_html(html)
    if VISIBLE_PANEL_EXEC_RE.search(visible_html):
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: duplicate executive summary panel still rendered.")
    plain = _strip_html(visible_html)
    for phrase in EXECUTIVE_DUPLICATE_PHRASES:
        if plain.count(phrase) > 1:
            diagnostics = _phrase_context_report(html, phrase)
            raise RuntimeError(
                f"Delivery HTML contract validation failed for {report_name}: duplicated executive takeaway phrase: {phrase[:80]}\n{diagnostics}"
            )


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
        md_text = report_path.read_text(encoding="utf-8")
        html = _render_delivery_html(report_path)
        _validate_no_forbidden_content(html, report_path.name)
        _validate_no_duplicate_executive_summary(html, report_path.name)
        _validate_required_titles(html, report_path.name)
        _validate_structural_radar(html, report_path.name)
        _validate_strict_tables_and_anchors(html, report_path.name, holdings)
        if looks_dutch_markdown(md_text):
            validate_dutch_delivery_language(html, report_path.name)
        print(f"ETF_DELIVERY_HTML_CONTRACT_OK | report={report_path.name} | dynamic_holdings={','.join(holdings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
