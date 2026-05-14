from __future__ import annotations

import re

# Centralized Dutch mappings for report body sections that are generated from
# runtime artifacts: radar tables, action tables, valuation-history notes and
# analyst/continuity appendix rows. This layer is deliberately table/section
# oriented so we do not keep adding one-off replacements in the workflow.

TABLE_HEADER_MAPPINGS = {
    "Theme": "Thema",
    "Short theme": "Shortthema",
    "Primary ETF": "Primaire ETF",
    "Alternative ETF": "Alternatieve ETF",
    "Alternative / hedge": "Alternatief / hedge",
    "Current holding": "Huidige positie",
    "Current exposure": "Huidige blootstelling",
    "Current proxy": "Huidige proxy",
    "Candidate ETF": "Kandidaat-ETF",
    "Implementation proxy": "Implementatieproxy",
    "Alternative proxy": "Alternatieve proxy",
    "Why it matters": "Waarom dit relevant is",
    "Why not promoted": "Waarom niet gepromoveerd",
    "What would change that": "Wat dat zou veranderen",
    "What needs to happen": "Benodigde bevestiging",
    "Required trigger": "Benodigde bevestiging",
    "Required confirmation": "Benodigde bevestiging",
    "Time horizon": "Tijdshorizon",
    "Current status": "Huidige status",
    "Status": "Status",
    "Stance": "Houding",
    "Reason": "Reden",
    "Decision": "Beoordeling",
    "Action": "Actie",
    "Sizing action": "Positiegrootte-actie",
    "Fresh cash test": "Nieuw-kapitaaltoets",
    "Existing / new": "Bestaand / nieuw",
    "Existing": "Bestaand",
    "New weight": "Nieuw gewicht",
    "Weight %": "Gewicht %",
    "Contribution %": "Bijdrage %",
    "Contribution": "Bijdrage",
    "Portfolio role": "Portefeuillerol",
    "Role": "Rol",
    "Bucket": "Categorie",
    "Type": "Type",
    "Regime fit": "Aansluiting op regime",
    "Macro timing": "Macro-timing",
    "Structural fit": "Structurele aansluiting",
    "Pricing basis": "Prijsbasis",
    "Pricing status": "Prijsstatus",
    "Short thesis": "Short-thesis",
    "Trigger": "Trigger",
    "Invalidation": "Invalidatie",
    "Invalidator": "Invalidatie",
    "First-order effect": "Eerste-orde-effect",
    "Second-order effect": "Tweede-orde-effect",
    "Likely beneficiaries": "Waarschijnlijke winnaars",
    "Likely losers": "Waarschijnlijke verliezers",
    "ETF implication": "ETF-implicatie",
    "Why I’m considering it": "Waarom dit wordt overwogen",
    "Why I'm considering it": "Waarom dit wordt overwogen",
    "Original Thesis": "Oorspronkelijke thesis",
    "Original thesis": "Oorspronkelijke thesis",
    "Continuity note": "Continuïteitsnotitie",
    "Notes": "Toelichting",
    "Comment": "Opmerking",
    "Date": "Datum",
    "Portfolio value (EUR)": "Portefeuillewaarde (EUR)",
    "Equity Curve (EUR)": "Portefeuillecurve (EUR)",
}

ENUM_VALUE_MAPPINGS = {
    "None": "Geen",
    "Yes": "Ja",
    "No": "Nee",
    "Hold": "Aanhouden",
    "Add": "Toevoegen",
    "Reduce": "Verlagen",
    "Close": "Sluiten",
    "Buy": "Kopen",
    "Sell": "Verkopen",
    "Existing": "Bestaand",
    "New": "Nieuw",
    "Candidate": "Kandidaat",
    "Watchlist": "Volglijst",
    "Watchlist / under review": "Volglijst / onder herbeoordeling",
    "Under review": "Onder herbeoordeling",
    "Funded": "Gefinancierd",
    "Surface": "Gesignaleerd",
    "Surfaced": "Gesignaleerd",
    "Not promoted": "Niet gepromoveerd",
    "Long alternative": "Long-alternatief",
    "Defensive hedge": "Defensieve hedge",
    "Inflation hedge": "Inflatiehedge",
    "Short candidate": "Shortkandidaat",
    "High": "Hoog",
    "Medium": "Gemiddeld",
    "Moderate": "Gemiddeld",
    "Low": "Laag",
}

