from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

# Client-facing Dutch scrub layer.
#
# This file is deliberately broader than the strict language validator. The
# validator should fail bad Dutch output; this scrubber should first normalize
# known recurring English fragments that come from runtime state, tables,
# chart/history comments, lane artifacts and delivery templates. Keep official
# tickers, official product names and accepted market terms intact.

EXACT_REPLACEMENTS = {
    # Cover / executive cards / general headings
    "Wednesday, 13 May 2026": "Woensdag 13 mei 2026",
    "PRIMARY REGIME": "PRIMAIR REGIME",
    "Primary regime": "Primair regime",
    "GEOPOLITICAL REGIME": "GEOPOLITIEK REGIME",
    "Geopolitical regime": "Geopolitiek regime",
    "MAIN TAKEAWAY": "KERNCONCLUSIE",
    "Main takeaway": "Kernconclusie",
    "Risk-on smal marktleiderschap\n(72% confidence)": "Risk-on met smal marktleiderschap\n(72% vertrouwen)",
    "(72% confidence)": "(72% vertrouwen)",
    "Mixed / not yet decisive": "Gemengd / nog niet doorslaggevend",
    "Keep the current allocation\ndisciplined.": "Houd de huidige allocatie\ngedisciplineerd.",
    "Keep the current allocation disciplined.": "Houd de huidige allocatie gedisciplineerd.",
    "WAT VERANDERDE THIS WEEK": "WAT VERANDERDE DEZE WEEK",
    "WAT VERANDERDE THIS WEEK": "WAT VERANDERDE DEZE WEEK",
    "Investment Report": "Beleggersrapport",
    "Investor Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "WEEKLY ETF REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Review": "Wekelijkse ETF-review",
    "WEEKLY ETF PRO REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Pro Review": "Wekelijkse ETF-review",

    # Core executive wording
    "new allocation vraagt": "nieuwe allocaties vragen",
    "macrosteun": "steun vanuit het macrobeeld",
    "Best verdiende exposure": "Best onderbouwde blootstelling",
    "Actiebias": "Beslissingsrichting",
    "Status portefeuillecurve: Aangesloten op sectie 15 with full valuation history": "Status portefeuillecurve: aangesloten op sectie 15 met volledige waarderingshistorie",
    "with full valuation history": "met volledige waarderingshistorie",
    "GLD remains a hedge review, not an unquestioned ballast position.": "GLD blijft een hedgepositie onder herbeoordeling en is geen vanzelfsprekende stabilisator.",
    "PPA en PAVE remain replaceable until their ETF implementation quality is proven.": "PPA en PAVE blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.",
    "Neen-U.S. equity exposure remains a diversification gap.": "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.",
    "Neen-U.S.": "Niet-Amerikaanse",
    "Non-U.S.": "Niet-Amerikaanse",
    "non-U.S.": "niet-Amerikaanse",

    # Section 4 / opportunity radar
    "AI compute infrastructure": "AI-rekenkrachtinfrastructuur",
    "Cybersecurity resilience": "Cybersecurityweerbaarheid",
    "Grid buildout / electrification": "Netuitbreiding / elektrificatie",
    "Broad commodity inflation hedge": "Brede grondstoffen-inflatiehedge",
    "Agricultural commodities": "Agrarische grondstoffen",
    "Critical minerals / copper / refining": "Kritieke mineralen / koper / raffinage",
    "Food security / agriculture inputs": "Voedselzekerheid / landbouwinputs",
    "Water infrastructure / treatment": "Waterinfrastructuur / waterbehandeling",
    "Semiconductor and AI capex remains the cleanest funded structural growth lane.": "Semiconductors en AI-capex blijven het zuiverste gefinancierde structurele groeithema.",
    "Macro filter: Regime and price leadership still support AI compute exposure, maar concentration discipline applies.": "Macrofilter: regime en koersleiderschap ondersteunen AI-rekenkrachtblootstelling nog steeds, maar concentratiediscipline blijft nodig.",
    "AI infrastructure leadership remains persistent, maar position-size discipline matters.": "Leiderschap in AI-infrastructuur blijft aanhouden, maar positiegrootte-discipline blijft belangrijk.",
    "Cyber spend is linked to AI, cloud, data-center and geopolitical resilience.": "Cybersecurity-uitgaven hangen samen met AI, cloud, datacenters en geopolitieke weerbaarheid.",
    "Offers digital-infrastructure exposure with less direct semiconductor cyclicality.": "Biedt blootstelling aan digitale infrastructuur met minder directe semiconductorcycliciteit.",
    "Power demand, grid bottlenecks and reshoring capex support infrastructure spend.": "Stroomvraag, netcongestie en reshoring-capex ondersteunen infrastructuuruitgaven.",
    "Macro filter: AI power demand and infrastructure policy support the grid lane; allocatie still depends on PAVE-vs-GRID duel evidence.": "Macrofilter: AI-stroomvraag en infrastructuurbeleid ondersteunen het netthema; allocatie blijft afhankelijk van de PAVE-versus-GRID-vervangingsanalyse.",
    "PAVE remains useful, maar GRID is the cleaner thematic challenger.": "PAVE blijft nuttig, maar GRID is het zuiverdere thematische alternatief.",
    "Broad commodities may hedge inflation better than single-metal or single-gold exposure.": "Brede grondstoffen kunnen inflatie beter afdekken dan blootstelling aan één metaal of alleen goud.",
    "Useful only if commodity breadth confirms.": "Alleen nuttig als de breedte in grondstoffen bevestigt.",
    "Direct crop exposure can hedge food inflation differently than agribusiness equities.": "Directe blootstelling aan landbouwgewassen kan voedselinflatie anders afdekken dan agribusiness-aandelen.",
    "Useful only if commodity stress becomes visible.": "Alleen nuttig als grondstoffenstress zichtbaar wordt.",
    "Critical mineral supply chains matter for electrification, defense and grid capex.": "Toeleveringsketens voor kritieke mineralen zijn relevant voor elektrificatie, defensie en netwerkinvesteringen.",
    "Needs supply-chain policy plus price momentum.": "Vereist steun vanuit toeleveringsketenbeleid en koersmomentum.",
    "Neetable lanes assessed maar not promoted this week": "Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd",
    "Notable lanes assessed maar not promoted this week": "Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd",
    "Notable lanes assessed but not promoted this week": "Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd",
    "Neetable lanes assessed": "Opvallende thema’s beoordeeld",
    "not promoted this week": "deze week niet gepromoveerd",
    "Industrial automation and factory software": "Industriële automatisering en fabriekssoftware",
    "Robotics / automation": "Robotica / automatisering",
    "Copper and electrification materials": "Koper en elektrificatiematerialen",
    "Biotech innovation / therapeutic platforms": "Biotechinnovatie / therapeutische platforms",
    "Nuclear utilities and clean baseload": "Nucleaire nutsbedrijven en schone basislast",
    "Structural case is credible, maar timing confirmation still trails higher-ranked lanes.": "De structurele case is geloofwaardig, maar timingbevestiging blijft achter bij hoger gerangschikte thema’s.",
    "Direct replacement duel versus SMH": "Directe vervangingsanalyse tegenover SMH",
    "Needs clearer industrial order momentum.": "Vereist duidelijker momentum in industriële orders.",
    "Needs industrial capex breadth and ETF momentum.": "Vereist bredere industriële capex en ETF-momentum.",
    "Neet promoted because it still trails SPY on 3-month relative strength.": "Niet gepromoveerd omdat de 3-maands relatieve sterkte nog achterblijft bij SPY.",
    "Can become attractive if breadth improves and rates ease.": "Kan aantrekkelijk worden als de breedte verbetert en de rente ontspant.",
    "Can diversify URNM if fuel-cycle volatility is too high.": "Kan URNM diversifiëren als volatiliteit in de brandstofcyclus te hoog blijft.",
    "Becomes more geschikt voor allocatie if copper momentum and China demand confirm.": "Wordt geschikter voor allocatie als kopermomentum en Chinese vraag bevestigen.",

    # Short radar / risks
    "Rate-sensitive small caps": "Rentegevoelige small-caps",
    "China platform beta": "Chinese platformbeta",
    "Long-duration bonds": "Langlopende obligaties",
    "Speculative clean-tech beta": "Speculatieve cleantechbeta",
    "Restrictive real rates pressure weaker balance sheets.": "Restrictieve reële rentes zetten zwakkere balansen onder druk.",
    "IWM breaks down versus SPY while yields firm.": "IWM breekt neerwaarts uit tegenover SPY terwijl rentes stevig blijven.",
    "Clear easing impulse and better credit breadth.": "Duidelijke verruimingsimpuls en betere kredietbreedte.",
    "Policy confidence remains fragile.": "Beleidsvertrouwen blijft kwetsbaar.",
    "Failed rally or renewed FX/policy stress.": "Mislukte rally of hernieuwde valuta-/beleidsstress.",
    "Durable stimulus and earnings recovery.": "Duurzame stimulans en winstherstel.",
    "Sticky inflation and real-rate risk remain headwinds.": "Hardnekkige inflatie en reëlerenterisico blijven tegenwind.",
    "Real yields rise again.": "Reële rentes stijgen opnieuw.",
    "Growth scare and decisive lower-yield breakout.": "Groeischrik en beslissende neerwaartse rente-uitbraak.",
    "Financing pressure and weak profitability remain issues.": "Financieringsdruk en zwakke winstgevendheid blijven knelpunten.",
    "Failure to recover in broad risk-on tape.": "Geen herstel in een brede risk-on-markt.",
    "Sharp rate relief or major policy surprise.": "Scherpe rentedaling of grote beleidsverrassing.",
    "SPY plus SMH creates high U.S. tech / AI factor overlap.": "SPY plus SMH creëert hoge Amerikaanse tech-/AI-factoroverlap.",
    "GLD remains": "GLD blijft",
    "remain replaceable": "blijven vervangbaar",

    # Performance and roles
    "ETF-positieperformance": "Rendement huidige ETF-posities",
    "Performance wordt berekend": "Rendement wordt berekend",
    "Core U.S. large-cap exposure": "Amerikaanse large-cap kernblootstelling",
    "AI compute / semiconductor leadership": "AI-rekenkracht / semiconductorleiderschap",
    "Defense and sovereign resilience": "Defensie en strategische weerbaarheid",
    "Grid and infrastructure capex": "Netwerk- en infrastructuurcapex",
    "Nuclear and uranium cycle exposure": "Kernenergie- en uraniumcyclus",
    "Hard-asset geopolitical and inflation hedge": "Reële activa / geopolitieke en inflatiehedge",
    "Core beta": "Kernbeta",
    "Growth engine": "Groeimotor",
    "Resilience": "Weerbaarheid",
    "Real-asset capex": "Reële activa / capex",
    "Strategic energy": "Strategische energie",
    "Hedge ballast": "Hedgepositie",
    "SPDR Gold Aantal aandelen": "SPDR Gold Shares",

    # Allocation map
    "US equities": "Amerikaanse aandelen",
    "Europe equities": "Europese aandelen",
    "EM equities": "Opkomende markten",
    "large cap": "Large-cap",
    "small cap": "Small-cap",
    "growth": "Groei",
    "quality": "Kwaliteit",
    "gold": "Goud",
    "industrials / defense": "Industrie / defensie",
    "non-USD assets": "Niet-USD activa",
    "Investable maar concentration risk is explicit.": "Belegbaar, maar concentratierisico is expliciet aanwezig.",
    "Volglijst only; non-U.S. exposure remains a diversification gap.": "Alleen volglijst; niet-Amerikaanse blootstelling blijft een diversificatiekloof.",
    "USD and oil sensitivity remain headwinds.": "USD- en oliegevoeligheid blijven tegenwind.",
    "Quality leadership still works.": "Kwaliteitsleiderschap werkt nog steeds.",
    "Rates and refinancing remain difficult.": "Rentes en herfinanciering blijven lastig.",
    "Selective growth led by SMH remains attractive.": "Selectieve groei onder leiding van SMH blijft aantrekkelijk.",
    "Earnings durability remains valuable.": "Winstbestendigheid blijft waardevol.",
    "Hedge role onder herbeoordeling.": "Hedgerol onder herbeoordeling.",
    "Structural thesis valid; vehicle onder herbeoordeling.": "Structurele thesis is valide; ETF-implementatie onder herbeoordeling.",
    "Zero allocation is an explicit U.S. exceptionalism bet.": "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht.",

    # Second-order effects
    "AI leadership": "AI-leiderschap",
    "Factor concentration": "Factorconcentratie",
    "Defense thesis vs ETF implementation": "Defensiethesis versus ETF-implementatie",
    "Hedge drawdown": "Hedgedrawdown",
    "SMH remains the cleanest growth expression": "SMH blijft de zuiverste groeiblootstelling",
    "Concentration must be watched": "Concentratie moet worden bewaakt",
    "SPY and SMH overlap": "SPY en SMH overlappen",
    "Portfolio is less diversified than ticker count suggests": "De portefeuille is minder gediversifieerd dan het aantal tickers suggereert",
    "Defense remains structurally valid": "Defensie blijft structureel valide",
    "PPA must justify itself versus ITA": "PPA moet zich bewijzen tegenover ITA",
    "GLD hedge role must be proven": "GLD moet zijn hedgefunctie bewijzen",
    "GSG/BIL remain challengers": "GSG/BIL blijven alternatieven",
    "Lower-quality cyclicals": "Cyclische waarden van lagere kwaliteit",
    "Overlapping U.S. beta": "Overlappende Amerikaanse beta",
    "Weak vehicle selection": "Zwakke ETF-selectie",
    "Unproductive hedge": "Onproductieve hedgepositie",
    "Aanhouden near max size": "Aanhouden rond maximale positiegrootte",

    # Current position review and action tables
    "Vers kapitaal": "Nieuw kapitaal",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "Force alternative duel; upgrade, reduce, replace, or close": "Vervangingsanalyse vereist; verhoog, verlaag, vervang of sluit",
    "Run hedge validity test and compare with alternatives": "Voer een hedge-validiteitstest uit en vergelijk met alternatieven",
    "SMH remains the leading funded growth exposure, subject to the max-position rule.": "SMH blijft de leidende gefinancierde groeiblootstelling, binnen de maximale positiegrootte.",
    "CIBR / BUG: Cyber spend is linked to AI, cloud, data-center and geopolitical resilience.": "CIBR / BUG: cybersecurity-uitgaven hangen samen met AI, cloud, datacenters en geopolitieke weerbaarheid.",
    "GSG / DBC: Broad commodities may hedge inflation better than single-metal or single-gold exposure.": "GSG / DBC: brede grondstoffen kunnen inflatie beter afdekken dan blootstelling aan één metaal of alleen goud.",
    "DBA / CORN: Direct crop exposure can hedge food inflation differently than agribusiness equities.": "DBA / CORN: directe blootstelling aan landbouwgewassen kan voedselinflatie anders afdekken dan agribusiness-aandelen.",
    "Growth engine": "Groeimotor",
    "Strategic energy": "Strategische energie",
    "Hedge ballast": "Hedgepositie",
    "None": "Geen",
    "Neene": "Geen",
    "Nieuw weight": "Nieuw gewicht",
    "compare versus ITA next run": "volgende run vergelijken met ITA",
    "compare versus GRID next run": "volgende run vergelijken met GRID",
    "not better than SMH for cash this run": "deze run niet beter dan SMH voor cash",
    "Aanhouden under hedge-validity review": "Aanhouden, onder hedge-validiteitsreview",
    "onder hedge-validity review": "onder hedge-validiteitsreview",

    # Section 7 history / notes
    "Inaugural model portfolio established": "Initiële modelportefeuille vastgesteld",
    "Fresh per-ticker repricing using latest completed close set": "Verse herprijzing per ticker op basis van de meest recente volledige slotkoersset",
    "Fresh six-of-six repricing using completed 20 April close set": "Verse herprijzing voor zes van zes posities op basis van de volledige slotkoersset van 20 april",
    "Fresh five-of-six repricing; PPA carried forward": "Verse herprijzing voor vijf van zes posities; PPA doorgeschoven",
    "Fresh six-of-six repricing using persisted 2026-04-29 audit": "Verse herprijzing voor zes van zes posities op basis van de vastgelegde audit van 2026-04-29",
    "Fresh five-of-six pricing recovery; GLD carried forward": "Prijsherstel voor vijf van zes posities; GLD doorgeschoven",
    "Latest 4 May close basis; +8 SMH executed from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH uitgevoerd vanuit cash",
    "pricing-audit": "prijsaudit",

    # Continuity section
    "Long": "Long",
    "Original Thesis": "Oorspronkelijke thesis",
    "Richting": "Richting",
    "Oorspronkelijke thesis": "Oorspronkelijke thesis",
    "Strongest secular growth exposure.": "Sterkste structurele groeiblootstelling.",
    "Defense thesis valid maar vehicle onder herbeoordeling.": "Defensiethesis is valide, maar ETF-implementatie staat onder herbeoordeling.",
    "Infrastructure capex remains valid.": "Infrastructuurcapex blijft valide.",
    "Hedge role must be proven.": "Hedgefunctie moet worden bewezen.",
    "Portfolio has zero non-U.S. exposure.": "De portefeuille heeft geen niet-Amerikaanse aandelenblootstelling.",
    "SPY: overlap review versus SMH remains active.": "SPY: overlapreview versus SMH blijft actief.",
    "PPA: direct duel versus ITA required.": "PPA: directe vervangingsanalyse tegenover ITA vereist.",
    "PAVE: direct duel versus GRID required.": "PAVE: directe vervangingsanalyse tegenover GRID vereist.",
    "GLD: hedge validity test required.": "GLD: hedge-validiteitstest vereist.",
    "Replacement challengers: niet geschikt voor allocatie without completed duel.": "Vervangingskandidaten: niet geschikt voor allocatie zonder afgeronde vervangingsanalyse.",
    "UCITS only": "Alleen UCITS",
    "Leverage ETFs allowed": "Leveraged ETF’s toegestaan",
    "Drawdown-tolerantie: Moderate": "Drawdown-tolerantie: Gemiddeld",
    "Voorkeur inkomen versus groei: Balanced growth with resilience bias": "Voorkeur inkomen versus groei: gebalanceerde groei met nadruk op weerbaarheid",
    "Toevoegened": "Toegevoegd",
    "Verlagend": "Verlaagd",
    "Sluitend": "Gesloten",
    "Neene unless explicit state says otherwise.": "Geen, tenzij de expliciete portefeuillestaat anders aangeeft.",
    "Thesis changes": "Thesiswijzigingen",
    "Section 14": "sectie 14",
}

