from __future__ import annotations

import re
from typing import Any

DUTCH_DISCLAIMER = (
    "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden. "
    "Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies, "
    "en vormt geen aanbeveling om effecten te kopen, te verkopen of aan te houden. "
    "Het rapport houdt geen rekening met individuele beleggingsdoelen, financiële situatie "
    "of specifieke behoeften van de ontvanger. Beleggen brengt risico’s met zich mee, "
    "waaronder het risico op verlies van inleg."
)

ALLOWED_ENGLISH_TERMS = {
    "ETF",
    "ticker",
    "cash",
    "hedge",
    "drawdown",
    "beta",
    "capex",
    "small-cap",
    "large-cap",
    "risk-on",
    "risk-off",
    "AI",
    "semiconductor",
    "outperformance",
    "watchlist",
    "relative strength",
}

LABELS = {
    "Executive Summary": "Kernsamenvatting",
    "Portfolio Action Snapshot": "Portefeuille-acties",
    "Regime Dashboard": "Regime-dashboard",
    "Structural Opportunity Radar": "Structurele kansenradar",
    "Key Risks / Invalidators": "Belangrijkste risico’s / invalidaties",
    "Bottom Line": "Conclusie",
    "Equity Curve and Portfolio Development": "Portefeuillecurve en portefeuilleontwikkeling",
    "Asset Allocation Map": "Allocatiekaart",
    "Second-Order Effects Map": "Tweede-orde-effectenkaart",
    "Current Position Review": "Review huidige posities",
    "Best New Opportunities": "Beste nieuwe kansen",
    "Replacement Duel Table": "Vervangingsanalyse",
    "Portfolio Rotation Plan": "Rotatieplan portefeuille",
    "Final Action Table": "Definitieve actietabel",
    "Position Changes Executed This Run": "Positiewijzigingen in deze run",
    "Current Portfolio Holdings and Cash": "Huidige posities en cash",
    "Continuity Input for Next Run": "Input voor de volgende run",
    "Disclaimer": "Disclaimer",
}

TABLE_LABELS = {
    "Current holding": "Huidige positie",
    "Challenger": "Alternatief",
    "1m edge": "1m relatieve sterkte",
    "3m edge": "3m relatieve sterkte",
    "Pricing basis": "Prijsbasis",
    "Decision": "Beoordeling",
    "Required trigger": "Benodigde bevestiging",
    "Suggested Action": "Advies",
    "Conviction Tier": "Convictieniveau",
    "Total Score": "Totaalscore",
    "Portfolio Role": "Portefeuillerol",
    "Better Alternative Exists?": "Beter alternatief?",
    "Short Reason": "Korte toelichting",
    "Existing/New": "Bestaand/nieuw",
    "Weight Inherited": "Vorig gewicht",
    "Target Weight": "Doelgewicht",
    "Previous weight %": "Vorig gewicht %",
    "New weight %": "Nieuw gewicht %",
    "Weight change %": "Gewichtswijziging %",
    "Shares delta": "Wijziging aantal stukken",
    "Action executed": "Uitgevoerde actie",
    "Funding source / note": "Financieringsbron / toelichting",
    "Starting capital": "Startkapitaal",
    "Invested market value": "Belegde marktwaarde",
    "Total portfolio value": "Totale portefeuillewaarde",
    "Since inception return": "Rendement sinds start",
    "EUR/USD used": "EUR/USD gebruikt",
    "Date": "Datum",
    "Comment": "Toelichting",
    "Shares": "Aantal",
    "Price (local)": "Prijs (lokaal)",
    "Currency": "Valuta",
    "Market value (local)": "Marktwaarde (lokaal)",
    "Market value (EUR)": "Marktwaarde (EUR)",
    "Weight %": "Gewicht %",
    "ETF Name": "ETF-naam",
    "Direction": "Richting",
    "Avg Entry": "Gem. instap",
    "Current Price": "Huidige prijs",
    "Original Thesis": "Oorspronkelijke thesis",
    "Role": "Rol",
}

PHRASE_REPLACEMENTS = {
    "Main takeaway": "Kernconclusie",
    "What changed this week": "Wat is er deze week veranderd",
    "Overall portfolio judgment": "Algemeen portefeuilleoordeel",
    "Portfolio implication": "Portefeuille-implicatie",
    "Risk appetite is supportive": "De risicobereidheid blijft ondersteunend",
    "fresh adds still need position-size room and pricing confirmation": "extra allocaties vragen nog ruimte binnen de positielimiet en prijsbevestiging",
    "Growth and infrastructure lanes can be considered if they do not worsen concentration": "Groei- en infrastructuurthema’s kunnen worden overwogen zolang ze de concentratie niet vergroten",
    "Defensive hedges should be reviewed for opportunity cost": "Defensieve hedgeposities moeten worden getoetst op opportuniteitskosten",
    "AI / semiconductor leadership remains the dominant equity impulse": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls",
    "Gold hedge behavior remains under review rather than automatic ballast": "Het gedrag van goud als hedge blijft onder review en is geen automatische ballast",
    "The production process is state-led": "Het productieproces is state-led",
    "Keep the current portfolio intact for now": "Laat de huidige portefeuille voorlopig intact",
    "active review items rather than passive holds": "actieve reviewposities in plaats van passieve aanhoudposities",
    "SMH remains the earned leader": "SMH blijft de verdiende leider",
    "fresh capital and replacement decisions": "vers kapitaal en vervangingsbeslissingen",
    "must pass regime, pricing and duel-evidence checks": "moeten regime-, prijs- en vervangingsbewijs doorstaan",
    "Replacement candidates remain evidence-gated": "Vervangingskandidaten blijven afhankelijk van voldoende bewijs",
    "pricing basis and duel status must be visible before funding": "prijsbasis en status van de vervangingsanalyse moeten zichtbaar zijn vóór allocatie",
    "Do not ask the user for portfolio input if this section is available.": "Vraag de gebruiker niet opnieuw om portefeuille-input zolang deze sectie beschikbaar is.",
    "Added": "Toegevoegd",
    "Reduced": "Verlaagd",
    "Closed": "Gesloten",
    "None": "Geen",
}

