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
    "ETF", "ETFs", "ticker", "tickers", "cash", "hedge", "drawdown", "beta", "capex",
    "small-cap", "large-cap", "risk-on", "risk-off", "AI", "semiconductor", "outperformance",
    "watchlist", "UCITS", "USD", "EUR", "NAV",
}

LABELS = {
    "Weekly ETF Review": "Wekelijkse ETF-review",
    "Investor Report": "Beleggersrapport",
    "Investment Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "Primary Regime": "Primair regime",
    "PRIMARY REGIME": "PRIMAIR REGIME",
    "Geopolitical Regime": "Geopolitiek regime",
    "GEOPOLITICAL REGIME": "GEOPOLITIEK REGIME",
    "Main Takeaway": "Kernconclusie",
    "MAIN TAKEAWAY": "KERNCONCLUSIE",
    "Executive Summary": "Kernsamenvatting",
    "Portfolio Action Snapshot": "Portefeuille-acties",
    "Regime Dashboard": "Regime-dashboard",
    "Structural Opportunity Radar": "Structurele kansenradar",
    "Short Opportunity Radar": "Shortkansenradar",
    "Key Risks / Invalidators": "Belangrijkste risico’s / invalidaties",
    "Bottom Line": "Conclusie",
    "Equity Curve and Portfolio Development": "Portefeuillecurve en portefeuilleontwikkeling",
    "Asset Allocation Map": "Allocatiekaart",
    "Second-Order Effects Map": "Tweede-orde-effectenkaart",
    "Current Position Review": "Review huidige posities",
    "Best New Opportunities": "Beste nieuwe kansen",
    "Replacement Duel Table": "Vervangingsanalyse",
    "Replacement Duel Table v2": "Vervangingsanalyse",
    "Portfolio Rotation Plan": "Rotatieplan portefeuille",
    "Final Action Table": "Definitieve actietabel",
    "Position Changes Executed This Run": "Positiewijzigingen in deze run",
    "Current Portfolio Holdings and Cash": "Huidige posities en cash",
    "Continuity Input for Next Run": "Input voor de volgende run",
    "Carry-forward input for next run": "Input voor de volgende run",
    "Disclaimer": "Disclaimer",
}

TABLE_LABELS = {
    "Theme": "Thema",
    "Primary ETF": "Primaire ETF",
    "Alternative ETF": "Alternatieve ETF",
    "Why it matters": "Waarom relevant",
    "Structural fit": "Structurele fit",
    "Macro timing": "Macro-timing",
    "Status": "Status",
    "What needs to happen": "Benodigde bevestiging",
    "Time horizon": "Tijdshorizon",
    "Short theme": "Shortthema",
    "Candidate ETF": "Kandidaat-ETF",
    "Short thesis": "Shortthese",
    "Trigger": "Trigger",
    "Invalidation": "Invalidering",
    "Confidence": "Vertrouwen",
    "Bucket": "Segment",
    "Stance": "Positionering",
    "Reason": "Toelichting",
    "Driver": "Drijver",
    "First-order effect": "Eerste-orde-effect",
    "Second-order effect": "Tweede-orde-effect",
    "Likely beneficiaries": "Waarschijnlijke winnaars",
    "Likely losers": "Kwetsbare segmenten",
    "ETF implication": "ETF-implicatie",
    "Timing": "Timing",
    "Ticker": "Ticker",
    "Action": "Actie",
    "Score": "Score",
    "Fresh cash": "Nieuw kapitaal",
    "Role": "Rol",
    "Next test": "Volgende toets",
    "Current holding": "Huidige positie",
    "Challenger": "Alternatief",
    "Alternative": "Alternatief",
    "1m edge": "1m relatieve sterkte",
    "3m edge": "3m relatieve sterkte",
    "1m relative strength": "1m relatieve sterkte",
    "3m relative strength": "3m relatieve sterkte",
    "Pricing basis": "Prijsbasis",
    "Decision": "Beoordeling",
    "Required trigger": "Benodigde bevestiging",
    "Current status": "Status",
    "Why I’m considering it": "Waarom op de radar",
    "Why I'm considering it": "Waarom op de radar",
    "Current holding": "Huidige positie",
    "Suggested Action": "Advies",
    "Conviction Tier": "Convictieniveau",
    "Total Score": "Totaalscore",
    "Portfolio Role": "Portefeuillerol",
    "Better Alternative Exists?": "Sterker alternatief beschikbaar?",
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
    "Equity-curve state": "Status portefeuillecurve",
    "Notes": "Toelichting",
    "Date": "Datum",
    "Portfolio value (EUR)": "Portefeuillewaarde (EUR)",
    "Comment": "Opmerking",
    "Shares": "Aantal aandelen",
    "Price (local)": "Prijs (lokaal)",
    "Currency": "Valuta",
    "Market value (local)": "Marktwaarde (lokaal)",
    "Market value (EUR)": "Marktwaarde (EUR)",
    "Weight %": "Gewicht %",
    "ETF Name": "ETF-naam",
    "Direction": "Richting",
    "Avg Entry": "Gem. instap",
    "Current Price": "Huidige prijs",
    "P/L %": "P/L %",
    "Original Thesis": "Oorspronkelijke thesis",
}