SECTION_TITLE_MAPPINGS = {
    "Notable lanes assessed but not promoted this week": "Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd",
    "Notable lanes assessed maar not promoted this week": "Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd",
    "Short Opportunity Radar": "Shortkansenradar",
    "Alternative Duel Table": "Alternatievenanalyse",
    "Replacement Duel Table": "Vervangingsanalyse",
    "Trade / Action Audit": "Transactie- en actie-audit",
    "Analyst Report": "Analistenrapport",
    "Analyst Appendix": "Analistenbijlage",
    "Continuity Input for Next Run": "Input voor de volgende run",
}

RADAR_PHRASE_MAPPINGS = {
    "Scored below the live radar cutoff versus stronger funded and challenger lanes.": "Scoorde onder de actuele radardrempel ten opzichte van sterker gefinancierde posities en alternatieven.",
    "No acceleration signal this week.": "Deze week geen versnelling zichtbaar.",
    "Momentum not decisive this week.": "Momentum is deze week niet doorslaggevend.",
    "Macro backdrop stabilized.": "Macro-achtergrond is gestabiliseerd.",
    "Leadership not broad enough this week.": "Leiderschap is deze week nog niet breed genoeg.",
    "Inflation pressure moderated.": "Inflatiedruk is afgenomen.",
    "Relative strength remains constructive.": "Relatieve sterkte blijft constructief.",
    "Power demand remains structurally strong.": "Stroomvraag blijft structureel sterk.",
    "Commodity trend remains mixed.": "Grondstoffentrend blijft gemengd.",
    "Geopolitical premium remains elevated.": "Geopolitieke risicopremie blijft verhoogd.",
    "Energy security remains relevant.": "Energiezekerheid blijft relevant.",
    "Domestic growth remains resilient.": "Binnenlandse groei blijft veerkrachtig.",
    "AI compute and hyperscaler demand remain resilient.": "Vraag naar AI-rekenkracht en hyperscalers blijft veerkrachtig.",
    "Utility capex cycle remains supportive.": "De capexcyclus bij nutsbedrijven blijft ondersteunend.",
    "Materials remain strategically important.": "Materialen blijven strategisch belangrijk.",
    "Defense spending trend remains intact.": "De trend in defensie-uitgaven blijft intact.",
    "Nuclear sentiment remains constructive.": "Sentiment rond kernenergie blijft constructief.",
    "India remains structurally strong.": "India blijft structureel sterk.",
}

ACTION_DECISION_MAPPINGS = {
    "Current holding still leads; no replacement.": "Huidige positie blijft leidend; geen vervanging.",
    "Alternative improving; keep replacement duel active.": "Alternatief verbetert; houd de vervangingsanalyse actief.",
    "Challenger improving; keep duel active.": "Alternatief verbetert; houd de vervangingsanalyse actief.",
    "Not fundable — close missing.": "Niet geschikt voor allocatie — slotkoers ontbreekt.",
    "pricing row present but close missing": "prijsregel aanwezig, maar slotkoers ontbreekt",
    "Needs positive 60d edge plus portfolio-fit improvement before funding.": "Vereist positieve 60-daagse relatieve sterkte en betere portefeuilleaansluiting vóór allocatie.",
    "Needs sustained relative outperformance and portfolio-fit improvement before funding.": "Vereist aanhoudende relatieve outperformance en betere portefeuilleaansluiting vóór allocatie.",
    "Needs sustained relative outperformance before funding.": "Vereist aanhoudende relatieve outperformance vóór allocatie.",
    "Keep replacement duel active.": "Houd de vervangingsanalyse actief.",
    "No replacement.": "Geen vervanging.",
    "Duel required.": "Vervangingsanalyse vereist.",
    "Close missing.": "Slotkoers ontbreekt.",
}

