from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from runtime.nl_table_section_mappings import apply_table_section_mappings, TABLE_SECTION_FORBIDDEN_AFTER_SCRUB

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

# Client-facing Dutch scrub layer.
#
# This file is deliberately broader than the strict language validator. The
# validator should fail bad Dutch output; this scrubber should first normalize
# known recurring English fragments that come from runtime state, tables,
# chart/history comments, lane artifacts and delivery templates. Keep official
# tickers, official product names and accepted market terms intact.

EXACT_REPLACEMENTS = {
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
    "Investment Report": "Beleggersrapport",
    "Investor Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "WEEKLY ETF REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Review": "Wekelijkse ETF-review",
    "WEEKLY ETF PRO REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Pro Review": "Wekelijkse ETF-review",
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
    "ETF-positieperformance": "Rendement huidige ETF-posities",
    "Performance wordt berekend": "Rendement wordt berekend",
    "SPDR Gold Aantal aandelen": "SPDR Gold Shares",
    "Vers kapitaal": "Nieuw kapitaal",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "Force alternative duel; upgrade, reduce, replace, or close": "Vervangingsanalyse vereist; verhoog, verlaag, vervang of sluit",
    "Run hedge validity test and compare with alternatives": "Voer een hedge-validiteitstest uit en vergelijk met alternatieven",
    "Nieuw weight": "Nieuw gewicht",
    "Aanhouden under hedge-validity review": "Aanhouden, onder hedge-validiteitsreview",
    "onder hedge-validity review": "onder hedge-validiteitsreview",
    "Toevoegened": "Toegevoegd",
    "Verlagend": "Verlaagd",
    "Sluitend": "Gesloten",
    "Neene unless explicit state says otherwise.": "Geen, tenzij de expliciete portefeuillestaat anders aangeeft.",
    "Neene": "Geen",
    "Section 14": "sectie 14",
}

REGEX_REPLACEMENTS = [
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
    text = apply_table_section_mappings(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    scrubbed = scrub_text(text)
    forbidden = FORBIDDEN_AFTER_SCRUB + TABLE_SECTION_FORBIDDEN_AFTER_SCRUB
    failures = [token for token in forbidden if token.lower() in scrubbed.lower()]
    if failures:
        raise RuntimeError("Dutch client-language scrub failed: " + ", ".join(sorted(set(failures))))
    report_path.write_text(scrubbed, encoding="utf-8")
    print(f"ETF_NL_CLIENT_LANGUAGE_SCRUB_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