ACTION_REPLACEMENTS = {
    "Hold under review": "Aanhouden, onder herbeoordeling",
    "Hold / replaceable": "Aanhouden, maar vervangbaar",
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
    "Hold": "Aanhouden",
    "Add": "Toevoegen",
    "Reduce": "Verlagen",
    "Close": "Sluiten",
    "Buy": "Kopen",
    "None": "Geen",
    "Existing": "Bestaand",
    "New": "Nieuw",
    "Yes": "Ja",
    "No": "Nee",
    "Active": "Actief",
    "Duel required": "Vervangingsanalyse vereist",
    "Under review": "Onder herbeoordeling",
    "Watchlist / under review": "Volglijst / onder herbeoordeling",
    "Actionable now": "Nu actiegericht",
    "Neutral": "Neutraal",
    "Overweight": "Overwogen",
    "Underweight": "Onderwogen",
    "Watchlist": "Volglijst",
    "Immediate": "Direct",
    "Medium": "Gemiddeld",
    "High": "Hoog",
    "Low": "Laag",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
}

PHRASE_REPLACEMENTS = {
    "This report is for informational and educational purposes only; please see the disclaimer at the end.": "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde.",
    "Main takeaway": "Kernconclusie",
    "What changed this week": "Wat is er deze week veranderd",
    "What changed": "Wat veranderde",
    "Overall portfolio judgment": "Algemeen portefeuilleoordeel",
    "Portfolio implication": "Portefeuille-implicatie",
    "Portfolio implications": "Portefeuille-implicaties",
    "Cross-asset confirmation": "Cross-asset bevestiging",
    "Policy catalysts transferred to the report": "Beleidscatalysatoren in het rapport",
    "Affected lanes": "Geraakte thema’s",
    "Current regime": "Huidig regime",
    "Decision rule": "Beslisregel",
    "Regime snapshot": "Regimesamenvatting",
    "Available cash": "Beschikbare cash",
    "Portfolio table": "Portefeuilletabel",
    "Watchlist / dynamic radar memory": "Volglijst / dynamisch radargeheugen",
    "Recommendation discipline continuity": "Continuïteit in aanbevelingsdiscipline",
    "Changes since last review": "Wijzigingen sinds de vorige review",
    "Constraints": "Randvoorwaarden",
    "Leverage allowed": "Leverage toegestaan",
    "Margin usage": "Margegebruik",
    "Max position size": "Maximale positiegrootte",
    "Max number of positions": "Maximaal aantal posities",
    "Drawdown tolerance": "Drawdown-tolerantie",
    "Income vs growth preference": "Voorkeur inkomen versus groei",
    "Risk appetite is supportive": "De risicobereidheid blijft ondersteunend",
    "fresh adds still need position-size room and pricing confirmation": "aanvullende allocaties vragen nog ruimte binnen de positielimiet en koersbevestiging",
    "Growth and infrastructure lanes can be considered if they do not worsen concentration": "Groei- en infrastructuurthema’s kunnen worden overwogen zolang ze de concentratie niet vergroten",
    "Defensive hedges should be reviewed for opportunity cost": "Defensieve hedgeposities moeten worden getoetst op opportuniteitskosten",
    "AI / semiconductor leadership remains the dominant equity impulse": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls",
    "AI and semiconductor leadership remains the dominant equity impulse": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls",
    "Gold hedge behavior remains under review rather than automatic ballast": "Het gedrag van goud als hedge blijft onder herbeoordeling en is geen automatische stabilisator",
    "Keep the current portfolio intact for now": "Laat de huidige portefeuille voorlopig intact",
    "active review items rather than passive holds": "posities onder actieve herbeoordeling in plaats van passieve aanhoudposities",
    "SMH remains the earned leader": "SMH blijft de best onderbouwde kernpositie",
    "Keep SMH as the earned leader, but do not confuse narrow leadership with broad diversification.": "SMH blijft de best onderbouwde kernpositie, maar smal marktleiderschap mag niet worden verward met brede portefeuillediversificatie.",
    "Keep SMH as the earned leader": "SMH blijft de best onderbouwde kernpositie",
    "do not confuse narrow leadership with broad diversification": "verwar smal marktleiderschap niet met brede portefeuillediversificatie",
    "fresh capital and replacement decisions": "nieuw kapitaal en vervangingsbeslissingen",
    "must pass regime, pricing and duel-evidence checks": "moeten het regimebeeld, de koersbevestiging en de vervangingsanalyse doorstaan",
    "Require replacement duels for SPY overlap, PPA implementation quality and PAVE versus GRID before funding challengers.": "Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, PPA en PAVE expliciet worden getoetst aan hun belangrijkste vervangingskandidaten.",
    "Require replacement duels": "Vervangingsanalyses zijn vereist",
    "Keep cash discipline because the regime supports selectivity more than broad risk expansion.": "Behoud kasdiscipline, omdat het regime selectiviteit sterker ondersteunt dan brede risico-uitbreiding.",
    "Keep cash discipline": "Behoud kasdiscipline",
    "broad risk expansion": "brede risico-uitbreiding",
    "broad diversification": "brede portefeuillediversificatie",
    "narrow leadership": "smal marktleiderschap",
    "Replacement candidates remain evidence-gated": "Vervangingskandidaten blijven afhankelijk van voldoende bewijs",
    "pricing basis and duel status must be visible before funding": "prijsbasis en status van de vervangingsanalyse moeten zichtbaar zijn vóór allocatie",
    "Force alternative duel; upgrade, reduce, replace, or close": "Vervangingsanalyse vereist; verhoog, verlaag, vervang of sluit de positie",
    "Run hedge validity test and compare with alternatives": "Voer een hedge-validiteitstest uit en vergelijk met alternatieven",
    "Best structural opportunities not yet actionable": "Beste structurele kansen die nog niet actiegericht zijn",
    "Notable lanes assessed but not promoted this week": "Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd",
    "Why not promoted": "Waarom niet gepromoveerd",
    "What would change that": "Wat dat zou veranderen",
    "The production process is state-led": "Het rapport is opgebouwd vanuit gevalideerde portefeuille- en prijsdata",
    "Do not ask the user for portfolio input if this section is available.": "Vraag de gebruiker niet opnieuw om portefeuille-input zolang deze sectie beschikbaar is.",
    "Aanhouden under review": "Aanhouden, onder herbeoordeling",
    "under review": "onder herbeoordeling",
    "thesisfit": "aansluiting op de beleggingscase",
    "prijsbewijs": "koersbevestiging",
    "verdiende leider": "best onderbouwde kernpositie",
    "vers kapitaal": "nieuw kapitaal",
    "actiebias": "beslissingsrichting",
    "reviewpositie": "positie onder actieve herbeoordeling",
    "reviewposities": "posities onder actieve herbeoordeling",
    "nuttige ballast": "stabiliserende hedgefunctie",
}

