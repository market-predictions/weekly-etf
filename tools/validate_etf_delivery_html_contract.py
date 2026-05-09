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
from runtime.render_etf_report_from_state import position_rows

report_module.build_report_html = build_report_html_with_state(
    report_module.build_report_html,
    report_module._base,
)

RAW_MARKDOWN_LINK_RE = re.compile(r"\[[A-Z][A-Z0-9.-]{0,14}\]\(https?://[^\)]+\)")
PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
FORBIDDEN_CONTENT_TOKENS = [
    "Placeholder for runtime replacement",
    "runtime rebuild required",
    "Pending classification",
    "None / None:",
]

# These are delivery-HTML checks, not markdown-source checks. Keep the markers
# limited to terms that survive the renderer. Structural Opportunity Radar has
# its own rendering-tolerant check below; the markdown content contract already
# validates the exact radar table headers before this delivery validator runs.
CLIENT_CONTENT_SECTIONS = {
    "Regime Dashboard": ["Macro regime", "Primary regime", "Geopolitical regime"],
    "Key Risks / Invalidators": ["SPY", "GLD", "PPA"],
    "Equity Curve and Portfolio Development": ["Current portfolio value", "Portfolio value"],
    "Asset Allocation Map": ["Bucket", "Stance", "Reason"],
    "Second-Order Effects Map": ["Driver", "ETF implication"],
    "Final Action Table": ["Ticker", "Suggested Action", "Total Score"],
    "Current Portfolio Holdings and Cash": ["Total portfolio value", "Market value", "Weight"],
    "Continuity Input for Next Run": ["Portfolio table", "Watchlist", "Recommendation discipline"],
}


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


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _clean(value: Any) -> str:
    return str(value or "").strip().lower()


def _strip_html(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", value)).strip()


def _is_add(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action"))
    executed = _clean(p.get("action_executed_this_run"))
    shares_delta = float(p.get("shares_delta_this_run") or 0.0)
    return "add" in action or "buy" in executed or shares_delta > 0


def _is_hold(p: dict[str, Any]) -> bool:
    return "hold" in _clean(p.get("suggested_action")) and not _is_add(p)


def _is_replace(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action"))
    better = _clean(p.get("better_alternative_exists"))
    return better == "yes" or "review" in action or "replace" in action


def _is_reduce(p: dict[str, Any]) -> bool:
    return "reduce" in _clean(p.get("suggested_action"))


def _is_close(p: dict[str, Any]) -> bool:
    action = _clean(p.get("suggested_action"))
    return "close" in action or "sell" in action


def _state() -> dict[str, Any]:
    return build_runtime_state()


def _current_holdings_from_state(state: dict[str, Any]) -> list[str]:
    tickers: list[str] = []
    for position in state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if ticker and ticker != "CASH" and ticker not in tickers:
            tickers.append(ticker)
    if not tickers:
        raise RuntimeError("Delivery HTML contract validation failed: no current holdings found in runtime state.")
    return tickers


def _classified_state_tickers(state: dict[str, Any]) -> dict[str, list[str]]:
    positions = position_rows(state)
    return {
        "add": [_ticker(p.get("ticker")) for p in positions if _is_add(p)],
        "hold": [_ticker(p.get("ticker")) for p in positions if _is_hold(p) or _is_add(p)],
        "replace": [_ticker(p.get("ticker")) for p in positions if _is_replace(p)],
        "reduce": [_ticker(p.get("ticker")) for p in positions if _is_reduce(p)],
        "close": [_ticker(p.get("ticker")) for p in positions if _is_close(p)],
    }


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


def _validate_no_placeholder_content(html: str, report_name: str) -> None:
    lower = html.lower()
    for token in FORBIDDEN_CONTENT_TOKENS:
        if token.lower() in lower:
            raise RuntimeError(
                f"Delivery HTML contract validation failed for {report_name}: forbidden placeholder token found: {token!r}"
            )


def _validate_client_content_sections(html: str, report_name: str) -> None:
    for title, required_terms in CLIENT_CONTENT_SECTIONS.items():
        panel = _section_panel(html, title)
        plain = _strip_html(panel).lower()
        if len(plain) < 120:
            raise RuntimeError(
                f"Delivery HTML contract validation failed for {report_name}: {title} is too thin after rendering."
            )
        missing = [term for term in required_terms if term.lower() not in plain]
        if missing:
            raise RuntimeError(
                f"Delivery HTML contract validation failed for {report_name}: {title} missing client-facing content markers: {', '.join(missing)}"
            )


def _validate_structural_opportunity_radar(html: str, report_name: str) -> None:
    """Validate the radar survived HTML rendering without overfitting to tags.

    The markdown content contract already checks the exact radar table headers.
    At the delivery layer we only need to make sure the rendered HTML still has
    a substantive, non-placeholder radar panel. The renderer may convert table
    headers, links and typography in ways that make exact runtime lane-name
    matching brittle, so this check uses durable client-facing terms.
    """
    panel = _section_panel(html, "Structural Opportunity Radar")
    plain = _strip_html(panel)
    plain_lower = plain.lower()
    if len(plain) < 240:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar is too thin after rendering."
        )

    required_any_groups = [
        ["actionable now", "watchlist", "under review"],
        ["structural", "macro", "time horizon", "why it matters", "what needs to happen"],
        ["best structural opportunities", "not yet actionable", "notable lanes"],
    ]
    missing_groups = []
    for group in required_any_groups:
        if not any(term in plain_lower for term in group):
            missing_groups.append(" / ".join(group))
    if missing_groups:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Structural Opportunity Radar missing rendered content markers: {', '.join(missing_groups)}"
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


def _validate_rotation_plan(html: str, report_name: str, classified: dict[str, list[str]]) -> None:
    panel = _section_panel(html, "Portfolio Rotation Plan")
    required_bits = [
        "rotation-plan-table",
        ">Close<",
        ">Reduce<",
        ">Hold<",
        ">Add<",
        ">Replace<",
    ]
    missing_bits = [bit for bit in required_bits if bit not in panel]
    if missing_bits:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Portfolio Rotation Plan missing required HTML bits: {', '.join(missing_bits)}"
        )

    if all(not values for values in classified.values()):
        return
    if re.search(r"<td>\s*None\s*</td>\s*<td>\s*None\s*</td>\s*<td>\s*None\s*</td>\s*<td>\s*None\s*</td>\s*<td>\s*None\s*</td>", panel, flags=re.IGNORECASE):
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Portfolio Rotation Plan shows all None despite state actions."
        )

    for bucket, tickers in classified.items():
        for ticker in tickers:
            if ticker and not _anchor_for_ticker_exists(panel, ticker):
                raise RuntimeError(
                    f"Delivery HTML contract validation failed for {report_name}: Portfolio Rotation Plan missing {bucket} anchor for {ticker}."
                )


