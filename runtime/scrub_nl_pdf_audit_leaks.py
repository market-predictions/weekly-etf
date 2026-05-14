from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

# Final Dutch PDF-audit cleanup pass.
#
# The earlier localization layers translate known report structures and tables.
# This pass catches residual client-visible English fragments that the PDF audit
# found in rendered Dutch reports. It is intentionally broader and phrase based:
# if these fragments appear, the Dutch report is not premium-client ready.

EXACT_REPLACEMENTS = {
    "Core U.S. large-cap exposure": "Amerikaanse large-cap kernblootstelling",
    "Core US large-cap exposure": "Amerikaanse large-cap kernblootstelling",
    "Cyber spend": "cybersecurity-uitgaven",
    "Direct replacement duel": "directe vervangingsanalyse",
    "Grid buildout": "netuitbreiding",
    "Growth engine": "groeimotor",
    "Hedge ballast": "hedgepositie",
    "Investable maar": "Belegbaar, maar",
    "Investable but": "Belegbaar, maar",
    "Needs supply-chain": "Vereist steun vanuit de toeleveringsketen",
    "Needs supply-chain policy plus price momentum.": "Vereist steun vanuit toeleveringsketenbeleid en koersmomentum.",
    "SMH remains": "SMH blijft",
    "Useful only if": "Alleen nuttig als",
    "Volglijst only": "Alleen volglijst",
    "Watchlist only": "Alleen volglijst",
    "Zero allocation": "Nulallocatie",
    "Zero allocation is an explicit U.S. exceptionalism bet.": "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht.",
    "Investable maar concentration risk is explicit.": "Belegbaar, maar concentratierisico is expliciet aanwezig.",
    "Volglijst only; non-U.S. exposure remains a diversification gap.": "Alleen volglijst; niet-Amerikaanse blootstelling blijft een diversificatiekloof.",
    "SMH remains the cleanest growth expression": "SMH blijft de zuiverste groeiblootstelling",
    "Useful only if commodity breadth confirms.": "Alleen nuttig als de breedte in grondstoffen bevestigt.",
    "Useful only if commodity stress becomes visible.": "Alleen nuttig als grondstoffenstress zichtbaar wordt.",
    "Direct replacement duel versus SMH": "Directe vervangingsanalyse tegenover SMH",
    "Direct replacement duel versus ITA": "Directe vervangingsanalyse tegenover ITA",
    "Direct replacement duel versus GRID": "Directe vervangingsanalyse tegenover GRID",
}

REGEX_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bCore\s+U\.?S\.?\s+large-cap\s+exposure\b", re.I), "Amerikaanse large-cap kernblootstelling"),
    (re.compile(r"\bCyber\s+spend\b", re.I), "cybersecurity-uitgaven"),
    (re.compile(r"\bDirect\s+replacement\s+duel\b", re.I), "directe vervangingsanalyse"),
    (re.compile(r"\bGrid\s+buildout\b", re.I), "netuitbreiding"),
    (re.compile(r"\bGrowth\s+engine\b", re.I), "groeimotor"),
    (re.compile(r"\bHedge\s+ballast\b", re.I), "hedgepositie"),
    (re.compile(r"\bInvestable\s+(?:maar|but)\b", re.I), "Belegbaar, maar"),
    (re.compile(r"\bNeeds\s+supply-chain\b", re.I), "Vereist steun vanuit de toeleveringsketen"),
    (re.compile(r"\b([A-Z]{2,6})\s+remains\b", re.I), r"\1 blijft"),
    (re.compile(r"\bUseful\s+only\s+if\b", re.I), "Alleen nuttig als"),
    (re.compile(r"\b(?:Volglijst|Watchlist)\s+only\b", re.I), "Alleen volglijst"),
    (re.compile(r"\bZero\s+allocation\b", re.I), "Nulallocatie"),
]

FORBIDDEN_AFTER_SCRUB = [
    "Core U.S. large-cap exposure",
    "Core US large-cap exposure",
    "Cyber spend",
    "Direct replacement duel",
    "Grid buildout",
    "Growth engine",
    "Hedge ballast",
    "Investable maar",
    "Investable but",
    "Needs supply-chain",
    "SMH remains",
    "Useful only if",
    "Volglijst only",
    "Watchlist only",
    "Zero allocation",
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
    previous = text
    for _ in range(3):
        current = previous
        for source, target in sorted(EXACT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
            current = current.replace(source, target)
        for pattern, target in REGEX_REPLACEMENTS:
            current = pattern.sub(target, current)
        if current == previous:
            return current
        previous = current
    return previous


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    scrubbed = scrub_text(text)
    failures = [token for token in FORBIDDEN_AFTER_SCRUB if token.lower() in scrubbed.lower()]
    if failures:
        raise RuntimeError("Dutch PDF-audit scrub failed: " + ", ".join(sorted(set(failures))))
    report_path.write_text(scrubbed, encoding="utf-8")
    print(f"ETF_NL_PDF_AUDIT_SCRUB_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
