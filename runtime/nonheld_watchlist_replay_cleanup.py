from __future__ import annotations

import re
from pathlib import Path


REPLACEMENTS = {
    "en": [
        (
            re.compile(r"\bPPA must justify itself\b", re.IGNORECASE),
            "PPA is a non-held watchlist candidate; vehicle selection must be justified",
        ),
    ],
    "nl": [
        (
            re.compile(r"\bPPA moet zich bewijzen\b", re.IGNORECASE),
            "PPA is een niet-aangehouden volglijstkandidaat; de instrumentkeuze moet worden onderbouwd",
        ),
    ],
}

SECTION_HEADINGS = {
    "en": "## 4. Structural Opportunity Radar",
    "nl": "## 4. Structurele kansenradar",
}

EXPLICIT_NOTES = {
    "en": (
        "- **Non-held watchlist status:** PPA and ITA are research candidates only; "
        "neither is a current portfolio position."
    ),
    "nl": (
        "- **Niet-aangehouden volglijststatus:** PPA en ITA zijn uitsluitend "
        "onderzoekskandidaten; geen van beide is een huidige portefeuillepositie."
    ),
}


def _ensure_section_qualifier(text: str, language: str) -> str:
    heading = SECTION_HEADINGS[language]
    start = text.find(heading)
    if start == -1:
        return text
    body_start = start + len(heading)
    next_heading = re.search(r"\n## (?:\d+|\d+[A-Z]?)[\.]?\s", text[body_start:])
    end = len(text) if next_heading is None else body_start + next_heading.start()
    section = text[start:end]
    folded = section.lower()
    if "ppa" not in folded:
        return text
    if "non-held" in folded or "niet-aangehouden" in folded:
        return text
    insertion = "\n\n" + EXPLICIT_NOTES[language]
    return text[:body_start] + insertion + text[body_start:]


def normalize_nonheld_watchlist_text(text: str, language: str) -> str:
    language = language.lower().strip()
    if language not in REPLACEMENTS:
        raise ValueError(f"Unsupported language: {language}")
    for pattern, replacement in REPLACEMENTS[language]:
        text = pattern.sub(replacement, text)
    return _ensure_section_qualifier(text, language)


def normalize_nonheld_watchlist_file(path: Path, language: str) -> bool:
    original = path.read_text(encoding="utf-8")
    normalized = normalize_nonheld_watchlist_text(original, language)
    if normalized == original:
        return False
    path.write_text(normalized, encoding="utf-8")
    print(
        "ETF_NONHELD_WATCHLIST_REPLAY_CLEANUP_OK | "
        f"report={path.name} | language={language}"
    )
    return True