VALUATION_HISTORY_MAPPINGS = {
    "Inaugural model portfolio established": "Initiële modelportefeuille vastgesteld",
    "Fresh per-ticker repricing using latest completed close set": "Verse herprijzing per ticker op basis van de meest recente volledige slotkoersset",
    "Fresh six-of-six repricing using completed 20 April close set": "Verse herprijzing voor zes van zes posities op basis van de volledige slotkoersset van 20 april",
    "Fresh five-of-six repricing; PPA carried forward": "Verse herprijzing voor vijf van zes posities; PPA doorgeschoven",
    "Fresh six-of-six repricing using persisted 2026-04-29 audit": "Verse herprijzing voor zes van zes posities op basis van de vastgelegde prijsaudit van 2026-04-29",
    "Fresh five-of-six pricing recovery; GLD carried forward": "Prijsherstel voor vijf van zes posities; GLD doorgeschoven",
    "Latest 4 May close basis; +8 SMH executed from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH uitgevoerd vanuit cash",
    "Latest close basis": "Meest recente slotkoersbasis",
    "carried forward": "doorgeschoven",
    "pricing recovery": "prijsherstel",
    "repricing": "herprijzing",
}

ANALYST_APPENDIX_MAPPINGS = {
    "Original Thesis": "Oorspronkelijke thesis",
    "Original thesis": "Oorspronkelijke thesis",
    "Thesis changes": "Thesiswijzigingen",
    "Strongest secular growth exposure.": "Sterkste structurele groeiblootstelling.",
    "Defense thesis valid but vehicle under review.": "Defensiethesis is valide, maar ETF-implementatie staat onder herbeoordeling.",
    "Defense thesis valid maar vehicle onder herbeoordeling.": "Defensiethesis is valide, maar ETF-implementatie staat onder herbeoordeling.",
    "Infrastructure capex remains valid.": "Infrastructuurcapex blijft valide.",
    "Hedge role must be proven.": "Hedgefunctie moet worden bewezen.",
    "Portfolio has zero non-U.S. exposure.": "De portefeuille heeft geen niet-Amerikaanse aandelenblootstelling.",
    "SPY: overlap review versus SMH remains active.": "SPY: overlapreview versus SMH blijft actief.",
    "PPA: direct duel versus ITA required.": "PPA: directe vervangingsanalyse tegenover ITA vereist.",
    "PAVE: direct duel versus GRID required.": "PAVE: directe vervangingsanalyse tegenover GRID vereist.",
    "GLD: hedge validity test required.": "GLD: hedge-validiteitstest vereist.",
    "Replacement challengers: not fundable without completed duel.": "Vervangingskandidaten: niet geschikt voor allocatie zonder afgeronde vervangingsanalyse.",
    "Replacement challengers: niet geschikt voor allocatie without completed duel.": "Vervangingskandidaten: niet geschikt voor allocatie zonder afgeronde vervangingsanalyse.",
    "Balanced growth with resilience bias": "gebalanceerde groei met nadruk op weerbaarheid",
    "UCITS only": "Alleen UCITS",
    "Leverage ETFs allowed": "Leveraged ETF’s toegestaan",
}

TABLE_SECTION_EXACT_MAPPINGS = {
    **TABLE_HEADER_MAPPINGS,
    **ENUM_VALUE_MAPPINGS,
    **SECTION_TITLE_MAPPINGS,
    **RADAR_PHRASE_MAPPINGS,
    **ACTION_DECISION_MAPPINGS,
    **VALUATION_HISTORY_MAPPINGS,
    **ANALYST_APPENDIX_MAPPINGS,
}

