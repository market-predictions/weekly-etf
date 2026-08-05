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


def normalize_nonheld_watchlist_text(text: str, language: str) -> str:
    language = language.lower().strip()
    if language not in REPLACEMENTS:
        raise ValueError(f"Unsupported language: {language}")
    for pattern, replacement in REPLACEMENTS[language]:
        text = pattern.sub(replacement, text)
    return text


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
