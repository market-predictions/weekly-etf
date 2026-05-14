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
    "## 7A. ETF Position Performance": "## 7A. ETF-positieperformance",
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
    "ETF Position Performance": "ETF-positieperformance",
    "Performance is calculated on the current ETF holdings using the latest validated close-price audit and available market-history inputs.": "Performance wordt berekend op de huidige ETF-posities op basis van de meest recente gevalideerde slotkoers-audit en beschikbare markthistorie.",
    "Portfolio Action Snapshot": "Portefeuille-acties",
    "Replacement Duel Table v2": "Vervangingsanalyse",
    "Replacement Duel Table": "Vervangingsanalyse",
    "Investment Report": "Beleggersrapport",
    "Investor Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "Starting capital": "Startkapitaal",
    "Invested market value": "Belegde marktwaarde",
    "Total portfolio value": "Totale portefeuillewaarde",
    "Since inception return": "Rendement sinds start",
    "EUR/USD used": "EUR/USD gebruikt",
}

ACTION_PHRASES = {
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden but replaceable": "Aanhouden, maar vervangbaar",
    "Buy": "Kopen",
    "Add": "Toevoegen",
    "Hold": "Aanhouden",
    "Reduce": "Verlagen",
    "Close": "Sluiten",
    "Existing": "Bestaand",
    "New": "Nieuw",
    "Yes": "Ja",
    "No": "Nee",
    "None": "Geen",
}

CLIENT_LANGUAGE_CLEANUPS = {
    "output/etf_valuation_history.csv": "de waarderingshistorie",
    "output/": "",
    "1-3 months": "1-3 maanden",
    "3-12 months": "3-12 maanden",
    "Tier 1": "Niveau 1",
    "Tier 2": "Niveau 2",
    "Tier 3": "Niveau 3",
}

PARTIAL_MIXED_EXACT_CLEANUPS = {
    "Aanhouden but replaceable": "Aanhouden, maar vervangbaar",
    "Aanhouden maar replaceable": "Aanhouden, maar vervangbaar",
    "Hold maar vervangbaar": "Aanhouden, maar vervangbaar",
}


def is_native_dutch_report(text: str) -> bool:
    markers = [
        "# Wekelijkse ETF-review",
        "## 1. Kernsamenvatting",
        "## 2. Portefeuille-acties",
        "## 3. Regime-dashboard",
        "## 10. Review huidige posities",
        "## 15. Huidige posities en cash",
    ]
    return sum(marker in text for marker in markers) >= 5


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
    return text


def _clean_client_language(text: str) -> str:
    for src, dst in sorted(CLIENT_LANGUAGE_CLEANUPS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(src, dst)
    return text


def _normalize_ticker_lists(text: str) -> str:
    return re.sub(
        r"\b([A-Z]{2,6}(?:,\s*[A-Z]{2,6})+)\s+and\s+([A-Z]{2,6})\b",
        lambda match: f"{match.group(1)} en {match.group(2)}",
        text,
    )


def _normalize_partial_mixed_language(text: str) -> str:
    for src, dst in sorted(PARTIAL_MIXED_EXACT_CLEANUPS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(src, dst)
    text = _normalize_ticker_lists(text)
    text = re.sub(r"###\s*Aanhouden\s+maar\s+vervangbaar", "### Aanhouden, maar vervangbaar", text, flags=re.IGNORECASE)
    text = re.sub(r"###\s*Aanhouden\s+but\s+replaceable", "### Aanhouden, maar vervangbaar", text, flags=re.IGNORECASE)
    text = re.sub(r"###\s*Hold\s+but\s+replaceable", "### Aanhouden, maar vervangbaar", text, flags=re.IGNORECASE)
    return text


def _localize_until_stable(text: str, passes: int = 3) -> str:
    previous = text
    for _ in range(passes):
        current = localize_text(previous, language="nl")
        current = localize_markdown_table_headers(current, language="nl")
        current = _clean_runtime_artifacts(current)
        current = _clean_client_language(current)
        current = _normalize_partial_mixed_language(current)
        if current == previous:
            return current
        previous = current
    return previous


def localize_report(text: str) -> str:
    if is_native_dutch_report(text):
        # Native Dutch output is already rendered from Dutch templates. Keep this
        # module as a safety net only: do not run broad English-to-Dutch phrase
        # replacement over it, because that is exactly what created mixed-language
        # table sentences in earlier iterations.
        text = _replace_disclaimer(text)
        text = _clean_runtime_artifacts(text)
        text = _clean_client_language(text)
        return text

    text = _replace_disclaimer(text)
    text = _localize_section_titles(text)
    text = _localize_phrases(text)
    text = _localize_until_stable(text, passes=4)
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
    print(f"ETF_NL_LOCALIZATION_OK | report={report_path.name} | native_dutch={is_native_dutch_report(localized)}")


if __name__ == "__main__":
    main()