TABLE_SECTION_REGEX_MAPPINGS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bCurrent\s+status\b", re.I), "Huidige status"),
    (re.compile(r"\bCurrent\s+holding\b", re.I), "Huidige positie"),
    (re.compile(r"\bCurrent\s+exposure\b", re.I), "Huidige blootstelling"),
    (re.compile(r"\bWhy\s+it\s+matters\b", re.I), "Waarom dit relevant is"),
    (re.compile(r"\bWhat\s+needs\s+to\s+happen\b", re.I), "Benodigde bevestiging"),
    (re.compile(r"\bRequired\s+trigger\b", re.I), "Benodigde bevestiging"),
    (re.compile(r"\bTime\s+horizon\b", re.I), "Tijdshorizon"),
    (re.compile(r"\bOriginal\s+Thesis\b", re.I), "Oorspronkelijke thesis"),
    (re.compile(r"\bNew\s+weight\b", re.I), "Nieuw gewicht"),
    (re.compile(r"\bFunding\s+source\b", re.I), "Financieringsbron"),
    (re.compile(r"\bFunding\s+note\b", re.I), "Allocatietoelichting"),
    (re.compile(r"\bnot\s+fundable\b", re.I), "niet geschikt voor allocatie"),
    (re.compile(r"\bfundable\b", re.I), "geschikt voor allocatie"),
    (re.compile(r"\bfunding\b", re.I), "allocatie"),
    (re.compile(r"\bcompare\s+versus\s+([A-Z]{2,6})\s+next\s+run\b", re.I), r"volgende run vergelijken met \1"),
    (re.compile(r"\bunder\s+hedge-validity\s+review\b", re.I), "onder hedge-validiteitsreview"),
    (re.compile(r"\bnot\s+better\s+than\s+([A-Z]{2,6})\s+for\s+cash\s+this\s+run\b", re.I), r"deze run niet beter dan \1 voor cash"),
    (re.compile(r"\b([A-Z]{2,6})\s+remains\s+([a-z][^.]+)\."), r"\1 blijft \2."),
]

TABLE_SECTION_FORBIDDEN_AFTER_SCRUB = [
    "Theme",
    "Primary ETF",
    "Alternative ETF",
    "Why it matters",
    "What needs to happen",
    "Time horizon",
    "Current status",
    "Why not promoted",
    "What would change that",
    "Short theme",
    "Candidate ETF",
    "Short thesis",
    "Invalidation",
    "First-order effect",
    "Second-order effect",
    "Likely beneficiaries",
    "Likely losers",
    "ETF implication",
    "Original Thesis",
    "New weight",
    "Funding source",
    "Funding note",
    "not fundable",
    "fundable",
    "funding",
    "Notable lanes assessed",
    "not promoted this week",
    "Scored below the live radar cutoff",
    "No acceleration signal this week",
    "Momentum not decisive this week",
    "Structural case is credible",
    "Current holding still leads",
    "Alternative improving",
    "Needs positive 60d edge",
    "Needs sustained relative outperformance",
    "Inaugural model portfolio established",
    "Fresh per-ticker repricing",
    "Fresh six-of-six",
    "Fresh five-of-six",
    "Latest close basis",
    "carried forward",
    "Thesis changes",
    "Balanced growth with resilience bias",
]


def _replace_exact(text: str) -> str:
    for source, target in sorted(TABLE_SECTION_EXACT_MAPPINGS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    return text


def _replace_regex(text: str) -> str:
    for pattern, target in TABLE_SECTION_REGEX_MAPPINGS:
        text = pattern.sub(target, text)
    return text


def apply_table_section_mappings(text: str) -> str:
    """Apply centralized table/section mappings to Dutch report text."""
    text = _replace_exact(text)
    text = _replace_regex(text)
    return text