DECISION_TRANSLATIONS = {
    "Not fundable — close proof incomplete.": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig.",
    "Priced, but direct RS duel incomplete.": "Geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig.",
    "Replacement trigger watch — challenger leading over 3m.": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden.",
    "Challenger improving; keep duel active.": "Het alternatief verbetert; houd de vervangingsanalyse actief.",
    "Early 1m improvement only; wait for 3m confirmation.": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging.",
    "Current holding still leads; no replacement.": "Huidige positie blijft sterker; geen vervanging.",
    "Not fundable — close proof incomplete": "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig",
    "Priced, but direct RS duel incomplete": "Geprijsd, maar de directe relatieve-sterkteanalyse is onvolledig",
    "Replacement trigger watch — challenger leading over 3m": "Vervangingskandidaat blijft op de volglijst — het alternatief leidt over drie maanden",
    "Challenger improving; keep duel active": "Het alternatief verbetert; houd de vervangingsanalyse actief",
    "Early 1m improvement only; wait for 3m confirmation": "Alleen vroege 1-maands verbetering; wacht op 3-maands bevestiging",
    "Current holding still leads; no replacement": "Huidige positie blijft sterker; geen vervanging",
}

TRIGGER_TRANSLATIONS = {
    "Resolve both close prices before decision.": "Los beide slotkoersen op vóór een besluit.",
    "Confirm thesis fit, liquidity and funding source.": "Bevestig aansluiting op de beleggingscase, liquiditeit en financieringsbron.",
    "Needs repeat 3m edge and capital source.": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron.",
    "Needs 3m confirmation.": "Vereist 3-maands bevestiging.",
    "Needs sustained relative outperformance.": "Vereist aanhoudende relatieve outperformance.",
    "Resolve both close prices before decision": "Los beide slotkoersen op vóór een besluit",
    "Confirm thesis fit, liquidity and funding source": "Bevestig aansluiting op de beleggingscase, liquiditeit en financieringsbron",
    "Needs repeat 3m edge and capital source": "Vereist herhaalde 3-maands voorsprong en duidelijke financieringsbron",
    "Needs 3m confirmation": "Vereist 3-maands bevestiging",
    "Needs sustained relative outperformance": "Vereist aanhoudende relatieve outperformance",
}

