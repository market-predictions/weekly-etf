from __future__ import annotations

import re

NON_US_EXPOSURE_REPLACEMENTS = {
    "Watchlist only; non-U.S. exposure remains a diversification gap.": "IEFA now provides non-U.S. developed-market exposure, but broader allocation still requires relative-strength confirmation.",
    "Zero allocation is an explicit U.S. exceptionalism bet.": "IEFA now provides non-U.S. developed-market exposure, but broader allocation still requires relative-strength confirmation.",
    "Non-U.S. equity exposure remains a diversification gap.": "Non-U.S. developed exposure has been increased through IEFA, but breadth and relative-strength confirmation remain required.",
    "Portfolio has limited non-U.S. exposure.": "IEFA now provides non-U.S. developed-market exposure, with broader allocation still under confirmation.",
    "Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof.": "IEFA biedt nu blootstelling aan ontwikkelde markten buiten de VS; verdere allocatie vraagt nog bevestiging in relatieve sterkte.",
    "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht.": "IEFA biedt nu blootstelling aan ontwikkelde markten buiten de VS; verdere allocatie vraagt nog bevestiging in relatieve sterkte.",
    "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.": "Blootstelling aan ontwikkelde markten buiten de VS is via IEFA verhoogd, maar blijft onder bevestiging in relatieve sterkte.",
    "De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS.": "De portefeuille heeft via IEFA blootstelling aan ontwikkelde markten buiten de VS, maar verdere allocatie vraagt bevestiging in relatieve sterkte.",
}

DUTCH_REGIME_MEMORY_PATTERNS = [
    (
        re.compile(
            r"Risk-on growth has persisted for (\d+) run\(s\); transition state is stable, breadth is improving, and cross-asset confirmation is mixed\.",
            re.IGNORECASE,
        ),
        r"Risk-on groei houdt al \1 runs aan; de overgangsfase is stabiel, de marktbreedte verbetert en cross-asset bevestiging blijft gemengd.",
    ),
    (
        re.compile(
            r"Risk-on growth has persisted for (\d+) run\(s\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\.",
            re.IGNORECASE,
        ),
        r"Risk-on groei houdt al \1 runs aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-asset bevestiging blijft gemengd.",
    ),
]

FORBIDDEN_RESIDUAL_PATTERNS = [
    "Watchlist only; non-U.S. exposure remains a diversification gap",
    "Zero allocation is an explicit U.S. exceptionalism bet",
    "Non-U.S. equity exposure remains a diversification gap",
    "Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof",
    "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht",
    "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof",
    "Risk-on growth has persisted",
]


def clean_residual_text(text: str) -> str:
    for source, target in NON_US_EXPOSURE_REPLACEMENTS.items():
        text = text.replace(source, target)
    for pattern, target in DUTCH_REGIME_MEMORY_PATTERNS:
        text = pattern.sub(target, text)
    return text


def residual_failures(text: str) -> list[str]:
    lower = text.lower()
    return [pattern for pattern in FORBIDDEN_RESIDUAL_PATTERNS if pattern.lower() in lower]