REGEX_REPLACEMENTS = [
    # Generic Dutch date rendering in delivery markdown/html text if present.
    (re.compile(r"\bMonday,\s+(\d{1,2})\s+May\s+2026\b"), r"Maandag \1 mei 2026"),
    (re.compile(r"\bTuesday,\s+(\d{1,2})\s+May\s+2026\b"), r"Dinsdag \1 mei 2026"),
    (re.compile(r"\bWednesday,\s+(\d{1,2})\s+May\s+2026\b"), r"Woensdag \1 mei 2026"),
    (re.compile(r"\bThursday,\s+(\d{1,2})\s+May\s+2026\b"), r"Donderdag \1 mei 2026"),
    (re.compile(r"\bFriday,\s+(\d{1,2})\s+May\s+2026\b"), r"Vrijdag \1 mei 2026"),
    (re.compile(r"\bSaturday,\s+(\d{1,2})\s+May\s+2026\b"), r"Zaterdag \1 mei 2026"),
    (re.compile(r"\bSunday,\s+(\d{1,2})\s+May\s+2026\b"), r"Zondag \1 mei 2026"),
    (re.compile(r"\bnot\s+fundable\b", re.I), "niet geschikt voor allocatie"),
    (re.compile(r"\bfunding\s+source\b", re.I), "financieringsbron"),
    (re.compile(r"\bfunding\s+note\b", re.I), "allocatietoelichting"),
    (re.compile(r"\bfunding\s+candidates\b", re.I), "allocatiekandidaten"),
    (re.compile(r"\bfunding\s+challengers\b", re.I), "allocatie naar alternatieven"),
    (re.compile(r"\bbefore\s+funding\b", re.I), "vóór allocatie"),
    (re.compile(r"\bafter\s+funding\b", re.I), "na allocatie"),
    (re.compile(r"\bfundable\b", re.I), "geschikt voor allocatie"),
    (re.compile(r"\bfunding\b", re.I), "allocatie"),
    (re.compile(r"\bbut\s+treat\b", re.I), "maar behandel"),
    (re.compile(r"\bbut\b", re.I), "maar"),
    (re.compile(r"\bas\s+(posities|positie|thema’s|themas|kandidaten|alternatieven)\b", re.I), r"als \1"),
    (re.compile(r"\band\s+(GLD|PAVE|PPA|SPY|SMH|URNM|cash|koersbevestiging|vervangingsbeslissingen)\b", re.I), r"en \1"),
    (re.compile(r"\b([A-Z]{2,6}(?:,\s*[A-Z]{2,6})+)\s+and\s+([A-Z]{2,6})\b"), lambda match: f"{match.group(1)} en {match.group(2)}"),
    (re.compile(r"\bNe+ne\b", re.I), "Geen"),
    (re.compile(r"\bNone\b"), "Geen"),
    (re.compile(r"\bHold\b"), "Aanhouden"),
    (re.compile(r"\bAdd\b"), "Toevoegen"),
    (re.compile(r"\bReduce\b"), "Verlagen"),
    (re.compile(r"\bClose\b"), "Sluiten"),
    (re.compile(r"\bExisting\b"), "Bestaand"),
    (re.compile(r"\bYes\b"), "Ja"),
    (re.compile(r"\bNo\b"), "Nee"),
    (re.compile(r"###\s*Aanhouden\s+(?:but|maar)\s+replaceable", re.I), "### Aanhouden, maar vervangbaar"),
    (re.compile(r"###\s*Hold\s+but\s+replaceable", re.I), "### Aanhouden, maar vervangbaar"),
]

