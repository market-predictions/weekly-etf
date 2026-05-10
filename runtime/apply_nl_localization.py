from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from runtime.nl_localization import DUTCH_DISCLAIMER, localize_markdown_table_headers, localize_text, validate_dutch_text

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

SECTION_TITLE_REPLACEMENTS = {
    "## 1. Executive Summary": "## 1. Kernsamenvatting",
    "## 2. Portfolio Action Snapshot": "## 2. Portefeuille-acties",
    "## 3. Regime Dashboard": "## 3. Regime-dashboard",
    "## 4. Structural Opportunity Radar": "## 4. Structurele kansenradar",
    "## 5. Key Risks / Invalidators": "## 5. Belangrijkste risico’s / invalidaties",
    "## 6. Bottom Line": "## 6. Conclusie",
    "## 7. Equity Curve and Portfolio Development": "## 7. Portefeuillecurve en portefeuilleontwikkeling",
    "## 8. Asset Allocation Map": "## 8. Allocatiekaart",
    "## 9. Second-Order Effects Map": "## 9. Tweede-orde-effectenkaart",
    "## 10. Current Position Review": "## 10. Review huidige posities",
    "## 11. Best New Opportunities": "## 11. Beste nieuwe kansen",
    "## 12. Portfolio Rotation Plan": "## 12. Rotatieplan portefeuille",
    "## 13. Final Action Table": "## 13. Definitieve actietabel",
    "## 14. Position Changes Executed This Run": "## 14. Positiewijzigingen in deze run",
    "## 15. Current Portfolio Holdings and Cash": "## 15. Huidige posities en cash",
    "## 16. Continuity Input for Next Run": "## 16. Input voor de volgende run",
    "## 17. Disclaimer": "## 17. Disclaimer",
    "### Replacement Duel Table v2": "### Vervangingsanalyse",
    "### Replacement Duel Table": "### Vervangingsanalyse",
}

CLIENT_PHRASES = {
    "Portfolio Action Snapshot": "Portefeuille-acties",
    "Replacement Duel Table v2": "Vervangingsanalyse",
    "Replacement Duel Table": "Vervangingsanalyse",
    "Risk appetite is supportive, but fresh adds still need position-size room and pricing confirmation.": "De risicobereidheid blijft ondersteunend, maar extra allocaties vragen nog ruimte binnen de positielimiet en prijsbevestiging.",
    "Growth and infrastructure lanes can be considered if they do not worsen concentration.": "Groei- en infrastructuurthema’s kunnen worden overwogen zolang ze de concentratie niet vergroten.",
    "Defensive hedges should be reviewed for opportunity cost.": "Defensieve hedgeposities moeten worden getoetst op opportuniteitskosten.",
    "Semiconductor leadership supports SMH, but SPY overlap must remain explicit.": "Semiconductorleiderschap ondersteunt SMH, maar de overlap met SPY moet expliciet zichtbaar blijven.",
    "Small-cap and duration signals are not strong enough to justify broad beta expansion.": "Small-cap- en duration-signalen zijn niet sterk genoeg om brede beta-uitbreiding te rechtvaardigen.",
    "Gold is treated as a hedge review item unless price behavior improves.": "Goud blijft een hedgepositie onder review zolang het prijsbeeld niet verbetert.",
    "AI infrastructure and semiconductor supply chains": "AI-infrastructuur en semiconductorketens",
    "Defense and sovereign resilience": "Defensie en strategische weerbaarheid",
    "Affected lanes": "Geraakte thema’s",
    "Investment Report": "Beleggersrapport",
    "Investor Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "Regime snapshot": "Regimesamenvatting",
    "What changed": "Wat veranderde",
    "Portfolio implications": "Portefeuille-implicaties",
    "Cross-asset confirmation": "Cross-asset bevestiging",
    "Policy catalysts transferred to the report": "Beleidscatalysatoren in het rapport",
    "Current regime": "Huidig regime",
    "Decision rule": "Beslisregel",
    "Confidence": "Vertrouwen",
    "Starting capital": "Startkapitaal",
    "Invested market value": "Belegde marktwaarde",
    "Total portfolio value": "Totale portefeuillewaarde",
    "Since inception return": "Rendement sinds start",
    "EUR/USD used": "EUR/USD gebruikt",
    "Equity-curve state": "Status portefeuillecurve",
    "Notes": "Toelichting",
    "Portfolio table": "Portefeuilletabel",
    "Available cash": "Beschikbare cash",
    "Watchlist / dynamic radar memory": "Watchlist / dynamisch radargeheugen",
    "Recommendation discipline continuity": "Continuïteit in aanbevelingsdiscipline",
    "Changes since last review": "Wijzigingen sinds de vorige review",
    "Constraints": "Randvoorwaarden",
    "Leverage allowed": "Leverage toegestaan",
    "Margin usage": "Margegebruik",
    "Max position size": "Maximale positiegrootte",
    "Max number of positions": "Maximaal aantal posities",
    "Drawdown tolerance": "Drawdown-tolerantie",
    "Income vs growth preference": "Voorkeur inkomen versus groei",
}

