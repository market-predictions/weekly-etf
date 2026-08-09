from __future__ import annotations

import re

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

DECISION_STATUS_REPLACEMENTS = {
    "Rotation execution status": "Portfolio decision status",
    "rotation execution status": "portfolio decision status",
    "Status rotatie-uitvoering": "Status portefeuillebesluit",
    "status rotatie-uitvoering": "status portefeuillebesluit",
    "portfolio rotation is already reflected in the official portfolio state and trade ledger; this run performed no duplicate state or ledger mutation.":
        "The official portfolio state and trade ledger are authoritative for this report; this run performed no duplicate state or ledger mutation.",
    "Portfolio rotation is already reflected in the official portfolio state and trade ledger; this run performed no duplicate state or ledger mutation.":
        "The official portfolio state and trade ledger are authoritative for this report; this run performed no duplicate state or ledger mutation.",
    "De bewaakte modelrotatie is al verwerkt in de officiële portefeuillestaat en het handelslogboek; deze run heeft geen dubbele staat- of handelslogboekmutatie uitgevoerd.":
        "De officiële portefeuillestaat en het handelslogboek zijn leidend voor dit rapport; deze run heeft geen dubbele staat- of handelslogboekmutatie uitgevoerd.",
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
    (
        re.compile(r"Risk-on growth has persisted across (\d+) weekly observation\(s\); transition state is a possible transition, breadth is mixed, and cross-asset confirmation is mixed\.", re.IGNORECASE),
        r"Risk-on groei houdt al \1 wekelijkse observaties aan; er is een mogelijke overgang, de marktbreedte is gemengd en cross-asset bevestiging blijft gemengd.",
    ),
    (
        re.compile(r"Risk-on growth has persisted across (\d+) weekly observation\(s\); transition state is newly confirmed, breadth is mixed, and cross-asset confirmation is mixed\.", re.IGNORECASE),
        r"Risk-on groei houdt al \1 wekelijkse observaties aan; het regime is nieuw bevestigd, de marktbreedte is gemengd en cross-asset bevestiging blijft gemengd.",
    ),
]

ROTATION_LIMIT_RE = re.compile(
    r"\b(?:system\s+)?override:\s*rotation budget(?:\s+for this run is)?\s+already used\b",
    re.IGNORECASE,
)


def _repair_product_names(text: str) -> str:
    for source, target in PRODUCT_NAME_REPAIRS.items():
        text = text.replace(source, target)
    return text


def _repair_rotation_limit_language(text: str, *, language: str) -> str:
    replacement = (
        "Uitvoeringsbeperking: rotatielimiet bereikt voor deze review"
        if language == "nl"
        else "Execution constraint: weekly rotation limit reached"
    )
    text = ROTATION_LIMIT_RE.sub(replacement, text)
    if language == "nl":
        text = text.replace("weekly rotation limit reached", "rotatielimiet bereikt voor deze review")
    else:
        text = text.replace("rotatielimiet bereikt voor deze review", "weekly rotation limit reached")
    return text


def _repair_decision_status_language(text: str) -> str:
    for source, target in sorted(
        DECISION_STATUS_REPLACEMENTS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        text = text.replace(source, target)
    return text


def clean_text(text: str, *, language: str) -> str:
    for source, target in NON_US_REPLACEMENTS.items():
        text = text.replace(source, target)
    text = _repair_rotation_limit_language(text, language=language)
    text = _repair_decision_status_language(text)
    if language == "nl":
        for pattern, target in DUTCH_MEMORY_PATTERNS:
            text = pattern.sub(target, text)
        text = _repair_product_names(text)
    text = normalize_client_language(text, language=language)
    return _repair_decision_status_language(text)


def failures(text: str, *, language: str) -> list[str]:
    lower = text.lower()
    checks = [
        "non-u.s. exposure remains a diversification gap",
        "blootstelling buiten de vs blijft een diversificatiekloof",
        "niet-amerikaanse aandelenblootstelling blijft een diversificatiekloof",
        "wp16-nl-equity-curve-guard",
        "iaantal aandelen",
        "rotation execution status",
        "status rotatie-uitvoering",
        "portfolio rotation is already reflected in the official portfolio state and trade ledger",
        "de bewaakte modelrotatie is al verwerkt in de officiële portefeuillestaat en het handelslogboek",
    ]
    if language == "nl":
        checks.append("risk-on growth has persisted")
    else:
        checks.append("risk-on groei houdt")
        checks.append("rotatielimiet bereikt voor deze review")
    return sorted(
        set(
            [item for item in checks if item in lower]
            + client_language_findings(text, language=language)
        )
    )
