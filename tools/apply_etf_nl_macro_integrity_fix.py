from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {old[:140]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply() -> None:
    replace_once(
        "runtime/macro_report_surface.py",
        '    "Tightening / inflation-sensitive": "Verkrappend / inflatiegevoelig",',
        '    "Tightening / inflation-sensitive": "Verkrappend / inflatiegevoelig",\n    "On hold after June tightening / data-dependent": "Ongewijzigd na de verkrapping in juni / datagedreven",',
    )
    replace_once(
        "runtime/macro_report_surface.py",
        '    "ECB rate-policy tightening": "ECB-renteverkrapping",',
        '    "ECB rate-policy tightening": "ECB-renteverkrapping",\n    "ECB rate-policy hold": "ECB-rente ongewijzigd",',
    )
    replace_once(
        "runtime/macro_report_surface.py",
        '    "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad.": "Roteer niet agressief tenzij een regimeverschuiving minstens twee runs aanhoudt of cross-asset bevestiging breed wordt.",',
        '    "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad.": "Roteer niet agressief tenzij een regimeverschuiving minstens twee runs aanhoudt of cross-asset bevestiging breed wordt.",\n    "Do not rotate aggressively unless a regime shift persists across at least two distinct report dates or cross-asset confirmation becomes broad.": "Roteer niet agressief tenzij een regimeverschuiving op minstens twee afzonderlijke rapportdatums aanhoudt of cross-assetbevestiging breed wordt.",',
    )
    replace_once(
        "runtime/macro_report_surface.py",
        '    "IEFA exposure is now present, but further non-U.S. developed allocations still require relative-strength, pricing and portfolio-discipline confirmation.": "IEFA-blootstelling is nu aanwezig, maar verdere allocaties naar ontwikkelde markten buiten de VS vragen nog bevestiging in relatieve sterkte, prijsbasis en portefeuillediscipline.",',
        '    "IEFA exposure is now present, but further non-U.S. developed allocations still require relative-strength, pricing and portfolio-discipline confirmation.": "IEFA-blootstelling is nu aanwezig, maar verdere allocaties naar ontwikkelde markten buiten de VS vragen nog bevestiging in relatieve sterkte, prijsbasis en portefeuillediscipline.",\n    "IEFA exposure is already material; further allocation still requires relative-strength, pricing and portfolio-concentration confirmation.": "IEFA is al een materiële positie; verdere allocatie vraagt nog bevestiging in relatieve sterkte, prijsbasis en portefeuilleconcentratie.",',
    )
    replace_once(
        "runtime/macro_report_surface.py",
        '    "The ECB raised rates this week in response to renewed inflation pressure; this raises the hurdle for rate-sensitive and non-U.S. developed-market exposure but does not override pricing, relative-strength or portfolio-discipline gates.": "De ECB verhoogde deze week de rente vanwege hernieuwde inflatiedruk; dit verhoogt de toetsingsdrempel voor rentegevoelige en niet-Amerikaanse ontwikkelde-marktenblootstelling, maar vervangt geen koers-, relatieve-sterkte- of portefeuillediscipline.",',
        '    "The ECB raised rates this week in response to renewed inflation pressure; this raises the hurdle for rate-sensitive and non-U.S. developed-market exposure but does not override pricing, relative-strength or portfolio-discipline gates.": "De ECB verhoogde deze week de rente vanwege hernieuwde inflatiedruk; dit verhoogt de toetsingsdrempel voor rentegevoelige en niet-Amerikaanse ontwikkelde-marktenblootstelling, maar vervangt geen koers-, relatieve-sterkte- of portefeuillediscipline.",\n    "The ECB kept its key interest rates unchanged on 23 July 2026 and retained a data-dependent, meeting-by-meeting approach; this is descriptive policy context and does not override portfolio gates.": "De ECB hield de beleidsrentes op 23 juli 2026 ongewijzigd en bleef per vergadering datagedreven beslissen; dit is beschrijvende beleidscontext en vervangt geen portefeuillevoorwaarden.",\n    "The ECB kept its key interest rates unchanged on 23 July 2026 and retained a meeting-by-meeting, data-dependent approach.": "De ECB hield de beleidsrentes op 23 juli 2026 ongewijzigd en bleef per vergadering datagedreven beslissen.",\n    "Renewed inflation pressure or weaker growth can change the relative-strength hurdle for developed-market exposure outside the United States.": "Hernieuwde inflatiedruk of zwakkere groei kan de relatieve-sterktedrempel voor ontwikkelde markten buiten de Verenigde Staten veranderen.",',
    )
    replace_once(
        "runtime/macro_report_surface.py",
        'NL_REGEX_REPLACEMENTS = [\n    (\n        re.compile(r"\\bRisk-on growth has persisted for (\\d+) run\\(s\\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\\.?,?", re.IGNORECASE),',
        'NL_REGEX_REPLACEMENTS = [\n    (\n        re.compile(r"\\bRisk-on growth has persisted across (\\d+) weekly observation\\(s\\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\\.?,?", re.IGNORECASE),\n        lambda m: f"Risk-on groei houdt al {m.group(1)} wekelijkse observaties aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-assetbevestiging blijft gemengd.",\n    ),\n    (\n        re.compile(r"\\bRisk-on narrow leadership has persisted across (\\d+) weekly observation\\(s\\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\\.?,?", re.IGNORECASE),\n        lambda m: f"Risk-on met smal marktleiderschap houdt al {m.group(1)} wekelijkse observaties aan; de overgangsfase is stabiel, de marktbreedte is gemengd en cross-assetbevestiging blijft gemengd.",\n    ),\n    (\n        re.compile(r"\\bRisk-on growth has persisted for (\\d+) run\\(s\\); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed\\.?,?", re.IGNORECASE),',
    )

    replace_once(
        "runtime/apply_nl_localization.py",
        '    text = text.replace("twelve_data", "externe slotkoersbron")\n    return text',
        '    text = text.replace("twelve_data", "externe slotkoersbron")\n    text = text.replace("Portfolio valuation based on confirmed prices and official holdings", "Waardering op basis van bevestigde slotkoersen en officiële posities")\n    text = text.replace("Portfolio valuation based on confirmed closing prices and official holdings", "Waardering op basis van bevestigde slotkoersen en officiële posities")\n    return text',
    )

    replace_once(
        "tools/validate_etf_report_portfolio_integrity.py",
        'import re\nfrom pathlib import Path\n\nfrom runtime.report_portfolio_integrity_contract import validate_report_portfolio_integrity',
        'import re\nimport sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nif str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))\n\nfrom runtime.report_portfolio_integrity_contract import validate_report_portfolio_integrity',
    )


if __name__ == "__main__":
    apply()
    print("ETF_NL_MACRO_INTEGRITY_FIX_OK")