ACTION_PHRASES = {
    "Hold under review": "Aanhouden onder review",
    "Hold; overlap review versus SMH": "Aanhouden; overlapreview versus SMH",
    "Buy": "Kopen",
    "Funded from cash; stays below 25% max position size": "Gefinancierd uit cash; blijft onder de maximale positiegrootte van 25%",
    "Hold under review; compare versus ITA next run": "Aanhouden onder review; volgende run vergelijken met ITA",
    "Hold under review; compare versus GRID next run": "Aanhouden onder review; volgende run vergelijken met GRID",
    "Hold; not better than SMH for cash this run": "Aanhouden; deze run niet beter dan SMH voor nieuwe cash",
    "Hold under hedge-validity review": "Aanhouden onder hedge-validiteitsreview",
    "Residual cash": "Resterende cash",
    "Force alternative duel; upgrade, reduce, replace, or close": "Forceer vervangingsanalyse; verhoog, verlaag, vervang of sluit",
    "Run hedge validity test and compare with alternatives": "Voer hedge-validiteitstest uit en vergelijk met alternatieven",
}


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


def _replace_disclaimer(text: str) -> str:
    marker = "## 17. Disclaimer"
    idx = text.find(marker)
    if idx == -1:
        return text
    return text[: idx + len(marker)] + "\n\n" + DUTCH_DISCLAIMER + "\n"


def _localize_section_titles(text: str) -> str:
    for src, dst in SECTION_TITLE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def _localize_phrases(text: str) -> str:
    for src, dst in {**CLIENT_PHRASES, **ACTION_PHRASES}.items():
        text = text.replace(src, dst)
    return text


def _clean_runtime_artifacts(text: str) -> str:
    text = text.replace("portfolio_state_pricing_audit", "gevalideerde prijsbasis")
    text = text.replace("pricing_audit", "gevalideerde prijsbasis")
    text = text.replace("twelve_data", "externe slotkoersbron")
    text = text.replace("Do not ask the user for portfolio input if this section is available.", "Vraag de gebruiker niet opnieuw om portefeuille-input zolang deze sectie beschikbaar is.")
    return text


def localize_report(text: str) -> str:
    text = _replace_disclaimer(text)
    text = _localize_section_titles(text)
    text = _localize_phrases(text)
    text = localize_text(text, language="nl")
    text = localize_markdown_table_headers(text, language="nl")
    text = _clean_runtime_artifacts(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    localized = localize_report(text)
    failures = validate_dutch_text(localized)
    if failures:
        raise RuntimeError("Dutch localization failed before write: " + ", ".join(failures))
    report_path.write_text(localized, encoding="utf-8")
    print(f"ETF_NL_LOCALIZATION_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