def _validate_replacement_duel_v2(html: str, report_name: str) -> None:
    panel = _section_panel(html, "Replacement Duel Table v2")
    required_bits = [
        "replacement-duel-v2-table",
        ">Current holding<",
        ">Challenger<",
        ">1m edge<",
        ">3m edge<",
        ">Pricing status<",
        ">Decision<",
    ]
    missing_bits = [bit for bit in required_bits if bit not in panel]
    if missing_bits:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Replacement Duel Table v2 missing required HTML bits: {', '.join(missing_bits)}"
        )

    row_matches = re.findall(r"<tr>(.*?)</tr>", panel, flags=re.IGNORECASE | re.DOTALL)
    data_rows = [row for row in row_matches if "<td" in row.lower()]
    if not data_rows:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Replacement Duel Table v2 has no data rows."
        )

    filled_decisions = 0
    for row in data_rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.IGNORECASE | re.DOTALL)
        if len(cells) < 6:
            continue
        decision_text = _strip_html(cells[5])
        if decision_text and decision_text.lower() not in {"none", "n/a", "-"}:
            filled_decisions += 1
    if filled_decisions == 0:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Replacement Duel Table v2 has no filled decision cells."
        )


def validate(output_dir: Path) -> None:
    state = _state()
    holdings = _current_holdings_from_state(state)
    classified = _classified_state_tickers(state)
    reports = _latest_reports(output_dir)
    for report_path in reports:
        html = _render_delivery_html(report_path)
        _validate_no_placeholder_content(html, report_path.name)
        _validate_no_raw_markdown_links(html, report_path.name)
        _validate_client_content_sections(html, report_path.name)
        _validate_structural_opportunity_radar(html, report_path.name)
        _validate_action_snapshot(html, report_path.name, holdings)
        _validate_position_review(html, report_path.name, holdings)
        _validate_rotation_plan(html, report_path.name, classified)
        _validate_replacement_duel_v2(html, report_path.name)
        print(f"ETF_DELIVERY_HTML_CONTRACT_OK | report={report_path.name} | dynamic_holdings={','.join(holdings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
