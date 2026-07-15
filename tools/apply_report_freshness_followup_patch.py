from __future__ import annotations

from pathlib import Path

from tools.apply_report_freshness_exact_phrase_patch import main as apply_exact_phrase_patch


class PatchError(RuntimeError):
    pass


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise PatchError(f"Expected follow-up anchor missing in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def main() -> None:
    path = Path("runtime/report_freshness_contract.py")
    changed = False
    changed |= replace_once(
        path,
        """def _replace_many(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _apply_state_consistency""",
        """def _replace_many(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _replace_in_section(text: str, section_number: int, replacements: dict[str, str]) -> str:
    marker = f"## {section_number}."
    start = text.find(marker)
    if start == -1:
        return text
    next_section = text.find(f"\n## {section_number + 1}.", start + len(marker))
    if next_section == -1:
        next_section = len(text)
    section = _replace_many(text[start:next_section], replacements)
    return text[:start] + section + text[next_section:]


def _apply_state_consistency""",
    )

    old_nl = '''        if has_dfen and not has_ppa:
            replacements.update(
                {
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven onder implementatie- en vervangingsreview; bij DFEN moet ook het hefboomprofiel expliciet worden meegewogen.",
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden vergeleken met niet-gehevelde defensiealternatieven zoals [ITA](https://www.tradingview.com/chart/?symbol=ITA) en [PPA](https://www.tradingview.com/chart/?symbol=PPA)",
                    "Houd [PPA](https://www.tradingview.com/chart/?symbol=PPA) onder herbeoordeling": "Houd de implementatiekwaliteit en het hefboomprofiel van [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) onder herbeoordeling",
                    "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst": "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst",
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA), [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) tegenover [GRID](https://www.tradingview.com/chart/?symbol=GRID)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden getoetst aan niet-gehevelde defensiealternatieven, en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) aan [GRID](https://www.tradingview.com/chart/?symbol=GRID)",
                }
            )
        return _replace_many(text, replacements)
'''
    new_nl = '''        text = _replace_many(text, replacements)
        if has_iefa:
            text = _replace_in_section(
                text,
                9,
                {
                    "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) op de volglijst": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) als kwaliteitsalternatief en [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) als reeds gefinancierde diversificatie",
                },
            )
        if has_dfen and not has_ppa:
            text = _replace_in_section(
                text,
                5,
                {
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven onder implementatie- en vervangingsreview; bij DFEN moet ook het hefboomprofiel expliciet worden meegewogen.",
                },
            )
            text = _replace_in_section(
                text,
                6,
                {
                    "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst": "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst",
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA), [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) tegenover [GRID](https://www.tradingview.com/chart/?symbol=GRID)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden getoetst aan niet-gehevelde defensiealternatieven, en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) aan [GRID](https://www.tradingview.com/chart/?symbol=GRID)",
                },
            )
            text = _replace_in_section(
                text,
                9,
                {
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden vergeleken met niet-gehevelde defensiealternatieven zoals [ITA](https://www.tradingview.com/chart/?symbol=ITA) en [PPA](https://www.tradingview.com/chart/?symbol=PPA)",
                    "Houd [PPA](https://www.tradingview.com/chart/?symbol=PPA) onder herbeoordeling": "Houd de implementatiekwaliteit en het hefboomprofiel van [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) onder herbeoordeling",
                },
            )
        return text
'''
    changed |= replace_once(path, old_nl, new_nl)

    old_en = '''    if has_dfen and not has_ppa:
        replacements.update(
            {
                "PPA and PAVE remain replaceable until ETF implementation quality is proven.": "DFEN and PAVE remain under implementation and replacement review; DFEN's leverage profile must also be assessed explicitly.",
                "PPA must prove itself versus ITA": "DFEN must be compared with unlevered defense alternatives such as ITA and PPA",
                "Keep PPA under review": "Keep DFEN implementation quality and leverage under review",
                "SPY, PPA and PAVE must be explicitly tested": "SPY, DFEN and PAVE must be explicitly tested",
            }
        )
    return _replace_many(text, replacements)
'''
    new_en = '''    text = _replace_many(text, replacements)
    if has_iefa:
        text = _replace_in_section(
            text,
            9,
            {
                "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) watchlist": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) as a quality alternative and [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) as an already funded diversifier",
            },
        )
    if has_dfen and not has_ppa:
        text = _replace_in_section(
            text,
            5,
            {
                "[PPA](https://www.tradingview.com/chart/?symbol=PPA) and [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) remain replaceable until their ETF implementation quality is proven.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) and [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) remain under implementation and replacement review; DFEN's leverage profile must also be assessed explicitly.",
            },
        )
        text = _replace_in_section(
            text,
            9,
            {
                "[PPA](https://www.tradingview.com/chart/?symbol=PPA) must justify itself versus [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) must be compared with unlevered defense alternatives such as [ITA](https://www.tradingview.com/chart/?symbol=ITA) and [PPA](https://www.tradingview.com/chart/?symbol=PPA)",
                "Hold [PPA](https://www.tradingview.com/chart/?symbol=PPA) under review": "Keep [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) implementation quality and leverage under review",
            },
        )
    return text
'''
    changed |= replace_once(path, old_en, new_en)
    apply_exact_phrase_patch()

    print(f"ETF_REPORT_FRESHNESS_FOLLOWUP_PATCH_OK | changed={str(changed).lower()}")


if __name__ == "__main__":
    main()
