from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from runtime.portfolio_attribution_basis import entry_basis, ledger_entry_bases, to_float


class ReportPortfolioIntegrityError(RuntimeError):
    pass


FRESH_PRICE_STATUSES = {
    "fresh_close",
    "fresh_fallback_source",
    "fresh_exact_close",
    "fresh_exact_unverified",
}

ETF_NAMES = {
    "CIBR": "First Trust NASDAQ Cybersecurity ETF",
    "GSG": "iShares S&P GSCI Commodity-Indexed Trust",
    "IEFA": "iShares Core MSCI EAFE ETF",
    "PAVE": "Global X U.S. Infrastructure Development ETF",
    "SMH": "VanEck Semiconductor ETF",
    "URNM": "Sprott Uranium Miners ETF",
    "XBI": "SPDR S&P Biotech ETF",
    "XLU": "Utilities Select Sector SPDR Fund",
    "XLV": "Health Care Select Sector SPDR Fund",
}

THESIS_EN = {
    "CIBR": "Cybersecurity resilience",
    "GSG": "Broad commodity and inflation-sensitive hedge exposure",
    "IEFA": "Developed markets outside the United States",
    "PAVE": "Grid and infrastructure capital expenditure",
    "SMH": "AI compute and semiconductor leadership",
    "URNM": "Nuclear and uranium cycle exposure",
    "XBI": "Biotechnology innovation",
    "XLU": "Defensive utilities and rate-sensitive ballast",
    "XLV": "Healthcare quality and defensive growth",
}

THESIS_NL = {
    "CIBR": "Cybersecurityweerbaarheid",
    "GSG": "Brede grondstoffen- en inflatiegevoelige hedgepositie",
    "IEFA": "Ontwikkelde markten buiten de Verenigde Staten",
    "PAVE": "Netwerk- en infrastructuurinvesteringen",
    "SMH": "AI-rekenkracht en semiconductorleiderschap",
    "URNM": "Kernenergie- en uraniumcyclus",
    "XBI": "Biotechnologische innovatie",
    "XLU": "Defensieve nutsbedrijven en rentegevoelige ballast",
    "XLV": "Healthcarekwaliteit en defensieve groei",
}

ROLE_EN = {
    "CIBR": "Portfolio allocation",
    "GSG": "Portfolio allocation",
    "IEFA": "Portfolio allocation",
    "PAVE": "Portfolio allocation",
    "SMH": "Growth engine",
    "URNM": "Strategic energy",
    "XBI": "Portfolio allocation",
    "XLU": "Portfolio allocation",
    "XLV": "Portfolio allocation",
}

ROLE_NL = {
    "CIBR": "Portefeuilleallocatie",
    "GSG": "Portefeuilleallocatie",
    "IEFA": "Portefeuilleallocatie",
    "PAVE": "Portefeuilleallocatie",
    "SMH": "Groeimotor",
    "URNM": "Strategische energie",
    "XBI": "Portefeuilleallocatie",
    "XLU": "Portefeuilleallocatie",
    "XLV": "Portefeuilleallocatie",
}

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^\)]+\)")


def _plain(value: str) -> str:
    return MARKDOWN_LINK_RE.sub(lambda match: match.group(1), value)


def _float(value: Any, default: float = 0.0) -> float:
    parsed = to_float(value)
    return default if parsed is None else parsed


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in (state.get("positions") or [])
        if isinstance(row, dict) and _ticker(row.get("ticker")) not in {"", "CASH"}
    ]


def active_tickers(state: dict[str, Any]) -> set[str]:
    return {_ticker(row.get("ticker")) for row in _positions(state)}


def _position_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): row for row in _positions(state)}


def _weight(position: dict[str, Any]) -> float:
    return _float(position.get("current_weight_pct"), _float(position.get("weight_pct")))


def _report_date(state: dict[str, Any]) -> str:
    return str(state.get("requested_close_date") or state.get("report_date") or "").strip()[:10]


def _fresh_pricing(state: dict[str, Any]) -> bool:
    rows = _positions(state)
    return bool(rows) and all(str(row.get("pricing_status") or "").strip() in FRESH_PRICE_STATUSES for row in rows)


def _current_execution_present(state: dict[str, Any]) -> bool:
    for row in _positions(state):
        action = str(row.get("action_executed_this_run") or "").strip().lower()
        shares_delta = abs(_float(row.get("shares_delta_this_run")))
        if action not in {"", "none", "no change"} and shares_delta > 1e-9:
            return True
    return False


