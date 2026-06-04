from __future__ import annotations

import re
from typing import Any

from runtime import nl_terminology as term

# Central terminology aliases. Keep these names for backward-compatible imports,
# but source the actual vocabulary from runtime.nl_terminology.
DUTCH_DISCLAIMER = term.DUTCH_DISCLAIMER
ALLOWED_ENGLISH_TERMS = term.ALLOWED_ENGLISH_TERMS
LABELS = term.REPORT_LABELS
TABLE_LABELS = term.TABLE_LABELS
ACTION_REPLACEMENTS = term.ACTION_REPLACEMENTS
PHRASE_REPLACEMENTS = term.PHRASE_REPLACEMENTS
DECISION_TRANSLATIONS = term.DECISION_TRANSLATIONS
TRIGGER_TRANSLATIONS = term.TRIGGER_TRANSLATIONS
FORBIDDEN_NL_STRINGS = term.FORBIDDEN_NL_STRINGS

# Legacy-only phrases that are still accepted in older non-native Dutch renders.
# New terminology should be added to runtime.nl_terminology, not here.
LEGACY_ONLY_PHRASE_REPLACEMENTS = {
    "The production process is state-led": "Het rapport is opgebouwd vanuit gevalideerde portefeuille- en prijsdata",
    "Do not ask the user for portfolio input if this section is available.": "Vraag de gebruiker niet opnieuw om portefeuille-input zolang deze sectie beschikbaar is.",
}

MIXED_LANGUAGE_PATTERNS = [
    re.compile(r"\b(but|keep|require|force|funding|fundable|existing|current status|duel required|under review)\b", re.I),
    re.compile(r"\b(Hold|Add|Reduce|Close|Existing|Yes|No|None)\b"),
]
DUTCH_FUNCTION_WORDS_RE = re.compile(
    r"\b(de|het|een|maar|moet|moeten|blijft|blijven|huidige|portefeuille|kapitaal|vervanging|aanhouden|verlagen|sluiten|toevoegen|onder|beoordeling)\b",
    re.I,
)


def localized_pricing_basis(row: dict[str, Any], language: str = "en") -> str:
    current_date = row.get("current_close_date") or ""
    challenger_date = row.get("challenger_close_date") or ""
    if language != "nl":
        if current_date and challenger_date:
            return f"Current and challenger closes validated on {current_date} / {challenger_date}."
        return "Close-price proof incomplete; not decision-grade."
    if current_date and challenger_date and current_date == challenger_date:
        return f"Prijsbasis: huidige positie en alternatief zijn beide gevalideerd op slotkoersen van {current_date}."
    if current_date and challenger_date:
        return f"Prijsbasis: huidige positie gevalideerd op {current_date}; alternatief op {challenger_date}."
    return "Prijsbasis: sluitkoersbevestiging is nog niet volledig; niet geschikt voor allocatiebesluit."


def localize_decision(value: Any, language: str = "en") -> str:
    text = str(value or "").strip()
    if language == "nl":
        return DECISION_TRANSLATIONS.get(text, text)
    return text


def localize_trigger(value: Any, language: str = "en") -> str:
    text = str(value or "").strip()
    if language == "nl":
        return TRIGGER_TRANSLATIONS.get(text, text)
    return text


def localize_action(value: Any, language: str = "en") -> str:
    text = str(value or "").strip()
    if language == "nl":
        return ACTION_REPLACEMENTS.get(text, text)
    return text


def localize_label(value: str, language: str = "en") -> str:
    if language != "nl":
        return value
    return LABELS.get(value) or TABLE_LABELS.get(value) or value


def _replace_word_boundary(text: str, src: str, dst: str) -> str:
    if re.fullmatch(r"[A-Za-z][A-Za-z /?'-]*", src):
        return re.sub(rf"(?<![A-Za-z0-9]){re.escape(src)}(?![A-Za-z0-9])", dst, text)
    return text.replace(src, dst)


def _central_replacements() -> dict[str, str]:
    return {**term.combined_text_replacements(), **LEGACY_ONLY_PHRASE_REPLACEMENTS}


def localize_text(value: Any, language: str = "nl") -> str:
    text = str(value or "")
    if language != "nl":
        return text
    replacements = _central_replacements()
    for src in sorted(replacements, key=len, reverse=True):
        text = _replace_word_boundary(text, src, replacements[src])
    text = re.sub(
        r"This report is provided for informational and educational purposes only\..*?possible loss of principal\.",
        DUTCH_DISCLAIMER,
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden\..*?possible loss of principal\.",
        DUTCH_DISCLAIMER,
        text,
        flags=re.DOTALL,
    )
    return text


def localize_markdown_table_headers(markdown: str, language: str = "nl") -> str:
    if language != "nl":
        return markdown
    lines: list[str] = []
    for line in markdown.splitlines():
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and not all(set(cell) <= {"-", ":"} for cell in cells):
                cells = [localize_text(cell, language="nl") for cell in cells]
                line = "| " + " | ".join(cells) + " |"
        lines.append(line)
    return "\n".join(lines)


def _sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def detect_mixed_language_sentences(text: str) -> list[str]:
    failures: list[str] = []
    for sentence in _sentences(text):
        if sentence.startswith("|"):
            continue
        if DUTCH_FUNCTION_WORDS_RE.search(sentence) and any(pattern.search(sentence) for pattern in MIXED_LANGUAGE_PATTERNS):
            failures.append(sentence[:180])
    return failures


def validate_dutch_text(text: str) -> list[str]:
    failures: list[str] = []
    for token in FORBIDDEN_NL_STRINGS:
        if token in text:
            failures.append(token)
    mixed = detect_mixed_language_sentences(text)
    failures.extend([f"mixed-language sentence: {sentence}" for sentence in mixed[:10]])
    if "## 17. Disclaimer" in text and DUTCH_DISCLAIMER not in text:
        failures.append("Dutch disclaimer contract")
    return failures
