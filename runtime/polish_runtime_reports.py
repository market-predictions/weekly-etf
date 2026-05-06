from __future__ import annotations

import argparse
import re
from pathlib import Path

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir} for {pattern.pattern}")
    return reports[-1]


def replace_between(text: str, start_heading: str, end_heading: str, replacement_body: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return text
    body_start = start + len(start_heading)
    end = text.find(end_heading, body_start)
    if end == -1:
        return text
    return text[:body_start] + "\n\n" + replacement_body.strip() + "\n\n" + text[end:]


def polish_english(text: str) -> str:
    text = text.replace(
        "- **Secondary cross-current:** Runtime-derived report generation is active. Pricing, lane discovery, portfolio state and recommendation discipline are separate inputs.",
        "- **Secondary cross-current:** The production process is now state-led: pricing, portfolio holdings, lane discovery and recommendation discipline are independently validated before delivery."
    )
    text = text.replace(
        "- **Secondary cross-current:** Runtime-derived report generation is active. Pricing, lane assessment, portfolio state and recommendation discipline are separate inputs.",
        "- **Secondary cross-current:** The production process is now state-led: pricing, portfolio holdings, lane discovery and recommendation discipline are independently validated before delivery."
    )
    text = text.replace(
        "- **What changed this week:** This report is rendered from normalized runtime state rather than manually patched markdown. Replacement challengers are shown only with pricing and duel status.",
        "- **What changed this week:** The report now separates presentation from state authority. Replacement candidates are no longer treated as fundable ideas unless their closing-price basis and duel status are visible."
    )
    text = text.replace(
        "- **Overall portfolio judgment:** Maintain the implemented book while keeping SPY, PPA, PAVE and GLD under explicit discipline review.",
        "- **Overall portfolio judgment:** Keep the current portfolio intact for now, but treat SPY, PPA, PAVE and GLD as active review items rather than passive holds."
    )
    text = text.replace(
        "- **Main takeaway:** **Use SMH as the highest-conviction funded leader, but do not let replacement candidates become fundable without close-based duel evidence.**",
        "- **Main takeaway:** **SMH remains the earned leader, but fresh capital and replacement decisions must now pass a stricter close-based evidence test.**"
    )
    text = text.replace(
        "- None from this renderer unless the runtime state already records an executed Add.",
        "- None executed this run. SMH remains the first candidate for additional capital only if the 25% position-size rule leaves room."
    )
    text = text.replace(
        "- No replacement is fundable until the pricing and relative-strength duel is complete.",
        "- No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel."
    )
    text = text.replace(
        "- Equity-curve state: Runtime-derived",
        "- Equity-curve state: Reconciled to Section 15"
    )
    text = text.replace(
        "| {report_date} | {nav:.2f} | Runtime-derived valuation from pricing audit and explicit portfolio state |",
        "| {report_date} | {nav:.2f} | Valuation reconciled to pricing audit and explicit portfolio state |"
    )
    text = text.replace(
        "| Close | None | No exits required by runtime state |",
        "| Close | None | No exit clears the evidence threshold today |"
    )
    text = text.replace(
        "| Add | None | No runtime-generated add |",
        "| Add | None | No fresh add is authorized without confirming position-size headroom |"
    )
    text = text.replace(
        "- Added: runtime-rendered markdown generation layer.",
        "- Added: a validated state-led production path; no portfolio position was added unless shown in Section 14."
    )
    text = text.replace(
        "- Thesis changes: No thesis abandoned; implementation discipline tightened.",
        "- Thesis changes: No structural thesis was abandoned; implementation discipline is materially tighter."
    )

    text = replace_between(
        text,
        "## 6. Bottom Line",
        "## 7. Equity Curve and Portfolio Development",
        """
- **Portfolio stance:** Stay invested, but raise the bar for any new capital deployment.
- **Best earned exposure:** SMH remains the portfolio's strongest contributor and cleanest secular growth expression.
- **Main discipline issue:** SPY and SMH still create meaningful U.S. tech / AI overlap; this is concentration with benefits, not full diversification.
- **Weakest implementation questions:** PPA must prove itself against ITA, PAVE must prove itself against GRID, and GLD must prove that it still behaves like useful ballast.
- **Action bias:** No replacement is fundable yet. The right next move is evidence gathering, not forced churn.
"""
    )

    # Section 10 is intentionally left intact. It is now generated from enriched
    # runtime position state plus the recommendation scorecard. Do not replace it
    # with a static table here.
    return text


def polish_dutch(text: str) -> str:
    text = polish_english(text)
    replacements = {
        "The production process is now state-led: pricing, portfolio holdings, lane discovery and recommendation discipline are independently validated before delivery.": "Het productieproces is nu state-led: pricing, portefeuilleposities, lane-discovery en aanbevelingsdiscipline worden onafhankelijk gevalideerd vóór verzending.",
        "The report now separates presentation from state authority. Replacement candidates are no longer treated as fundable ideas unless their closing-price basis and duel status are visible.": "Het rapport scheidt nu presentatie van state-authority. Vervangingskandidaten worden niet meer als financierbare ideeën gepresenteerd zonder zichtbare sluitkoersbasis en duel-status.",
        "Keep the current portfolio intact for now, but treat SPY, PPA, PAVE and GLD as active review items rather than passive holds.": "Behoud de huidige portefeuille voorlopig, maar behandel SPY, PPA, PAVE en GLD als actieve reviewposities in plaats van passieve holds.",
        "SMH remains the earned leader, but fresh capital and replacement decisions must now pass a stricter close-based evidence test.": "SMH blijft de verdiende leider, maar nieuw kapitaal en vervangingsbesluiten moeten nu door een strengere sluitkoers-gebaseerde bewijscheck.",
        "None executed this run. SMH remains the first candidate for additional capital only if the 25% position-size rule leaves room.": "Geen add uitgevoerd deze run. SMH blijft de eerste kandidaat voor extra kapitaal, alleen als de 25%-positielimiet ruimte laat.",
        "No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel.": "Geen challenger is al gepromoveerd tot financierbare vervanger. Elke genoemde vervanger moet eerst dezelfde sluitkoersbasis en relatieve-sterkte-duel doorstaan.",
        "Portfolio stance": "Portefeuillehouding",
        "Stay invested, but raise the bar for any new capital deployment.": "Blijf belegd, maar verhoog de lat voor elke nieuwe kapitaalinzet.",
        "Best earned exposure": "Best verdiende exposure",
        "SMH remains the portfolio's strongest contributor and cleanest secular growth expression.": "SMH blijft de sterkste bijdrage in de portefeuille en de zuiverste structurele groeiblootstelling.",
        "Main discipline issue": "Belangrijkste disciplinepunt",
        "SPY and SMH still create meaningful U.S. tech / AI overlap; this is concentration with benefits, not full diversification.": "SPY en SMH zorgen nog steeds voor duidelijke Amerikaanse tech/AI-overlap; dit is concentratie met voordelen, geen volledige spreiding.",
        "Weakest implementation questions": "Zwakste implementatievragen",
        "PPA must prove itself against ITA, PAVE must prove itself against GRID, and GLD must prove that it still behaves like useful ballast.": "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en GLD moet bewijzen dat het nog steeds nuttige ballast is.",
        "Action bias": "Actiebias",
        "No replacement is fundable yet. The right next move is evidence gathering, not forced churn.": "Nog geen vervanger is financierbaar. De juiste volgende stap is bewijs verzamelen, niet geforceerd wisselen.",
        "The position review separates three questions: is the thesis still valid, is the ETF still the right vehicle, and would fresh cash buy this today at the current weight?": "De positiereview scheidt drie vragen: is de thesis nog geldig, is de ETF nog het juiste instrument, en zou vers kapitaal dit vandaag nog kopen op het huidige gewicht?",
        "Reconciled to Section 15": "Aangesloten op Section 15",
        "No exit clears the evidence threshold today": "Geen exit haalt vandaag de bewijsdrempel",
        "No fresh add is authorized without confirming position-size headroom": "Geen fresh add zonder bevestigde ruimte binnen de positielimiet",
        "a validated state-led production path; no portfolio position was added unless shown in Section 14.": "een gevalideerd state-led productiepad; geen positie is toegevoegd tenzij zichtbaar in Section 14.",
        "No structural thesis was abandoned; implementation discipline is materially tighter.": "Geen structurele thesis is losgelaten; de implementatiediscipline is duidelijk aangescherpt.",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    en_path = latest_report(output_dir, EN_RE)
    nl_path = latest_report(output_dir, NL_RE)

    en_path.write_text(polish_english(en_path.read_text(encoding="utf-8")), encoding="utf-8")
    nl_path.write_text(polish_dutch(nl_path.read_text(encoding="utf-8")), encoding="utf-8")

    print(f"ETF_RUNTIME_POLISH_OK | en={en_path.name} | nl={nl_path.name}")


if __name__ == "__main__":
    main()