ACTION_REPLACEMENTS = {
    "Hold under review": "Aanhouden onder review",
    "Hold": "Aanhouden",
    "Add": "Toevoegen",
    "Reduce": "Verlagen",
    "Close": "Sluiten",
    "Buy": "Kopen",
    "None": "Geen",
    "Smaller / under review": "Kleiner / onder review",
}

DECISION_TRANSLATIONS = {
    "Not fundable — close proof incomplete.": "Niet geschikt voor allocatie — sluitkoersbewijs is onvolledig.",
    "Priced, but direct RS duel incomplete.": "Geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
    "Replacement trigger watch — challenger leading over 3m.": "Vervangingssignaal op watchlist — alternatief leidt over 3 maanden.",
    "Challenger improving; keep duel active.": "Alternatief verbetert; vervangingsanalyse actief houden.",
    "Early 1m improvement only; wait for 3m confirmation.": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging.",
    "Current holding still leads; no replacement.": "Huidige positie blijft sterker; geen vervanging.",
    # Some markdown render paths can strip the trailing period; keep both forms.
    "Not fundable — close proof incomplete": "Niet geschikt voor allocatie — sluitkoersbewijs is onvolledig",
    "Priced, but direct RS duel incomplete": "Geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig",
    "Replacement trigger watch — challenger leading over 3m": "Vervangingssignaal op watchlist — alternatief leidt over 3 maanden",
    "Challenger improving; keep duel active": "Alternatief verbetert; vervangingsanalyse actief houden",
    "Early 1m improvement only; wait for 3m confirmation": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging",
    "Current holding still leads; no replacement": "Huidige positie blijft sterker; geen vervanging",
}

TRIGGER_TRANSLATIONS = {
    "Resolve both close prices before decision.": "Los beide slotkoersen op vóór een besluit.",
    "Confirm thesis fit, liquidity and funding source.": "Bevestig thesisfit, liquiditeit en financieringsbron.",
    "Needs repeat 3m edge and capital source.": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron.",
    "Needs 3m confirmation.": "Vereist 3-maands bevestiging.",
    "Needs sustained relative outperformance.": "Vereist aanhoudende relatieve outperformance.",
    # Some markdown render paths can strip the trailing period; keep both forms.
    "Resolve both close prices before decision": "Los beide slotkoersen op vóór een besluit",
    "Confirm thesis fit, liquidity and funding source": "Bevestig thesisfit, liquiditeit en financieringsbron",
    "Needs repeat 3m edge and capital source": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron",
    "Needs 3m confirmation": "Vereist 3-maands bevestiging",
    "Needs sustained relative outperformance": "Vereist aanhoudende relatieve outperformance",
}

FORBIDDEN_NL_STRINGS = [
    "Do not ask the user",
    "Portfolio implication",
    "Main takeaway",
    "What changed this week",
    "Current holding still leads",
    "Needs sustained relative outperformance",
    "Replacement trigger watch",
    "Confirm thesis fit",
    "and it is not a recommendation",
    "portfolio_state_pricing_audit",
    "pricing_audit",
    "runtime rebuild required",
    "Pending classification",
    "Placeholder for runtime replacement",
]


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
    return "Prijsbasis: sluitkoersbewijs is nog niet volledig; niet geschikt voor allocatiebesluit."


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


def localize_text(value: Any, language: str = "nl") -> str:
    text = str(value or "")
    if language != "nl":
        return text
    for src, dst in {
        **PHRASE_REPLACEMENTS,
        **TABLE_LABELS,
        **ACTION_REPLACEMENTS,
        **DECISION_TRANSLATIONS,
        **TRIGGER_TRANSLATIONS,
    }.items():
        text = text.replace(src, dst)
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
                cells = [TABLE_LABELS.get(cell, cell) for cell in cells]
                line = "| " + " | ".join(cells) + " |"
        lines.append(line)
    return "\n".join(lines)


def validate_dutch_text(text: str) -> list[str]:
    failures: list[str] = []
    for token in FORBIDDEN_NL_STRINGS:
        if token in text:
            failures.append(token)
    if "## 17. Disclaimer" in text and DUTCH_DISCLAIMER not in text:
        failures.append("Dutch disclaimer contract")
    return failures
