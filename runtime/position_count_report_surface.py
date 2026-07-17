from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from runtime.position_count_contract import (
    DEFAULT_MAX_ACTIVE_POSITIONS,
    assess_current_positions,
    client_breach_sentence,
)

DEFAULT_PORTFOLIO_STATE_PATH = Path("output/etf_portfolio_state.json")
_SECTION_MARKERS = {
    "en": ("Current Portfolio Holdings and Cash", "Continuity Input for Next Run"),
    "nl": ("Huidige posities en cash", "Input voor de volgende run"),
}
_SYMBOL_RE = re.compile(r"symbol=([A-Z][A-Z0-9./_-]{0,14})", re.IGNORECASE)
_MARKDOWN_ROW_RE = re.compile(
    r"^\|\s*(?:\[)?([A-Z][A-Z0-9./_-]{0,14})(?:\])?(?:\([^\)]*\))?\s*\|",
    re.MULTILINE,
)
_EN_MARKDOWN_LINE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*]\s*)?)Max number of positions:\s*\d+.*$",
    re.IGNORECASE | re.MULTILINE,
)
_NL_MARKDOWN_LINE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*]\s*)?)Maximaal aantal posities:\s*\d+.*$",
    re.IGNORECASE | re.MULTILINE,
)
_EN_HTML_TEXT_RE = re.compile(
    r"Max number of positions:\s*\d+[^<\r\n]*",
    re.IGNORECASE,
)
_NL_HTML_TEXT_RE = re.compile(
    r"Maximaal aantal posities:\s*\d+[^<\r\n]*",
    re.IGNORECASE,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _section(text: str, language: str) -> str:
    start_marker, end_marker = _SECTION_MARKERS[language]
    start = text.find(start_marker)
    if start < 0:
        return ""
    end = text.find(end_marker, start + len(start_marker))
    return text[start : end if end >= 0 else len(text)]


def report_active_tickers(text: str, language: str) -> tuple[str, ...]:
    section = _section(text, language)
    if not section:
        return ()
    tickers = {match.group(1).upper() for match in _SYMBOL_RE.finditer(section)}
    if not tickers:
        tickers = {match.group(1).upper() for match in _MARKDOWN_ROW_RE.finditer(section)}
    tickers.discard("CASH")
    tickers.discard("TICKER")
    return tuple(sorted(tickers))


def apply_position_count_surface(
    text: str,
    *,
    language: str,
    official_positions: list[dict[str, Any]],
    max_active_positions: int = DEFAULT_MAX_ACTIVE_POSITIONS,
) -> str:
    assessment = assess_current_positions(
        official_positions,
        max_active_positions=max_active_positions,
    )
    if not assessment.passed or assessment.status != "close_first":
        return text

    report_tickers = report_active_tickers(text, language)
    if report_tickers != assessment.current_tickers:
        return text

    sentence = client_breach_sentence(
        current_count=assessment.current_count,
        max_active_positions=max_active_positions,
        language=language,
    )
    if not sentence:
        return text

    markdown_re = _NL_MARKDOWN_LINE_RE if language == "nl" else _EN_MARKDOWN_LINE_RE
    inline_re = _NL_HTML_TEXT_RE if language == "nl" else _EN_HTML_TEXT_RE
    if markdown_re.search(text):
        return markdown_re.sub(
            lambda match: f"{match.group('prefix')}{sentence}",
            text,
            count=1,
        )
    if inline_re.search(text):
        return inline_re.sub(sentence, text, count=1)
    return text


def apply_official_position_count_surface(
    text: str,
    *,
    language: str,
    portfolio_state_path: Path = DEFAULT_PORTFOLIO_STATE_PATH,
    max_active_positions: int = DEFAULT_MAX_ACTIVE_POSITIONS,
) -> str:
    if not portfolio_state_path.exists():
        return text
    payload = _read_json(portfolio_state_path)
    positions = [
        dict(row)
        for row in payload.get("positions", []) or []
        if isinstance(row, dict)
    ]
    return apply_position_count_surface(
        text,
        language=language,
        official_positions=positions,
        max_active_positions=max_active_positions,
    )
