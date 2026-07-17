from __future__ import annotations

import re

from runtime.position_count_contract import client_breach_sentence
from runtime.report_surface_language_contract import (
    client_language_findings,
    normalize_client_language,
)

NON_US_REPLACEMENTS = {
    "Watchlist only; non-U.S. exposure remains a diversification gap.": "IEFA now provides non-U.S. developed-market exposure, but broader allocation still requires relative-strength confirmation.",
    "Non-U.S. equity exposure remains a diversification gap.": "Non-U.S. developed exposure has been increased through IEFA, but breadth and relative-strength confirmation remain required.",
    "Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof.": "IEFA biedt nu blootstelling aan ontwikkelde markten buiten de VS; verdere allocatie vraagt nog bevestiging in relatieve sterkte.",
    "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.": "Blootstelling aan ontwikkelde markten buiten de VS is via IEFA verhoogd, maar blijft onder bevestiging in relatieve sterkte.",
}

PRODUCT_NAME_REPAIRS = {
    "iAantal aandelen": "iShares",
    "iAantal aandelen S&P GSCI Commodity-Indexed Trust": "iShares S&P GSCI Commodity-Indexed Trust",
    "SPDR Gold Aantal aandelen": "SPDR Gold Shares",
}

DUTCH_MEMORY_PATTERNS = [
    (
        re.compile(r"Risk-on growth has persisted for (\d+) run\(s\); transition state is stable, breadth is improving, and cross-asset confirmation is mixed\.", re.IGNORECASE),
        r"Risk-on groei houdt al \1 runs aan; de overgangsfase is stabiel, de marktbreedte verbetert en cross-asset bevestiging blijft gemengd.",
    ),
    (
        re.compile(r"Risk-on growth has persisted for (\d+) run\(s\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\.", re.IGNORECASE),
        r"Risk-on groei houdt al \1 runs aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-asset bevestiging blijft gemengd.",
    ),
]

_SECTION_MARKERS = {
    "en": ("## 15. Current Portfolio Holdings and Cash", "## 16. Continuity Input for Next Run"),
    "nl": ("## 15. Huidige posities en cash", "## 16. Input voor de volgende run"),
}
_SYMBOL_RE = re.compile(r"symbol=([A-Z][A-Z0-9./_-]{0,14})", re.IGNORECASE)
_EN_LIMIT_RE = re.compile(r"Max number of positions:\s*(\d+)", re.IGNORECASE)
_NL_LIMIT_RE = re.compile(r"Maximaal aantal posities:\s*(\d+)", re.IGNORECASE)
_EN_CONSTRAINT_LINE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*]\s*)?)Max number of positions:\s*\d+.*$",
    re.IGNORECASE | re.MULTILINE,
)
_NL_CONSTRAINT_LINE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*]\s*)?)Maximaal aantal posities:\s*\d+.*$",
    re.IGNORECASE | re.MULTILINE,
)


def _repair_product_names(text: str) -> str:
    for source, target in PRODUCT_NAME_REPAIRS.items():
        text = text.replace(source, target)
    return text


def _section(text: str, language: str) -> str:
    start_marker, end_marker = _SECTION_MARKERS[language]
    start = text.find(start_marker)
    if start < 0:
        return ""
    end = text.find(end_marker, start + len(start_marker))
    return text[start : end if end >= 0 else len(text)]


def _active_report_tickers(text: str, language: str) -> tuple[str, ...]:
    section = _section(text, language)
    if not section:
        return ()
    tickers = {match.group(1).upper() for match in _SYMBOL_RE.finditer(section)}
    tickers.discard("CASH")
    return tuple(sorted(tickers))


def _apply_position_count_surface(text: str, language: str) -> str:
    tickers = _active_report_tickers(text, language)
    if not tickers:
        return text
    limit_re = _NL_LIMIT_RE if language == "nl" else _EN_LIMIT_RE
    match = limit_re.search(text)
    if not match:
        return text
    maximum = int(match.group(1))
    current = len(tickers)
    sentence = client_breach_sentence(
        current_count=current,
        max_active_positions=maximum,
        language=language,
    )
    if not sentence:
        return text
    line_re = _NL_CONSTRAINT_LINE_RE if language == "nl" else _EN_CONSTRAINT_LINE_RE
    return line_re.sub(lambda found: f"{found.group('prefix')}{sentence}", text, count=1)


def clean_text(text: str, *, language: str) -> str:
    for source, target in NON_US_REPLACEMENTS.items():
        text = text.replace(source, target)
    if language == "nl":
        for pattern, target in DUTCH_MEMORY_PATTERNS:
            text = pattern.sub(target, text)
        text = _repair_product_names(text)
    text = _apply_position_count_surface(text, language)
    return normalize_client_language(text, language=language)


def failures(text: str, *, language: str) -> list[str]:
    lower = text.lower()
    checks = [
        "non-u.s. exposure remains a diversification gap",
        "blootstelling buiten de vs blijft een diversificatiekloof",
        "niet-amerikaanse aandelenblootstelling blijft een diversificatiekloof",
        "wp16-nl-equity-curve-guard",
        "iaantal aandelen",
    ]
    if language == "nl":
        checks.append("risk-on growth has persisted")
    else:
        checks.append("risk-on groei houdt")
    return sorted(set([item for item in checks if item in lower] + client_language_findings(text, language=language)))
