from __future__ import annotations

import argparse
import json
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
STYLE_BLOCK_RE = re.compile(r"<(style|script)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
HIDDEN_EXEC_MARKER_RE = re.compile(r"<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\b(?:exec-summary-suppressed|exec-summary-render-marker)\b)[^>]*>.*?</div>", re.DOTALL | re.IGNORECASE)
VISIBLE_PANEL_EXEC_RE = re.compile(r"<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bpanel-exec\b)[^>]*>", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
RUNTIME_POINTER = Path("output/runtime/latest_etf_report_state_path.txt")

FORBIDDEN_CONTENT_TOKENS = [
    "Placeholder for runtime replacement",
    "runtime rebuild required",
    "Pending classification",
    "None / None:",
    "Replacement Duel Table v2",
]
FORBIDDEN_POST_EXECUTION_PHRASES = [
    "Rotation plan artifact is active",
    "proposed until",
    "pending execution",
    "pending portfolio-state persistence",
    "pending execution and portfolio-state persistence",
    "Proposed rotation",
    "proposed rotation",
    "trade intents are proposed",
    "not executed trades until",
    "until the trade ledger and portfolio state record execution",
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
EXECUTIVE_DUPLICATE_PHRASES = [
    "SMH remains the earned leader, but fresh capital and replacement decisions must pass regime, pricing and duel-evidence checks.",
    "SMH blijft de best onderbouwde kernpositie, maar nieuw kapitaal en vervangingsbeslissingen moeten koersbevestiging, relatieve sterkte en steun vanuit het macrobeeld doorstaan.",
    "Houd de huidige allocatie gedisciplineerd.",
]


def _canonical_report_key(path: Path) -> tuple[str, int] | None:
    match = PRO_REPORT_RE.match(path.name)
    return (match.group(1), int(match.group(2) or "1")) if match else None


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
    candidates = []
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


def _load_pointer_state() -> dict[str, Any] | None:
    candidates: list[Path] = []
    if RUNTIME_POINTER.exists():
        raw = RUNTIME_POINTER.read_text(encoding="utf-8").strip()
        if raw:
            candidates += [Path(raw), RUNTIME_POINTER.parent / Path(raw).name]
    for raw in (os.environ.get("MRKT_RPRTS_RUNTIME_STATE_PATH"), os.environ.get("ETF_RUNTIME_STATE_PATH")):
        if raw:
            candidates.append(Path(raw))
    for path in candidates:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _state() -> dict[str, Any]:
    return _load_pointer_state() or build_runtime_state()


def _is_post_execution_state(state: dict[str, Any]) -> bool:
    context = state.get("execution_context") or {}
    flags = state.get("validation_flags") or {}
    return context.get("report_phase") == "post_execution" or bool(flags.get("already_executed_noop")) or bool(flags.get("post_execution_report"))


def _render_delivery_html(report_path: Path) -> str:
    md_text = report_path.read_text(encoding="utf-8")
    html = report_module.build_report_html(md_text, _report_date_from_filename(report_path), image_src=None, render_mode="email")
    return sanitize_client_facing_html(html, md_text=md_text, language="nl" if looks_dutch_markdown(md_text) else "en")


def _visible_html(html: str) -> str:
    html = STYLE_BLOCK_RE.sub("", html)
    html = HIDDEN_EXEC_MARKER_RE.sub("", html)
    return html


def _visible_text(html: str) -> str:
    html = _visible_html(html)
    text = unescape(TAG_RE.sub(" ", html))
    return re.sub(r"\s+", " ", text).strip()


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


def _validate_no_forbidden_content(html: str, report_name: str) -> None:
    lower = html.lower()
    for token in FORBIDDEN_CONTENT_TOKENS:
        if token.lower() in lower:
            raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: forbidden token found: {token!r}")
    match = RAW_MARKDOWN_LINK_RE.search(html)
    if match:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: raw markdown link found: {match.group(0)}")


def _validate_post_execution_copy(html: str, report_name: str, state: dict[str, Any]) -> None:
    if not _is_post_execution_state(state):
        return
    text = _visible_text(html)
    found = [phrase for phrase in FORBIDDEN_POST_EXECUTION_PHRASES if phrase in text]
    if found:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: post-execution HTML still contains proposed/pending wording: {', '.join(sorted(set(found)))}"
        )


def _validate_no_duplicate_executive_summary(html: str, report_name: str) -> None:
    visible_html = _visible_html(html)
    text = _visible_text(html)
    if VISIBLE_PANEL_EXEC_RE.search(visible_html):
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: duplicate executive summary panel still rendered.")
    for phrase in EXECUTIVE_DUPLICATE_PHRASES:
        if text.count(phrase) > 1:
            raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: duplicated executive takeaway phrase: {phrase[:80]}")


def _validate_required_titles(html: str, report_name: str) -> None:
    text = _visible_text(html)
    missing = [" / ".join(group) for group in STRICT_TITLE_GROUPS if not any(title in text for title in group)]
    if missing:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing rendered section titles: {', '.join(missing)}")


def _validate_structural_radar(html: str, report_name: str) -> None:
    text = _visible_text(html).lower()
    if "structural opportunity radar" not in text and "structurele kansenradar" not in text:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing Structural Opportunity Radar section.")
    if "placeholder" in text or "runtime replacement" in text:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar still contains placeholder text.")


def _validate_strict_tables_and_anchors(html: str, report_name: str, holdings: list[str]) -> None:
    required_classes = ["action-table", "position-review-table", "rotation-plan-table", "replacement-duel-v2-table"]
    missing_classes = [klass for klass in required_classes if klass not in html]
    if missing_classes:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing strict delivery table classes: {', '.join(missing_classes)}")
    text = _visible_text(html)
    forbidden_headers = [header for header in FORBIDDEN_REPLACEMENT_DUEL_HEADERS if header in text]
    if forbidden_headers:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: removed Replacement Duel columns still rendered: {', '.join(forbidden_headers)}")
    missing_headers = [" / ".join(group) for group in REPLACEMENT_DUEL_REQUIRED_HEADER_GROUPS if not any(header in text for header in group)]
    if missing_headers:
        raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: Replacement Duel Table missing headers: {', '.join(missing_headers)}")
    for ticker in holdings:
        if not _anchor_for_ticker_exists(html, ticker):
            raise RuntimeError(f"Delivery HTML contract validation failed for {report_name}: missing TradingView anchor for current holding {ticker}.")


def validate(output_dir: Path) -> None:
    state = _state()
    holdings = _current_holdings_from_state(state)
    reports = _latest_reports(output_dir)
    for report_path in reports:
        md_text = report_path.read_text(encoding="utf-8")
        html = _render_delivery_html(report_path)
        _validate_no_forbidden_content(html, report_path.name)
        _validate_post_execution_copy(html, report_path.name, state)
        _validate_no_duplicate_executive_summary(html, report_path.name)
        _validate_required_titles(html, report_path.name)
        _validate_structural_radar(html, report_path.name)
        _validate_strict_tables_and_anchors(html, report_path.name, holdings)
        if looks_dutch_markdown(md_text):
            validate_dutch_delivery_language(html, report_path.name)
        post_flag = "post_execution=True" if _is_post_execution_state(state) else "post_execution=False"
        print(f"ETF_DELIVERY_HTML_CONTRACT_OK | report={report_path.name} | dynamic_holdings={','.join(holdings)} | {post_flag}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