FORBIDDEN_AFTER_SCRUB = [
    "fundable",
    "funding",
    "Aanhouden but replaceable",
    "passive holds",
    "active review items",
    "but treat",
    "PRIMARY REGIME",
    "GEOPOLITICAL REGIME",
    "MAIN TAKEAWAY",
    "confidence",
    "Mixed / not yet decisive",
    "Keep the current allocation",
    "THIS WEEK",
    "Capital spending",
    "AI compute infrastructure",
    "Neetable",
    "not promoted this week",
    "SPY plus SMH creates",
    "GLD remains",
    "Neen-U.S.",
    "Best verdiende",
    "Actiebias",
    "with full valuation history",
    "Inaugural model portfolio established",
    "Fresh per-ticker",
    "Equity Curve (EUR)",
    "Portfolio value (EUR)",
    "US equities",
    "Investment Report",
    "Investor Report",
    "Analyst Report",
]


def latest_nl_report(output_dir: Path) -> Path:
    explicit = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and NL_RE.match(path.name):
            return path
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro_nl_*.md") if NL_RE.match(path.name))
    if not reports:
        raise RuntimeError(f"No Dutch ETF pro report found in {output_dir}")
    return reports[-1]


def scrub_text(text: str) -> str:
    for source, target in sorted(EXACT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    for pattern, target in REGEX_REPLACEMENTS:
        text = pattern.sub(target, text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    scrubbed = scrub_text(text)
    failures = [token for token in FORBIDDEN_AFTER_SCRUB if token.lower() in scrubbed.lower()]
    if failures:
        raise RuntimeError("Dutch client-language scrub failed: " + ", ".join(sorted(set(failures))))
    report_path.write_text(scrubbed, encoding="utf-8")
    print(f"ETF_NL_CLIENT_LANGUAGE_SCRUB_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
