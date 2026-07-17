from __future__ import annotations

import re
from collections import Counter
from typing import Any


EXACT_REPLACEMENTS: dict[str, str] = {
    "Macro policy inputs are now surfaced through the runtime macro pack; portfolio actions still require pricing, relative-strength and position-discipline gates.":
        "Current macro and policy evidence remains supportive, while portfolio actions still require pricing, relative-strength and position-discipline confirmation.",
    "Rotation engine status": "Implemented portfolio change",
    "Guarded model rotation executed and persisted:": "Portfolio rotation completed:",
    "guarded model rotation executed and persisted:": "portfolio rotation completed:",
    "The one-major-rotation budget is consumed for this run; another mutation requires a future validated run.":
        "One major allocation change was completed this week; any further change requires fresh market confirmation and a new portfolio review.",
    "Diagnostic-only: these notes grant no allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority or portfolio mutation authority.":
        "Supplementary comparison: this score provides context only and is not an allocation recommendation.",
    "The position review separates thesis quality, ETF implementation quality, fresh-cash test and rotation-engine decision. Existing holdings are not treated as automatic default holds. Where a position-discipline score is not yet available after a rotation, the report shows the live lane score if available; otherwise it flags that the current score is pending.":
        "The position review assesses thesis quality, ETF fit, new-capital attractiveness and the next decision trigger. Existing holdings must continue to justify their place against current evidence and alternatives.",
    "Guarded auto-execution:": "Implemented change:",
    "Hold-with-override note:": "Execution note:",
    "Hold with override": "Hold — no further change this review",
    "model/action weights": "target allocation weights",
    "override handling": "execution constraints",
    "Force alternative duel; upgrade, reduce, replace, or close.":
        "Reassess against the named alternative and retain only if the current ETF remains superior.",
    "Required next action: None.": "Next review: Maintain and reassess when new evidence arrives.",
    "Fresh cash: None": "New capital: No additional allocation",
    "Rotation destination": "Portfolio allocation",
    "Runtime valuation from immutable pricing audit and explicit portfolio state":
        "Portfolio valuation based on confirmed prices and official holdings",
    "Runtime valuation repriced from official portfolio-state shares":
        "Portfolio valuation based on confirmed prices and official holdings",
    "Runtime-derived valuation from pricing audit and explicit portfolio state":
        "Portfolio valuation based on confirmed prices and official holdings",
    "Holdings with high release scores remain subject to reduce/replace/override discipline.":
        "Holdings with the weakest capital-efficiency profile remain candidates for reduction or replacement.",
    "the guarded mutation is executed and persisted": "the allocation change has been completed",
    "available churn budget": "room within the weekly turnover limit",
    "evidence- and churn-gated": "subject to fresh pricing, relative-strength and concentration confirmation",
    "future run clears all discipline gates": "future review confirms the required price, relative-strength and concentration conditions",
    "Bewaakte modelrotatie uitgevoerd en verwerkt:": "Portefeuillerotatie voltooid:",
    "Bewaakte modelrotatie": "Portefeuillerotatie",
    "De shadow-engine": "Een tweede regelgebaseerde beoordeling",
    "shadow-engine": "tweede regelgebaseerde beoordeling",
    "alleen ter review": "aanvullend",
    "grotendeels in lijn met de bestaande regime-inschatting": "grotendeels in lijn met het primaire regimebeeld",
    "Dit geeft geen autoriteit voor portefeuillewijzigingen.": "Deze aanvullende controle verandert de portefeuilleacties niet.",
    "De normale discipline blijft leidend.": "Prijsbasis, relatieve sterkte en positiediscipline blijven leidend.",
    "Aanhouden met override": "Aanhouden — geen verdere wijziging in deze review",
    "override: rotation budget already used": "rotatielimiet bereikt voor deze review",
    "override min trade size not met": "positie te klein voor een efficiënte transactie",
    "release score": "reviewprioriteit",
    "Guarded auto-execution:": "Implemented change:",
    "Bewaakte auto-uitvoering:": "Verwerkte wijziging:",
    "Rotatiebestemming": "Portefeuilleallocatie",
    "een toekomstige run alle disciplinepoorten vrijgeeft": "een toekomstige review de vereiste prijs-, relatieve-sterkte- en concentratievoorwaarden bevestigt",
    "beschikbare churnruimte": "ruimte binnen de wekelijkse transactielimiet",
    "bewijs- en churnbegrensd": "afhankelijk van nieuwe prijs-, relatieve-sterkte- en concentratiebevestiging",
    "Systeemoverride: rotatiebudget is al gebruikt": "Rotatielimiet bereikt voor deze review",
    "rotatiebudget is al gebruikt": "rotatielimiet bereikt voor deze review",
    "Voer de vervangingsanalyse tegenover": "Herbeoordeel tegenover",
}