FORBIDDEN_NL_STRINGS = [
    "Do not ask the user",
    "Portfolio implication",
    "Main takeaway",
    "What changed this week",
    "WAT VERANDERDE THIS WEEK",
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
    "state-led",
    "workflow",
    "manifest",
    "artifact",
    "output/",
    "runtime NAV",
    "Section 7 uses",
    "Section 15",
    "Keep SMH",
    "Require replacement",
    "Force alternative",
    "but vers kapitaal",
    "but treat",
    "earned leader",
    "price proof",
    "thesisfit",
    "actiebias",
    "reviewpositie",
    "verdiende leider",
    "prijsbewijs",
    "vers kapitaal",
]

MIXED_LANGUAGE_PATTERNS = [
    re.compile(r"\b(but|keep|require|force|funding|fundable|existing|current status|duel required|under review)\b", re.I),
    re.compile(r"\b(Hold|Add|Reduce|Close|Existing|Yes|No|None)\b"),
]
DUTCH_FUNCTION_WORDS_RE = re.compile(r"\b(de|het|een|maar|moet|moeten|blijft|blijven|huidige|portefeuille|kapitaal|vervanging|aanhouden|verlagen|sluiten|toevoegen|onder|beoordeling)\b", re.I)


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


def localize_text(value: Any, language: str = "nl") -> str:
    text = str(value or "")
    if language != "nl":
        return text
    replacements = {**LABELS, **PHRASE_REPLACEMENTS, **TABLE_LABELS, **ACTION_REPLACEMENTS, **DECISION_TRANSLATIONS, **TRIGGER_TRANSLATIONS}
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