def _trade_intents(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = state.get("trade_intents") or (state.get("rotation_plan") or {}).get("trade_intents") or []
    return [row for row in rows if isinstance(row, dict)]


def _no_action(state: dict[str, Any]) -> bool:
    return not _trade_intents(state) and not _current_execution_present(state)


def _section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = re.search(r"\n## (?:\d+|\d+[A-Z]?)[\.]?\s", text[start + len(heading) :])
    end = len(text) if next_heading is None else start + len(heading) + next_heading.start()
    return text[start:end]


def _replace_section(text: str, heading: str, body: str) -> str:
    start = text.find(heading)
    if start == -1:
        return text
    search_start = start + len(heading)
    next_heading = re.search(r"\n## (?:\d+|\d+[A-Z]?)[\.]?\s", text[search_start:])
    end = len(text) if next_heading is None else search_start + next_heading.start()
    return text[:start] + heading + "\n\n" + body.strip() + "\n" + text[end:]


def _replace_subsection(text: str, heading: str, next_heading: str, body: str) -> str:
    start = text.find(heading)
    if start == -1:
        return text
    body_start = start + len(heading)
    end = text.find(next_heading, body_start)
    if end == -1:
        return text
    return text[:start] + heading + "\n\n" + body.strip() + "\n\n" + text[end:]


def _basis_metrics(state: dict[str, Any]) -> dict[str, dict[str, float | None]]:
    bases = ledger_entry_bases(state)
    out: dict[str, dict[str, float | None]] = {}
    for row in _positions(state):
        ticker = _ticker(row.get("ticker"))
        basis = entry_basis(row, state, bases)
        current_value = _float(row.get("previous_market_value_eur"), _float(row.get("market_value_eur")))
        current_price = _float(row.get("previous_price_local"), _float(row.get("current_price_local")))
        avg_entry = _float((basis or {}).get("avg_entry_local"), 0.0) or None
        cost = _float((basis or {}).get("cost_basis_eur"), 0.0) or None
        pnl_pct: float | None
        if cost and cost > 0:
            pnl_pct = round((current_value - cost) / cost * 100.0, 2)
        else:
            fallback = to_float(row.get("pnl_pct"))
            pnl_pct = None if fallback is None else round(fallback, 2)
        out[ticker] = {
            "avg_entry_local": avg_entry,
            "pnl_pct": pnl_pct,
            "current_price_local": current_price,
        }
    return out


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def _continuity_table(state: dict[str, Any], language: str) -> str:
    metrics = _basis_metrics(state)
    if language == "nl":
        lines = [
            "| Ticker | ETF-naam | Richting | Gewicht % | Gem. instap | Huidige prijs | P/L % | Oorspronkelijke thesis | Rol |",
            "|---|---|---|---:|---:|---:|---:|---|---|",
        ]
    else:
        lines = [
            "| Ticker | ETF name | Direction | Weight % | Avg entry | Current price | P/L % | Original thesis | Role |",
            "|---|---|---|---:|---:|---:|---:|---|---|",
        ]
    for row in _positions(state):
        ticker = _ticker(row.get("ticker"))
        basis = metrics.get(ticker, {})
        if language == "nl":
            direction = "Longpositie"
            thesis = THESIS_NL.get(ticker, ticker)
            role = ROLE_NL.get(ticker, "Portefeuilleallocatie")
        else:
            direction = "Long"
            thesis = THESIS_EN.get(ticker, ticker)
            role = ROLE_EN.get(ticker, "Portfolio allocation")
        lines.append(
            f"| {ticker} | {ETF_NAMES.get(ticker, ticker)} | {direction} | {_weight(row):.2f} | "
            f"{_fmt(basis.get('avg_entry_local'))} | {_fmt(basis.get('current_price_local'))} | "
            f"{_fmt(basis.get('pnl_pct'))} | {thesis} | {role} |"
        )
    return "\n".join(lines)


def _decision_cockpit(state: dict[str, Any], language: str) -> str:
    positions = _position_map(state)
    smh_weight = _weight(positions.get("SMH", {}))
    if language == "nl":
        action = "geen portefeuilleactie" if _no_action(state) else "zie de voorgestelde of uitgevoerde actietabel"
        return "\n".join(
            [
                f"- **Deze week:** {action}.",
                f"- **Belangrijkste actieve risico:** SMH is {smh_weight:.2f}% van de portefeuille en blijft boven de zachte limiet van 25%.",
                "- **Belangrijkste actieve reviews:** PAVE tegenover GRID, de GSG-hedgerol en de close-first beoordeling van URNM en XLU.",
                "- **Niet-aangehouden onderzoeksinstrumenten:** PPA en ITA zijn uitsluitend defensie-volglijstkandidaten; SPY is uitsluitend een marktbenchmark.",
                "- **Trigger voor volgende actie:** een mutatie moet het huidige 9/8-positieprobleem verbeteren, een geldige prijsbasis hebben en de volledige relatieve-sterkte- en thesiscontrole doorstaan.",
                "- **Nieuw kapitaal:** er mag geen nieuwe ticker worden geopend zolang het aantal actieve posities niet is teruggebracht tot maximaal acht.",
            ]
        )
    action = "no portfolio action" if _no_action(state) else "see the proposed or executed action table"
    return "\n".join(
        [
            f"- **This week:** {action}.",
            f"- **Main active risk:** SMH is {smh_weight:.2f}% of the portfolio and remains above the 25% soft cap.",
            "- **Main active reviews:** PAVE versus GRID, the GSG hedge role, and the close-first assessment of URNM and XLU.",
            "- **Non-held research instruments:** PPA and ITA are defense-watchlist candidates only; SPY is a market benchmark only.",
            "- **Next-action trigger:** any change must improve the current 9/8 position-count breach, use a valid pricing basis, and pass the full relative-strength and thesis review.",
            "- **Fresh capital:** no new ticker may be opened until active positions are reduced to eight or fewer.",
        ]
    )


def _risk_section(state: dict[str, Any], language: str) -> str:
    positions = _position_map(state)
    smh = _weight(positions.get("SMH", {}))
    iefa = _weight(positions.get("IEFA", {}))
    if language == "nl":
        return "\n".join(
            [
                f"- SMH weegt {smh:.2f}% en overschrijdt daarmee de zachte positielimiet van 25%; aanvullend kapitaal is geblokkeerd.",
                "- URNM blijft een materiële negatieve bijdrager en XLU is te klein voor een efficiënte gedeeltelijke transactie; beide horen in de close-first beoordeling zolang de portefeuille 9 posities tegenover een maximum van 8 telt.",
                "- PAVE is een huidige positie onder implementatie- en vervangingsreview tegenover GRID.",
                "- De GSG-hedgerol moet periodiek worden bewezen en is geen vanzelfsprekende stabilisator.",
                f"- IEFA levert een materiële allocatie naar ontwikkelde markten buiten de Verenigde Staten ({iefa:.2f}%); verdere uitbreiding vraagt relatieve-sterkte- en concentratiebevestiging.",
            ]
        )
    return "\n".join(
        [
            f"- SMH is {smh:.2f}% of the portfolio and therefore exceeds the 25% soft position cap; additional capital is blocked.",
            "- URNM remains a material negative contributor and XLU is too small for an efficient partial trade; both belong in the close-first review while the portfolio has 9 positions against a maximum of 8.",
            "- PAVE is a current holding under implementation and replacement review versus GRID.",
            "- The GSG hedge role must be re-earned periodically and is not an automatic stabilizer.",
            f"- IEFA provides a material developed-ex-U.S. allocation ({iefa:.2f}%); further expansion requires relative-strength and concentration confirmation.",
        ]
    )


def _conclusion_section(state: dict[str, Any], language: str) -> str:
    if not _no_action(state):
        if language == "nl":
            return "\n".join(
                [
                    "- **Portefeuillehouding:** voorgestelde of uitgevoerde wijzigingen worden uitsluitend door de autoritatieve actietabellen bepaald.",
                    "- **Best onderbouwde blootstelling:** SMH blijft structureel sterk, maar concentratie- en positielimieten blijven bindend.",
                    "- **Belangrijkste disciplinepunt:** iedere mutatie moet de positiecapaciteit verbeteren en de prijs-, relatieve-sterkte- en thesistoets doorstaan.",
                    "- **Volglijstscheiding:** PPA en ITA blijven niet-aangehouden defensie-instrumenten totdat een afzonderlijke, geldige allocatiebeslissing bestaat.",
                ]
            )
        return "\n".join(
            [
                "- **Portfolio stance:** proposed or executed changes are determined only by the authoritative action tables.",
                "- **Best-supported exposure:** SMH remains structurally strong, but concentration and position limits remain binding.",
                "- **Main discipline point:** every transition must improve portfolio capacity and pass pricing, relative-strength and thesis review.",
                "- **Watchlist separation:** PPA and ITA remain non-held defense instruments until a separate valid allocation decision exists.",
            ]
        )
    if language == "nl":
        return "\n".join(
            [
                "- **Portefeuillehouding:** deze review stelt geen positie- of cashwijziging voor; de officiële aantallen stukken blijven ongewijzigd.",
                "- **Best onderbouwde blootstelling:** SMH blijft de sterkste structurele groeiblootstelling, maar de huidige weging ligt boven de zachte limiet.",
                "- **Belangrijkste disciplinepunt:** herstel eerst het aantal actieve posities van 9 naar maximaal 8; open in de tussentijd geen nieuwe ticker.",
                "- **Huidige implementatiereviews:** PAVE tegenover GRID, de GSG-hedgerol en de close-first rangschikking van URNM en XLU.",
                "- **Volglijstscheiding:** PPA tegenover ITA is uitsluitend een vergelijking tussen niet-aangehouden defensie-instrumenten en geen portefeuillerisico.",
            ]
        )
    return "\n".join(
        [
            "- **Portfolio stance:** this review proposes no position or cash change; official share quantities remain unchanged.",
            "- **Best-supported exposure:** SMH remains the strongest structural growth exposure, but its current weight is above the soft cap.",
            "- **Main discipline point:** restore active positions from 9 to no more than 8 before opening any new ticker.",
            "- **Current implementation reviews:** PAVE versus GRID, the GSG hedge role, and the close-first ranking of URNM and XLU.",
            "- **Watchlist separation:** PPA versus ITA is solely a comparison of non-held defense instruments and is not a portfolio risk.",
        ]
    )


def _allocation_map(state: dict[str, Any], language: str) -> str:
    iefa = _weight(_position_map(state).get("IEFA", {}))
    if language == "nl":
        rows = [
            ("Amerikaanse aandelen", "Neutraal", "Belegbaar, maar de portefeuille kent expliciet concentratierisico."),
            ("Ontwikkelde markten buiten de VS", "Neutraal", f"IEFA vertegenwoordigt {iefa:.2f}% van de portefeuille; verdere uitbreiding is niet automatisch."),
            ("Opkomende markten", "Onderwogen", "USD- en grondstoffengevoeligheid blijven tegenwind."),
            ("Large-cap", "Neutraal", "Kwaliteitsleiderschap blijft bruikbaar."),
            ("Small-cap", "Onderwogen", "Rentes en herfinanciering blijven beperkend."),
            ("Groei", "Neutraal", "Selectieve groei onder leiding van SMH blijft aantrekkelijk, maar is concentratiebegrensd."),
            ("Kwaliteit", "Overwogen", "Winstbestendigheid blijft waardevol."),
            ("Grondstoffen / hedge", "Neutraal", "De GSG-hedgerol blijft onder periodieke validatie."),
            ("Industrie / defensie", "Volglijst", "De structurele defensiecase is valide; PPA en ITA zijn niet-aangehouden instrumentkandidaten."),
            ("Valuta- en regioblootstelling", "Monitoren", "IEFA creëert ontwikkelde-marktenblootstelling buiten de VS; valuta- en regioconcentratie moeten afzonderlijk worden bewaakt."),
        ]
        header = ["| Segment | Positionering | Toelichting |", "|---|---|---|"]
    else:
        rows = [
            ("U.S. equities", "Neutral", "Investable, but portfolio concentration risk is explicit."),
            ("Developed markets outside the U.S.", "Neutral", f"IEFA represents {iefa:.2f}% of the portfolio; further expansion is not automatic."),
            ("Emerging markets", "Underweight", "USD and commodity sensitivity remain headwinds."),
            ("Large cap", "Neutral", "Quality leadership remains useful."),
            ("Small cap", "Underweight", "Rates and refinancing remain restrictive."),
            ("Growth", "Neutral", "Selective growth led by SMH remains attractive but concentration-capped."),
            ("Quality", "Overweight", "Earnings durability remains valuable."),
            ("Commodities / hedge", "Neutral", "The GSG hedge role remains under periodic validation."),
            ("Industrials / defense", "Watchlist", "The structural defense case is valid; PPA and ITA are non-held vehicle candidates."),
            ("Currency and regional exposure", "Monitor", "IEFA creates developed-ex-U.S. exposure; currency and regional concentration must be monitored separately."),
        ]
        header = ["| Segment | Stance | Explanation |", "|---|---|---|"]
    return "\n".join(header + [f"| {a} | {b} | {c} |" for a, b, c in rows])


def _second_order_map(state: dict[str, Any], language: str) -> str:
    if language == "nl":
        return "\n".join(
            [
                "| Drijver | Eerste-orde-effect | Tweede-orde-effect | Waarschijnlijke winnaars | Kwetsbare segmenten | ETF-implicatie | Timing | Vertrouwen |",
                "|---|---|---|---|---|---|---|---|",
                "| SMH-concentratie | SMH blijft de zuiverste gefinancierde groeiblootstelling | Een weging boven 25% verhoogt factor- en positierisico | SMH, SOXX | Overlappende AI- en semiconductorbeta | Geen extra kapitaal; bewaak verkleinings- of vervangingsbewijs | Direct | Hoog |",
                "| PAVE-implementatie | De infrastructuurthesis blijft valide | GRID kan een zuiverder instrument blijken | PAVE, GRID | Onvoldoende thematische zuiverheid | Houd de PAVE-versus-GRID-review actief | 1-3 maanden | Gemiddeld |",
                "| Defensie-volglijst | Defensie-uitgaven blijven structureel relevant | Instrumentkeuze tussen PPA en ITA blijft onbewezen | PPA, ITA | Verkeerde ETF-implementatie | Niet-aangehouden volglijstvergelijking; geen portefeuilleactie | 3-12 maanden | Gemiddeld |",
                "| Grondstoffenhedge | GSG kan aanbod- en inflatierisico diversifiëren | Opportuniteitskosten lopen op als de hedgerol niet bevestigt | GSG, DBC, cash | Onproductieve hedgepositie | Valideer de GSG-rol periodiek | Direct | Gemiddeld |",
            ]
        )
    return "\n".join(
        [
            "| Driver | First-order effect | Second-order effect | Likely beneficiaries | Vulnerable segments | ETF implication | Timing | Confidence |",
            "|---|---|---|---|---|---|---|---|",
            "| SMH concentration | SMH remains the cleanest funded growth exposure | A weight above 25% increases factor and position risk | SMH, SOXX | Overlapping AI and semiconductor beta | No additional capital; monitor reduction or replacement evidence | Immediate | High |",
            "| PAVE implementation | The infrastructure thesis remains valid | GRID may prove to be a cleaner vehicle | PAVE, GRID | Insufficient thematic purity | Keep the PAVE-versus-GRID review active | 1-3 months | Medium |",
            "| Defense watchlist | Defense spending remains structurally relevant | Vehicle selection between PPA and ITA remains unproven | PPA, ITA | Poor ETF implementation | Non-held watchlist comparison; no portfolio action | 3-12 months | Medium |",
            "| Commodity hedge | GSG can diversify supply and inflation risk | Opportunity cost rises if the hedge role does not confirm | GSG, DBC, cash | Unproductive hedge position | Revalidate the GSG role periodically | Immediate | Medium |",
        ]
    )


def _watchlist_table(state: dict[str, Any], language: str) -> str:
    if language == "nl":
        return "\n".join(
            [
                "| Thema | Primaire ETF | Alternatieve ETF | Waarom op de radar | Status |",
                "|---|---|---|---|---|",
                "| AI-rekenkrachtinfrastructuur | SMH | SOXX | SMH is de gefinancierde kernpositie; SOXX is de niet-aangehouden challenger. | Gefinancierd / concentratiebegrensd |",
                "| Defensie-innovatie / strategische weerbaarheid | PPA | ITA | Structurele defensiecase; beide ETF’s zijn uitsluitend onderzoekskandidaten. | Niet-aangehouden volglijstvergelijking |",
                "| Netuitbreiding / elektrificatie | PAVE | GRID | PAVE is de huidige positie; GRID is de niet-aangehouden vervangingskandidaat. | Huidige positie onder vervangingsreview |",
                "| Hedge- en grondstoffenbreedte | GSG | DBC / BIL | GSG is de huidige positie; hedgefunctie en opportuniteitskosten moeten worden bevestigd. | Huidige positie onder rolvalidatie |",
                "| Ontwikkelde markten buiten de VS | IEFA | EFA | IEFA is de huidige gefinancierde positie; EFA is uitsluitend een vergelijkingsinstrument. | Gefinancierd / monitoren |",
            ]
        )
    return "\n".join(
        [
            "| Theme | Primary ETF | Alternative ETF | Why it is on the radar | Status |",
            "|---|---|---|---|---|",
            "| AI compute infrastructure | SMH | SOXX | SMH is the funded core holding; SOXX is a non-held challenger. | Funded / concentration-capped |",
            "| Defense innovation / sovereign resilience | PPA | ITA | Structural defense case; both ETFs are research candidates only. | Non-held watchlist comparison |",
            "| Grid buildout / electrification | PAVE | GRID | PAVE is the current holding; GRID is the non-held replacement challenger. | Current holding under replacement review |",
            "| Commodity and hedge breadth | GSG | DBC / BIL | GSG is the current holding; hedge function and opportunity cost require confirmation. | Current holding under role validation |",
            "| Developed markets outside the U.S. | IEFA | EFA | IEFA is the funded current holding; EFA is a comparison instrument only. | Funded / monitor |",
        ]
    )


def _discipline_continuity(language: str) -> str:
    if language == "nl":
        return "\n".join(
            [
                "- SMH: huidige positie onder concentratiediscipline; geen aanvullend kapitaal boven de zachte limiet.",
                "- PAVE: huidige positie; directe vervangingsanalyse tegenover de niet-aangehouden challenger GRID blijft vereist.",
                "- GSG: huidige positie; hedgerol en opportuniteitskosten blijven onder validatie.",
                "- URNM en XLU: huidige posities in de close-first beoordeling zolang de portefeuille 9/8 posities telt.",
                "- PPA en ITA: niet-aangehouden defensie-volglijstinstrumenten; geen huidige positie en geen uitvoeringsautoriteit.",
                "- SPY: uitsluitend benchmark voor markt- en relatieve-sterktevergelijkingen; geen huidige positie.",
            ]
        )
    return "\n".join(
        [
            "- SMH: current holding under concentration discipline; no additional capital above the soft cap.",
            "- PAVE: current holding; direct replacement analysis versus non-held challenger GRID remains required.",
            "- GSG: current holding; hedge role and opportunity cost remain under validation.",
            "- URNM and XLU: current holdings in the close-first review while the portfolio remains at 9/8 positions.",
            "- PPA and ITA: non-held defense-watchlist instruments; no current position and no execution authority.",
            "- SPY: benchmark only for market and relative-strength comparisons; no current position.",
        ]
    )


def _changes_summary(state: dict[str, Any], language: str) -> str:
    if _no_action(state):
        if language == "nl":
            return "\n".join(
                [
                    "- Portefeuillewijzigingen: geen; aantallen stukken, actieve tickers en cash zijn in deze review niet gewijzigd.",
                    "- Waardering: bijgewerkt met de slotkoersset van de gevraagde rapportdatum.",
                    "- Onderzoeksstatus: PAVE-versus-GRID, GSG-rolvalidatie en de close-first beoordeling blijven actief; PPA-versus-ITA blijft uitsluitend volglijstonderzoek.",
                    "- Thesiswijzigingen: geen structurele thesis is losgelaten.",
                ]
            )
        return "\n".join(
            [
                "- Portfolio changes: none; share quantities, active tickers and cash were unchanged in this review.",
                "- Valuation: refreshed using the requested report-date closing-price set.",
                "- Research status: PAVE-versus-GRID, GSG role validation and the close-first review remain active; PPA-versus-ITA remains watchlist research only.",
                "- Thesis changes: no structural thesis was abandoned.",
            ]
        )
    return "- Portfolio changes are shown in the authoritative action and position-change tables."


def _normalize_radar_rows(text: str, state: dict[str, Any], language: str) -> str:
    active = active_tickers(state)
    lines: list[str] = []
    in_omitted = False
    for line in text.splitlines():
        plain = _plain(line)
        if "Notable lanes assessed but not promoted" in plain or "Opvallende thema’s beoordeeld" in plain:
            in_omitted = True
        elif in_omitted and line.startswith("## "):
            in_omitted = False

        if line.startswith("|") and "PPA" in plain and "ITA" in plain and ("Defense innovation" in plain or "Defensie-innovatie" in plain):
            cells = line.split("|")
            if len(cells) >= 11:
                if language == "nl":
                    cells[7] = " Niet-aangehouden volglijst "
                    cells[8] = " Vergelijk PPA en ITA als instrumentkandidaten; geen van beide is een huidige positie. "
                else:
                    cells[7] = " Non-held watchlist "
                    cells[8] = " Compare PPA and ITA as vehicle candidates; neither is a current holding. "
                line = "|".join(cells)

        if in_omitted and line.startswith("|") and not line.startswith("|---"):
            cells = line.split("|")
            if len(cells) >= 6:
                primary = _ticker(_plain(cells[2]))
                if primary in active:
                    if language == "nl":
                        cells[3] = " Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend. "
                        cells[4] = " Heroverweeg alleen bij een materiële wijziging in relatieve sterkte, rolvalidatie, concentratie of financieringsbron. "
                    else:
                        cells[3] = " Existing funded position; no additional lane promotion was granted this run. "
                        cells[4] = " Reassess only if relative strength, role validity, concentration or the funding case changes materially. "
                    line = "|".join(cells)
        lines.append(line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _normalize_action_language(text: str, state: dict[str, Any], language: str) -> str:
    if language == "nl":
        replacements = {
            "Negative pnl gt 20": "P/L lager dan -20%",
            "Negative pnl gt 10": "P/L lager dan -10%",
            "Negative pnl gt 5": "P/L lager dan -5%",
            "Loss and sub4 forced reunderwrite": "materieel verlies vereist volledige herbeoordeling",
            "Role impaired": "portefeuillerol verzwakt",
            "Sterker alternatief is beschikbaar voor v…": "Sterker alternatief beschikbaar; volledige PAVE-versus-GRID-review vereist",
            "Portfolio valuation based on confirmed prices and official holdings": "Waardering op basis van bevestigde slotkoersen en officiële posities",
            "Latest portfolio valuation based on confirmed closing prices and current holdings": "Waardering op basis van bevestigde slotkoersen en officiële posities",
            "Runtime valuation repriced from official portfolio-state shares": "Waardering op basis van bevestigde slotkoersen en officiële posities",
        }
    else:
        replacements = {
            "Negative pnl gt 20": "P/L below -20%",
            "Negative pnl gt 10": "P/L below -10%",
            "Negative pnl gt 5": "P/L below -5%",
            "Loss and sub4 forced reunderwrite": "material loss requires full re-underwriting",
            "Role impaired": "portfolio role impaired",
            "Stronger alternative is available for v…": "Stronger alternative available; complete the PAVE-versus-GRID review",
        }
    for old, new in replacements.items():
        text = text.replace(old, new)
    if language == "nl":
        text = text.replace(
            "SPY-relative performance",
            "prestaties tegenover de SPY-marktbenchmark",
        )
        text = text.replace(
            "SPY-relatieve performance",
            "prestaties tegenover de SPY-marktbenchmark",
        )
    else:
        text = text.replace(
            "SPY-relative performance",
            "performance versus the SPY market benchmark",
        )

    spy_link = r"(?:\[SPY\]\([^\)]+\)|SPY)"
    if language == "nl":
        text = re.sub(
            spy_link + r"-relative performance",
            "prestaties tegenover de SPY-marktbenchmark",
            text,
            flags=re.IGNORECASE,
        )
    else:
        text = re.sub(
            spy_link + r"-relative performance",
            "performance versus the SPY market benchmark",
            text,
            flags=re.IGNORECASE,
        )

    text = text.replace(
        "Monitor commodity breadth and hedge contribution after execution.",
        "Monitor commodity breadth and hedge contribution in the current portfolio.",
    )
    text = text.replace(
        "Monitor grondstoffenbreedte en bijdrage aan de hedgefunctie na uitvoering.",
        "Monitor grondstoffenbreedte en bijdrage aan de hedgefunctie in de huidige portefeuille.",
    )
    text = text.replace(
        "A stronger alternative is available for…",
        "A stronger alternative is available; complete the PAVE-versus-GRID review",
    )
    text = text.replace(
        "Sterker alternatief is beschikbaar voor…",
        "Sterker alternatief beschikbaar; rond de PAVE-versus-GRID-review af",
    )
    text = re.sub(
        r"Review has persisted for multiple report cycles;\s*Review has persisted for several report(?: cycles)?…?",
        "Review has persisted for multiple report cycles",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Review loopt al meerdere rapportcycli;\s*Review loopt al meerdere rapport(?:cycli)?…?",
        "Review loopt al meerdere rapportcycli",
        text,
        flags=re.IGNORECASE,
    )
    text = text.replace(
        "- PPA / ITA: Defense spending remains structurally durable, but vehicle selection must be proven.",
        "- PPA / ITA (non-held watchlist comparison): Defense spending remains structurally durable, but vehicle selection must be proven.",
    )
    text = text.replace(
        "- PPA / ITA: Defensie-uitgaven blijven structureel ondersteund, maar ETF-keuze blijft belangrijk.",
        "- PPA / ITA (niet-aangehouden volglijstvergelijking): Defensie-uitgaven blijven structureel ondersteund, maar ETF-keuze blijft belangrijk.",
    )

    duplicate_patterns = [
        r"(Review has persisted for multiple report cycles;\s*)\1+",
        r"(Review has persisted for several report cycles;\s*)\1+",
        r"(Review loopt al meerdere rapportcycli;\s*)\1+",
    ]
    for pattern in duplicate_patterns:
        text = re.sub(pattern, r"\1", text, flags=re.IGNORECASE)

    if _no_action(state):
        text = text.replace(
            "Execution constraint: weekly rotation limit reached",
            "No current-run trade intent; the review remains active",
        )
        text = text.replace(
            "Uitvoeringsbeperking: rotatielimiet bereikt voor deze review",
            "Geen handelsintentie in deze run; de herbeoordeling blijft actief",
        )
    return text


def _normalize_history_and_macro(text: str, state: dict[str, Any], language: str) -> str:
    report_date = _report_date(state)
    fresh = _fresh_pricing(state)
    if report_date and fresh:
        replacement = (
            "Waardering op basis van bevestigde slotkoersen en officiële posities"
            if language == "nl"
            else "Portfolio valuation based on confirmed closing prices and official holdings"
        )
        pattern = re.compile(rf"^(\|\s*{re.escape(report_date)}\s*\|[^\n]*?\|)\s*[^|\n]+\s*\|$", re.MULTILINE)
        text = pattern.sub(lambda match: match.group(1) + f" {replacement} |", text)

    if language == "nl":
        text = re.sub(
            r"Risk-on groei houdt al \d+ wekelijkse meetmomenten aan;",
            "Risk-on groei blijft het huidige regime;",
            text,
        )
        text = text.replace(
            "ECB-houding: Verkrappend / inflatiegevoelig.",
            "ECB-houding: Ongewijzigd na de verkrapping in juni / datagedreven.",
        )
    else:
        text = re.sub(
            r"Risk-on growth has persisted across \d+ weekly observations;",
            "Risk-on growth remains the current regime;",
            text,
        )
        text = text.replace(
            "ECB stance: Tightening / inflation-sensitive.",
            "ECB stance: On hold after June tightening / data-dependent.",
        )
    return text


def apply_report_portfolio_integrity(text: str, state: dict[str, Any], language: str) -> str:
    language = language.lower().strip()
    if language not in {"en", "nl"}:
        raise ValueError(f"Unsupported language: {language}")

    if language == "nl":
        text = _replace_section(text, "## 2A. Besliscockpit", _decision_cockpit(state, language))
        text = _replace_section(text, "## 5. Belangrijkste risico’s / invalidaties", _risk_section(state, language))
        text = _replace_section(text, "## 6. Conclusie", _conclusion_section(state, language))
        text = _replace_section(text, "## 8. Allocatiekaart", _allocation_map(state, language))
        text = _replace_section(text, "## 9. Tweede-orde-effectenkaart", _second_order_map(state, language))
        text = _replace_subsection(text, "### Portefeuilletabel", "### Beschikbare cash", _continuity_table(state, language))
        text = _replace_subsection(text, "### Volglijst / dynamisch radargeheugen", "### Continuïteit in aanbevelingsdiscipline", _watchlist_table(state, language))
        text = _replace_subsection(text, "### Continuïteit in aanbevelingsdiscipline", "### Randvoorwaarden", _discipline_continuity(language))
        text = _replace_subsection(text, "### Wijzigingen sinds de vorige review", "## 17. Disclaimer", _changes_summary(state, language))
    else:
        text = _replace_section(text, "## 2A. Decision cockpit", _decision_cockpit(state, language))
        text = _replace_section(text, "## 5. Key Risks / Invalidators", _risk_section(state, language))
        text = _replace_section(text, "## 6. Bottom Line", _conclusion_section(state, language))
        text = _replace_section(text, "## 8. Asset Allocation Map", _allocation_map(state, language))
        text = _replace_section(text, "## 9. Second-Order Effects Map", _second_order_map(state, language))
        text = _replace_subsection(text, "### Portfolio table", "### Available cash", _continuity_table(state, language))
        text = _replace_subsection(text, "### Watchlist / dynamic radar memory", "### Recommendation discipline continuity", _watchlist_table(state, language))
        text = _replace_subsection(text, "### Recommendation discipline continuity", "### Constraints", _discipline_continuity(language))
        text = _replace_subsection(text, "### Changes since last review", "## 17. Disclaimer", _changes_summary(state, language))

    text = _normalize_radar_rows(text, state, language)
    text = _normalize_action_language(text, state, language)
    text = _normalize_history_and_macro(text, state, language)
    validate_report_portfolio_integrity(text, state, language)
    return text


def _continuity_section(text: str, language: str) -> str:
    heading = "### Portefeuilletabel" if language == "nl" else "### Portfolio table"
    end_heading = "### Beschikbare cash" if language == "nl" else "### Available cash"
    start = text.find(heading)
    end = text.find(end_heading, start + len(heading)) if start != -1 else -1
    if start == -1 or end == -1:
        return ""
    return text[start:end]


def validate_report_portfolio_integrity(text: str, state: dict[str, Any], language: str) -> None:
    errors: list[str] = []
    active = active_tickers(state)
    plain = _plain(text)
    lower = plain.lower()

    targeted_headings = (
        ["## 2A. Besliscockpit", "## 5. Belangrijkste risico’s / invalidaties", "## 6. Conclusie", "## 10. Review huidige posities", "## 12. Rotatieplan portefeuille", "## 13. Definitieve actietabel", "## 14. Positiewijzigingen in deze run"]
        if language == "nl"
        else ["## 2A. Decision cockpit", "## 5. Key Risks / Invalidators", "## 6. Bottom Line", "## 10. Current Position Review", "## 12. Portfolio Rotation Plan", "## 13. Final Action Table", "## 14. Position Changes Executed This Run"]
    )
    for heading in targeted_headings:
        section = _plain(_section(text, heading)).lower()
        if "PPA" not in active and "ppa" in section and "non-held" not in section and "niet-aangehouden" not in section:
            errors.append(f"non_held_ppa_current_position_language:{heading}")
        if "SPY" not in active and "spy" in section and "benchmark" not in section:
            errors.append(f"non_held_spy_current_position_language:{heading}")

    forbidden = [
        "ppa and pave remain replaceable",
        "ppa en pave blijven vervangbaar",
        "keep spy under review",
        "houd spy onder herbeoordeling",
        "spy plus smh creates",
        "spy plus smh creëert",
        "ppa must justify itself",
        "ppa moet zich bewijzen",
        "runtime-rendered markdown generation layer",
        "gevalideerd productiepad op basis van expliciete portefeuillestaat",
        "negative pnl gt",
        "loss and sub4 forced reunderwrite",
        "weekly observations",
        "wekelijkse meetmomenten",
        "doorgeschoven waardering",
        "carried-forward valuation",
    ]
    for phrase in forbidden:
        if phrase in lower:
            errors.append(f"stale_or_internal_phrase:{phrase}")

    report_date = _report_date(state)
    try:
        after_ecb_hold = bool(report_date and date.fromisoformat(report_date) >= date(2026, 7, 23))
    except ValueError:
        after_ecb_hold = False
    if after_ecb_hold and ("tightening / inflation-sensitive" in lower or "verkrappend / inflatiegevoelig" in lower):
        errors.append("stale_ecb_stance_after_2026_07_23_hold")

    if _fresh_pricing(state):
        latest_line = next((line for line in text.splitlines() if report_date and line.strip().startswith(f"| {report_date} |")), "")
        if not latest_line or ("confirmed" not in latest_line.lower() and "bevestigde" not in latest_line.lower()):
            errors.append("fresh_pricing_latest_history_comment_not_confirmed")

    continuity = _plain(_continuity_section(text, language))
    metrics = _basis_metrics(state)
    for ticker in active:
        if ticker not in continuity:
            errors.append(f"continuity_missing_active_ticker:{ticker}")
            continue
        expected = metrics.get(ticker, {}).get("pnl_pct")
        if expected is not None and f"{float(expected):.2f}" not in continuity:
            errors.append(f"continuity_pnl_not_attribution_aligned:{ticker}")

    if _no_action(state):
        section12 = _plain(_section(text, "## 12. Rotatieplan portefeuille" if language == "nl" else "## 12. Portfolio Rotation Plan")).lower()
        section14 = _plain(_section(text, "## 14. Positiewijzigingen in deze run" if language == "nl" else "## 14. Position Changes Executed This Run")).lower()
        if "dfen" in section12 or "ppa" in section12 or "add from rotation" in section12 or "toevoegen uit rotatie" in section12:
            errors.append("zero_action_rotation_plan_contains_new_ticker")
        if "proposed" in section14 and "no proposed" not in section14 and "geen voorgestelde" not in section14:
            errors.append("zero_action_position_changes_contains_proposal")
        if "rotation limit reached" in lower or "rotatielimiet bereikt" in lower:
            errors.append("zero_action_claims_consumed_rotation_limit")

    if language == "nl":
        for phrase in ("portfolio valuation based on", "negative pnl", "loss and sub4", "current holding under"):
            if phrase in lower:
                errors.append(f"unlocalized_dutch_phrase:{phrase}")

    if "PPA" not in active:
        watchlist = _plain(_section(text, "## 4. Structurele kansenradar" if language == "nl" else "## 4. Structural Opportunity Radar")).lower()
        if "ppa" in watchlist and "non-held" not in watchlist and "niet-aangehouden" not in watchlist:
            errors.append("ppa_watchlist_not_explicitly_non_held")

    if errors:
        raise ReportPortfolioIntegrityError(
            "ETF report portfolio-integrity validation failed: " + "; ".join(sorted(set(errors)))
        )