REGEX_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\brelease score\s+(\d+(?:\.\d+)?)", re.IGNORECASE),
        r"review priority \1",
    ),
    (
        re.compile(r"\breviewprioriteit\s+(\d+(?:\.\d+)?)", re.IGNORECASE),
        r"reviewprioriteit \1",
    ),
    (
        re.compile(r"\boverride:\s*rotation budget already used\b", re.IGNORECASE),
        "weekly rotation limit reached",
    ),
    (
        re.compile(r"\boverride\s+min trade size not met\b", re.IGNORECASE),
        "position too small for an efficient trade",
    ),
    (
        re.compile(r"\bRisk-on growth has persisted for (\d+) run\(s\)", re.IGNORECASE),
        r"Risk-on growth has persisted across \1 weekly observations",
    ),
    (
        re.compile(r"\bRisk-on groei houdt al (\d+) runs aan", re.IGNORECASE),
        r"Risk-on groei houdt al \1 wekelijkse meetmomenten aan",
    ),
    (
        re.compile(r"(?<!\.)\.\.(?!\.)"),
        ".",
    ),
    (
        re.compile(r"([!?])\1+"),
        r"\1",
    ),
)

FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("shadow_engine", re.compile(r"\bshadow[- ]engine\b", re.IGNORECASE)),
    ("runtime_macro_pack", re.compile(r"\bruntime macro pack\b", re.IGNORECASE)),
    ("rotation_engine_status", re.compile(r"\brotation engine status\b", re.IGNORECASE)),
    ("guarded_model_rotation", re.compile(r"\bguarded model rotation\b", re.IGNORECASE)),
    ("guarded_auto_execution", re.compile(r"\bguarded auto-execution\b", re.IGNORECASE)),
    ("release_score", re.compile(r"\brelease score\b", re.IGNORECASE)),
    ("hold_with_override", re.compile(r"\bhold with override\b", re.IGNORECASE)),
    ("dutch_hold_with_override", re.compile(r"\baanhouden met override\b", re.IGNORECASE)),
    ("raw_override", re.compile(r"\boverride(?::|\s+min trade size)", re.IGNORECASE)),
    ("review_only", re.compile(r"\breview-only\b|\balleen ter review\b", re.IGNORECASE)),
    ("diagnostic_only", re.compile(r"\bdiagnostic-only\b", re.IGNORECASE)),
    ("lane_scoring_authority", re.compile(r"\blane-scoring authority\b", re.IGNORECASE)),
    ("runtime_valuation", re.compile(r"\bruntime(?:-derived)? valuation\b", re.IGNORECASE)),
    ("model_action_weights", re.compile(r"\bmodel/action weights\b", re.IGNORECASE)),
    ("rotation_budget", re.compile(r"\brotation budget already used\b|\brotatiebudget is al gebruikt\b", re.IGNORECASE)),
    ("churn_budget", re.compile(r"\bchurn(?: budget|-gated|begrensd|ruimte)\b", re.IGNORECASE)),
    ("discipline_gates", re.compile(r"\bdiscipline gates\b|\bdisciplinepoorten\b", re.IGNORECASE)),
    ("run_parenthetical", re.compile(r"\brun\(s\)\b", re.IGNORECASE)),
    ("double_period", re.compile(r"(?<!\.)\.\.(?!\.)")),
)

NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)?%?")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^\)]+\)")


def normalize_client_language(text: str, *, language: str) -> str:
    cleaned = text
    for source, target in sorted(EXACT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        cleaned = cleaned.replace(source, target)
    for pattern, replacement in REGEX_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)
    return cleaned


def client_language_findings(text: str, *, language: str) -> list[str]:
    del language  # Reserved for future language-specific gates.
    findings: list[str] = []
    for code, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            findings.append(code)
    return findings


def numeric_multiset(text: str) -> Counter[str]:
    return Counter(NUMBER_RE.findall(text))


def markdown_link_multiset(text: str) -> Counter[str]:
    return Counter(MARKDOWN_LINK_RE.findall(text))


def evidence_summary(original: str, cleaned: str, *, language: str) -> dict[str, Any]:
    return {
        "language": language,
        "before_findings": client_language_findings(original, language=language),
        "after_findings": client_language_findings(cleaned, language=language),
        "numeric_multiset_preserved": numeric_multiset(original) == numeric_multiset(cleaned),
        "markdown_link_multiset_preserved": markdown_link_multiset(original) == markdown_link_multiset(cleaned),
        "idempotent": normalize_client_language(cleaned, language=language) == cleaned,
        "before_chars": len(original),
        "after_chars": len(cleaned),
    }
