from __future__ import annotations

"""Shared Dutch terminology contract for runtime aliases and delivery guards.

This module wraps ``runtime.nl_terminology`` and centralizes the remaining
migration/runtime aliases that used to be duplicated across localization,
scrubbers, delivery HTML, and validators. Native Dutch reports remain guard-only;
legacy/non-native paths can reuse these exact aliases without creating another
broad translation layer.
"""

from runtime import nl_terminology as term

DUTCH_STATUS_ALIASES = {
    "No / under review": "Nee / onder herbeoordeling",
    "no / under review": "Nee / onder herbeoordeling",
    "None / under review": "Geen / onder herbeoordeling",
    "none / under review": "Geen / onder herbeoordeling",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "smaller / under review": "Kleiner / onder herbeoordeling",
    "Hold / monitor": "Aanhouden / monitoren",
    "hold / monitor": "Aanhouden / monitoren",
    "Hold under review": "Aanhouden, onder herbeoordeling",
    "hold under review": "Aanhouden, onder herbeoordeling",
    "Under review": "Onder herbeoordeling",
    "under review": "onder herbeoordeling",
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
    "Hold / replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden but replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden maar replaceable": "Aanhouden, maar vervangbaar",
    "Hold maar vervangbaar": "Aanhouden, maar vervangbaar",
}

ACTION_REPLACEMENTS = {
    **term.ACTION_REPLACEMENTS,
    **DUTCH_STATUS_ALIASES,
}

DECISION_TRANSLATIONS = {
    **term.DECISION_TRANSLATIONS,
    "Not fundable - close proof incomplete.": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig.",
    "Not fundable - close proof incomplete": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig",
    "Not fundable - valuation-grade challenger pricing required.": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist.",
    "Not fundable - valuation-grade challenger pricing required": "Niet geschikt voor allocatie — waarderingswaardige prijsbevestiging voor het alternatief is vereist",
    "Priced valuation-grade, but direct RS duel incomplete.": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
    "Priced valuation-grade, but direct RS duel incomplete": "Waarderingswaardig geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig",
    "Replacement trigger watch - challenger leading over 3m.": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden.",
    "Replacement trigger watch - challenger leading over 3m": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden",
    "Replacement trigger watch — challenger leading over 3m": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden",
}

TRIGGER_TRANSLATIONS = {
    **term.TRIGGER_TRANSLATIONS,
    "Upgrade challenger to valuation-grade pricing before any funding decision.": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit.",
    "Upgrade challenger to valuation-grade pricing before any funding decision": "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit",
}

LEGACY_ONLY_PHRASE_REPLACEMENTS = {
    "The production process is state-led": "Het rapport is opgebouwd vanuit gevalideerde portefeuille- en prijsdata",
    "Do not ask the user for portfolio input if this section is available.": "Vraag de gebruiker niet opnieuw om portefeuille-input zolang deze sectie beschikbaar is.",
}

CLIENT_SURFACE_EXACT_REPLACEMENTS = {
    **term.REPORT_LABELS,
    **term.TABLE_LABELS,
    **ACTION_REPLACEMENTS,
    **term.PHRASE_REPLACEMENTS,
    **term.EXACT_CLIENT_LANGUAGE_REPLACEMENTS,
    **DECISION_TRANSLATIONS,
    **TRIGGER_TRANSLATIONS,
    **DUTCH_STATUS_ALIASES,
    "WEEKLY ETF REVIEW": "WEKELIJKSE ETF-REVIEW",
    "WEEKLY ETF PRO REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Pro Review": "Wekelijkse ETF-review",
    "Investment Report": "Beleggersrapport",
    "Investor Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "Keep the current allocation": "Houd de huidige allocatie",
    "Keep the current allocation.": "Houd de huidige allocatie.",
    "Neeg geen": "Geen",
    "Neeg Geen": "Geen",
    "Neeg": "Nee",
}

PARTIAL_MIXED_EXACT_CLEANUPS = {
    source: target
    for source, target in DUTCH_STATUS_ALIASES.items()
    if "replaceable" in source or "vervangbaar" in source
}

REPLACEMENT_DUEL_PHRASE_CLEANUPS = {
    **DECISION_TRANSLATIONS,
    **TRIGGER_TRANSLATIONS,
}

