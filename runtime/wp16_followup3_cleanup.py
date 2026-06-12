from __future__ import annotations

import re

NON_US_REPLACEMENTS = {
    "Watchlist only; non-U.S. exposure remains a diversification gap.": "IEFA now provides non-U.S. developed-market exposure, but broader allocation still requires relative-strength confirmation.",
    "Non-U.S. equity exposure remains a diversification gap.": "Non-U.S. developed exposure has been increased through IEFA, but breadth and relative-strength confirmation remain required.",
    "Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof.": "IEFA biedt nu blootstelling aan ontwikkelde markten buiten de VS; verdere allocatie vraagt nog bevestiging in relatieve sterkte.",
    "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.": "Blootstelling aan ontwikkelde markten buiten de VS is via IEFA verhoogd, maar blijft onder bevestiging in relatieve sterkte.",
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


def clean_text(text: str, *, language: str) -> str:
    for source, target in NON_US_REPLACEMENTS.items():
        text = text.replace(source, target)
    if language == "nl":
        for pattern, target in DUTCH_MEMORY_PATTERNS:
            text = pattern.sub(target, text)
    return text


def failures(text: str, *, language: str) -> list[str]:
    lower = text.lower()
    checks = [
        "non-u.s. exposure remains a diversification gap",
        "blootstelling buiten de vs blijft een diversificatiekloof",
        "niet-amerikaanse aandelenblootstelling blijft een diversificatiekloof",
        "wp16-nl-equity-curve-guard",
    ]
    if language == "nl":
        checks.append("risk-on growth has persisted")
    else:
        checks.append("risk-on groei houdt")
    return [item for item in checks if item in lower]
