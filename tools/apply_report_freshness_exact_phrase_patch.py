from __future__ import annotations

from pathlib import Path


class PatchError(RuntimeError):
    pass


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise PatchError(f"Expected exact-phrase anchor missing in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def add_mapping_after(path: Path, anchor: str, mapping: str) -> bool:
    return replace_once(path, anchor, anchor + "\n" + mapping)


def main() -> None:
    path = Path("runtime/report_freshness_contract.py")
    changed = False

    changed |= replace_once(
        path,
        '"Only watchlist; non-U.S. exposure remains a diversification gap.": f"IEFA already represents {iefa_weight:.2f}% of the portfolio; further expansion is not automatic and remains relative-strength and concentration gated.",',
        '"Watchlist only; non-U.S. exposure remains a diversification gap.": f"IEFA already represents {iefa_weight:.2f}% of the portfolio; further expansion is not automatic and remains relative-strength and concentration gated.",',
    )
    changed |= replace_once(
        path,
        '            "only watchlist; non-u.s. exposure remains a diversification gap",\n',
        '            "only watchlist; non-u.s. exposure remains a diversification gap",\n            "watchlist only; non-u.s. exposure remains a diversification gap",\n',
    )

    broken_helper_line = '    next_section = text.find(f"\n## {section_number + 1}.", start + len(marker))'
    escaped_helper_line = '    next_section = text.find(f"\\n## {section_number + 1}.", start + len(marker))'
    changed |= replace_once(path, broken_helper_line, escaped_helper_line)

    changed |= add_mapping_after(
        path,
        '                    "| Ontwikkelde markten buiten de VS | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Relatieve sterkte tegenover de relevante huidige positie is nog onvoldoende overtuigend. | Sterkere relatieve sterkte en duidelijke aansluiting op de beleggingscase. |": "| Ontwikkelde markten buiten de VS | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend. | Heroverweeg alleen bij een duidelijke wijziging in relatieve sterkte, factorconcentratie of financieringsbron. |",',
        '                    "| Ontwikkelde markten buiten de VS | IEFA | Relatieve sterkte tegenover de relevante huidige positie is nog onvoldoende overtuigend. | Sterkere relatieve sterkte en duidelijke aansluiting op de beleggingscase. |": "| Ontwikkelde markten buiten de VS | IEFA | Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend. | Heroverweeg alleen bij een duidelijke wijziging in relatieve sterkte, factorconcentratie of financieringsbron. |",',
    )
    changed |= add_mapping_after(
        path,
        '                    "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) op de volglijst": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) als kwaliteitsalternatief en [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) als reeds gefinancierde diversificatie",',
        '                    "QUAL, IEFA op de volglijst": "QUAL als kwaliteitsalternatief en IEFA als reeds gefinancierde diversificatie",',
    )
    changed |= add_mapping_after(
        path,
        '                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven onder implementatie- en vervangingsreview; bij DFEN moet ook het hefboomprofiel expliciet worden meegewogen.",',
        '                    "PPA en PAVE blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.": "DFEN en PAVE blijven onder implementatie- en vervangingsreview; bij DFEN moet ook het hefboomprofiel expliciet worden meegewogen.",',
    )
    changed |= add_mapping_after(
        path,
        '                    "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst": "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst",',
        '                    "Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, PPA en PAVE expliciet worden getoetst": "Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, DFEN en PAVE expliciet worden getoetst",',
    )
    changed |= add_mapping_after(
        path,
        '                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA), [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) tegenover [GRID](https://www.tradingview.com/chart/?symbol=GRID)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden getoetst aan niet-gehevelde defensiealternatieven, en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) aan [GRID](https://www.tradingview.com/chart/?symbol=GRID)",',
        '                    "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID": "DFEN moet worden getoetst aan niet-gehevelde defensiealternatieven, en PAVE aan GRID",',
    )
    changed |= add_mapping_after(
        path,
        '                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden vergeleken met niet-gehevelde defensiealternatieven zoals [ITA](https://www.tradingview.com/chart/?symbol=ITA) en [PPA](https://www.tradingview.com/chart/?symbol=PPA)",',
        '                    "PPA moet zich bewijzen tegenover ITA": "DFEN moet worden vergeleken met niet-gehevelde defensiealternatieven zoals ITA en PPA",',
    )
    changed |= add_mapping_after(
        path,
        '                    "Houd [PPA](https://www.tradingview.com/chart/?symbol=PPA) onder herbeoordeling": "Houd de implementatiekwaliteit en het hefboomprofiel van [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) onder herbeoordeling",',
        '                    "Houd PPA onder herbeoordeling": "Houd de implementatiekwaliteit en het hefboomprofiel van DFEN onder herbeoordeling",',
    )

    changed |= add_mapping_after(
        path,
        '                "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) watchlist": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) as a quality alternative and [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) as an already funded diversifier",',
        '                "QUAL, IEFA watchlist": "QUAL as a quality alternative and IEFA as an already funded diversifier",',
    )
    changed |= add_mapping_after(
        path,
        '                "[PPA](https://www.tradingview.com/chart/?symbol=PPA) and [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) remain replaceable until their ETF implementation quality is proven.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) and [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) remain under implementation and replacement review; DFEN\'s leverage profile must also be assessed explicitly.",',
        '                "PPA and PAVE remain replaceable until their ETF implementation quality is proven.": "DFEN and PAVE remain under implementation and replacement review; DFEN\'s leverage profile must also be assessed explicitly.",',
    )
    changed |= add_mapping_after(
        path,
        '                "[PPA](https://www.tradingview.com/chart/?symbol=PPA) must justify itself versus [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) must be compared with unlevered defense alternatives such as [ITA](https://www.tradingview.com/chart/?symbol=ITA) and [PPA](https://www.tradingview.com/chart/?symbol=PPA)",',
        '                "PPA must justify itself versus ITA": "DFEN must be compared with unlevered defense alternatives such as ITA and PPA",',
    )
    changed |= add_mapping_after(
        path,
        '                "Hold [PPA](https://www.tradingview.com/chart/?symbol=PPA) under review": "Keep [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) implementation quality and leverage under review",',
        '                "Hold PPA under review": "Keep DFEN implementation quality and leverage under review",',
    )

    changed |= add_mapping_after(
        path,
        '                    "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht.": f"De portefeuille heeft via IEFA al {iefa_weight:.2f}% niet-Amerikaanse ontwikkelde-marktenblootstelling; valuta- en regioconcentratie moeten daarom actief worden bewaakt.",',
        '                    "De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS.": f"IEFA biedt al een materiële allocatie naar ontwikkelde markten buiten de VS ({iefa_weight:.2f}%); verdere wijzigingen vereisen relatieve-sterkte- en concentratiebewijs.",',
    )
    changed |= add_mapping_after(
        path,
        '                "Zero allocation is an explicit bet on U.S. exceptionalism.": f"The portfolio already carries {iefa_weight:.2f}% non-U.S. developed-market exposure through IEFA; currency and regional concentration therefore require active monitoring.",',
        '                "Zero allocation is an explicit U.S. exceptionalism bet.": f"The portfolio already carries {iefa_weight:.2f}% non-U.S. developed-market exposure through IEFA; currency and regional concentration therefore require active monitoring.",',
    )
    changed |= add_mapping_after(
        path,
        '                "Zero allocation is an explicit U.S. exceptionalism bet.": f"The portfolio already carries {iefa_weight:.2f}% non-U.S. developed-market exposure through IEFA; currency and regional concentration therefore require active monitoring.",',
        '                "Portfolio has limited non-U.S. exposure.": f"IEFA already provides a material non-U.S. developed-market allocation ({iefa_weight:.2f}%); further changes require relative-strength and concentration evidence.",',
    )
    changed |= add_mapping_after(
        path,
        '                "| Non-U.S. developed market diversification | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Scored below the live radar cutoff versus stronger funded and challenger lanes. | Becomes fundable if U.S. factor concentration rises or non-U.S. breadth improves. |": "| Non-U.S. developed market diversification | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Existing funded position; no additional lane promotion was granted this run. | Reassess only if relative strength, factor concentration or the funding case changes materially. |",',
        '                "| Non-U.S. developed market diversification | IEFA | Scored below the live radar cutoff versus stronger funded and challenger lanes. | Becomes fundable if U.S. factor concentration rises or non-U.S. breadth improves. |": "| Non-U.S. developed market diversification | IEFA | Existing funded position; no additional lane promotion was granted this run. | Reassess only if relative strength, factor concentration or the funding case changes materially. |",',
    )

    changed |= replace_once(
        path,
        '            "zero allocation is an explicit bet",\n',
        '            "zero allocation is an explicit bet",\n            "zero allocation is an explicit u.s. exceptionalism bet",\n            "portfolio has limited non-u.s. exposure",\n            "de portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de vs",\n',
    )

    print(f"ETF_REPORT_FRESHNESS_EXACT_PHRASE_PATCH_OK | changed={str(changed).lower()}")


if __name__ == "__main__":
    main()