NATIVE_STATE_LABEL_REPLACEMENTS = {
    "Healthcare quality and defensive growth": "Healthcarekwaliteit en defensieve groei",
    "Non-U.S. developed market diversification": "Ontwikkelde markten buiten de VS",
    "Non-U.S. developed diversification": "Ontwikkelde markten buiten de VS",
    "Latest 4 mei close basis; +8 SMH from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH vanuit cash",
    "Latest 4 May close basis; +8 SMH from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH vanuit cash",
    "Runtime valuation from immutable pricing audit and explicit portfolio state": "Waardering uit onveranderlijke prijsaudit en expliciete portefeuillestaat",
    "Runtime valuation repriced from official portfolio-state shares": "Waardering op basis van officiële portefeuillestaat en gevalideerde slotkoersen",
    "Rotation destination": "Rotatiebestemming",
    "No / under review": "Nee / onder herbeoordeling",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "| Long |": "| Longpositie |",
}

NATIVE_STATE_LABEL_FORBIDDEN = sorted(NATIVE_STATE_LABEL_REPLACEMENTS)

# Regex contracts intentionally stay centralized here so consumers can import the
# same symbols. Native Dutch runtime reports remain guard-only; no broad regex
# prose translation is applied to native output.
REGEX_CLIENT_LANGUAGE_REPLACEMENTS = list(term.REGEX_CLIENT_LANGUAGE_REPLACEMENTS)
NATIVE_REGEX_REPLACEMENTS = []

CLIENT_FACING_TOKEN_REPLACEMENTS = {
    "Pending classification": "Mixed / not yet decisive",
    "Placeholder for runtime replacement": "Latest available classified input",
    "runtime rebuild required": "Latest available classified input",
    "fresh_cash_smaller_or_review": "Fresh capital only after review or at smaller size",
    "failed_fresh_cash_test": "Position does not pass the fresh-capital test",
    "replaceable_status": "Position is under replacement review",
    "review_age_ge_2": "Review has persisted for multiple report cycles",
    "review_age_ge_3": "Review has persisted for several report cycles",
    "role_impaired": "Portfolio role is impaired",
    "destination from trade_intents": "Proposed destination from the rotation plan",
    "trade_intents": "proposed trade intents",
    "target_weights": "target allocations",
    "rotation_decisions": "rotation decisions",
    "churn_budget_used": "rotation budget already used",
    "Reason codes": "Decision rationale",
    "Redencodes": "Toelichting",
}

DUTCH_MD_MARKERS = [
    "kernsamenvatting",
    "portefeuille-acties",
    "huidige posities",
    "beleggersrapport",
    "wekelijks",
    "wekelijkse etf-review",
    "primair regime",
    "geopolitiek regime",
    "kernconclusie",
    "dit rapport wordt uitsluitend verstrekt",
]

ENGLISH_MD_MARKERS = [
    "executive summary",
    "portfolio action snapshot",
    "current portfolio holdings and cash",
    "weekly etf review",
    "weekly etf pro review",
    "investor report",
    "primary regime",
    "main takeaway",
    "this report is for informational",
]

DUTCH_DELIVERY_FORBIDDEN_TOKENS = [
    "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Tuesday",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
    "PRIMARY REGIME", "GEOPOLITICAL REGIME", "MAIN TAKEAWAY",
    "Investor Report", "Investment Report", "Analyst Report",
    "Mixed / not yet decisive", "Keep the current allocation", "confidence",
    "Equity Curve (EUR)", "Portfolio value (EUR)",
    "fresh_cash_smaller_or_review", "failed_fresh_cash_test", "replaceable_status",
    "review_age_ge_2", "review_age_ge_3", "churn_budget_used",
    "trade_intents", "target_weights", "rotation_decisions",
]


def combined_text_replacements() -> dict[str, str]:
    return {
        **term.combined_text_replacements(),
        **ACTION_REPLACEMENTS,
        **DECISION_TRANSLATIONS,
        **TRIGGER_TRANSLATIONS,
        **DUTCH_STATUS_ALIASES,
        **LEGACY_ONLY_PHRASE_REPLACEMENTS,
    }
