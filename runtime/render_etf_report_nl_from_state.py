from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable

from runtime.nl_dates import format_dutch_report_date
from runtime.replacement_duel_v2 import replacement_duel_v2_markdown

ETF_NAMES = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "SMH": "VanEck Semiconductor ETF",
    "PPA": "Invesco Aerospace & Defense ETF",
    "PAVE": "Global X U.S. Infrastructure Development ETF",
    "URNM": "Sprott Uranium Miners ETF",
    "GLD": "SPDR Gold Shares",
}

VALUATION_HISTORY_PATH = Path("output/etf_valuation_history.csv")

ROLE_NL = {
    "Core beta": "Kernbeta",
    "Growth engine": "Groeimotor",
    "Resilience": "Weerbaarheid",
    "Real-asset capex": "Reële activa / capex",
    "Strategic energy": "Strategische energie",
    "Hedge ballast": "Hedgepositie",
    "Position": "Positie",
}

THESIS_NL = {
    "Core U.S. large-cap exposure": "Amerikaanse large-cap kernblootstelling",
    "Core US large-cap exposure": "Amerikaanse large-cap kernblootstelling",
    "AI compute / semiconductor leadership": "AI-rekenkracht en semiconductorleiderschap",
    "Defense and sovereign resilience": "Defensie en strategische weerbaarheid",
    "Grid and infrastructure capex": "Netwerk- en infrastructuurcapex",
    "Nuclear and uranium cycle exposure": "Kernenergie- en uraniumcyclus",
    "Hard-asset geopolitical and inflation hedge": "Reële activa / geopolitieke en inflatiehedge",
}

ACTION_NL = {
    "Hold": "Aanhouden",
    "Add": "Toevoegen",
    "Reduce": "Verlagen",
    "Close": "Sluiten",
    "Sell": "Verkopen",
    "Buy": "Kopen",
    "Hold under review": "Aanhouden, onder herbeoordeling",
    "Hold but replaceable": "Aanhouden, maar vervangbaar",
}

FRESH_CASH_NL = {
    "Yes": "Ja",
    "No": "Nee",
    "Smaller": "Kleiner",
    "Smaller / under review": "Kleiner / onder herbeoordeling",
    "Hold": "Aanhouden",
    "Reduce": "Verlagen",
}

LANE_NL = {
    "AI compute infrastructure": "AI-rekenkrachtinfrastructuur",
    "AI Infrastructure": "AI-rekenkrachtinfrastructuur",
    "Cybersecurity resilience": "Cybersecurityweerbaarheid",
    "Grid buildout / electrification": "Netuitbreiding / elektrificatie",
    "Grid Electrification": "Netuitbreiding / elektrificatie",
    "Broad commodity inflation hedge": "Brede grondstoffen-inflatiehedge",
    "Industrial automation and factory software": "Industriële automatisering en fabriekssoftware",
    "Robotics / automation": "Robotica / automatisering",
    "Agricultural commodities": "Agrarische grondstoffen",
    "Food security / agriculture inputs": "Voedselzekerheid / landbouwinputs",
    "Water infrastructure / treatment": "Waterinfrastructuur / waterbehandeling",
    "Critical minerals / copper / refining": "Kritieke mineralen / koper / raffinage",
    "Copper and electrification materials": "Koper en elektrificatiematerialen",
    "Biotech innovation / therapeutic platforms": "Biotechinnovatie / therapeutische platforms",
    "Nuclear utilities and clean baseload": "Nucleaire nutsbedrijven en schone basislast",
    "Defense innovation / sovereign resilience": "Defensie-innovatie / strategische weerbaarheid",
    "Gold hedge review": "Herbeoordeling goudhedge",
    "Non-U.S. developed diversification": "Ontwikkelde markten buiten de VS",
    "India Industrialization": "Industrialisatie India",
    "Uranium and Nuclear": "Uranium en kernenergie",
    "Critical Minerals": "Kritieke mineralen",
    "Defense Resilience": "Defensieveerbaarheid",
}

POSITION_SHORT_REASON_NL = {
    "SPY": "Nuttig als kernblootstelling, maar de overlap met SMH blijft expliciet onder herbeoordeling.",
    "SMH": "Best onderbouwde groeiblootstelling; uitbreiding blijft begrensd door de maximale positiegrootte.",
    "PPA": "Structurele defensiecase blijft valide, maar de ETF-implementatie moet zich bewijzen tegenover ITA.",
    "PAVE": "Infrastructuurcase blijft valide, maar GRID is de scherpste vervangingskandidaat.",
    "URNM": "Strategische energiecase blijft valide, maar krijgt deze run geen extra kapitaal boven SMH.",
    "GLD": "Hedgefunctie staat onder herbeoordeling na de forse drawdown.",
}

POSITION_NEXT_ACTION_NL = {
    "SPY": "Toets overlap met SMH voordat extra kapitaal wordt toegewezen.",
    "SMH": "Aanhouden binnen de maximale positiegrootte en opnieuw toetsen op concentratie.",
    "PPA": "Voer de vervangingsanalyse tegenover ITA opnieuw uit.",
    "PAVE": "Voer de vervangingsanalyse tegenover GRID opnieuw uit.",
    "URNM": "Aanhouden en vergelijken met URA/NLR als uraniumbreedte verbetert.",
    "GLD": "Voer de hedge-validiteitstest opnieuw uit tegenover GSG en BIL.",
}


def f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def f4(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return ""


def pct(value: Any, signed: bool = False) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n.v.t."
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.2f}%"


def text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw if raw else fallback


def ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def short(value: Any, fallback: str = "", max_len: int = 145) -> str:
    raw = text(value, fallback)
    return raw if len(raw) <= max_len else raw[: max_len - 1].rstrip() + "…"


def position_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state.get("positions", []) or [])


def cash_eur(state: dict[str, Any]) -> float:
    return float((state.get("portfolio") or {}).get("cash_eur") or 0.0)


def invested_eur(state: dict[str, Any]) -> float:
    return round(sum(float(p.get("previous_market_value_eur") or 0.0) for p in position_rows(state)), 2)


def total_nav(state: dict[str, Any]) -> float:
    return round(invested_eur(state) + cash_eur(state), 2)


def weights(state: dict[str, Any]) -> dict[str, float]:
    nav = total_nav(state) or 1.0
    return {
        ticker(p.get("ticker")): round(float(p.get("previous_market_value_eur") or 0.0) / nav * 100.0, 2)
        for p in position_rows(state)
    }


def eurusd_used(state: dict[str, Any]) -> str:
    return f4((state.get("fx_basis") or {}).get("rate")) or "0.0000"


def nl_role(value: Any) -> str:
    return ROLE_NL.get(text(value), text(value, "Positie"))


def nl_thesis(value: Any, ticker_value: str = "") -> str:
    raw = text(value)
    if raw in THESIS_NL:
        return THESIS_NL[raw]
    fallback = {
        "SPY": "Amerikaanse large-cap kernblootstelling",
        "SMH": "AI-rekenkracht en semiconductorleiderschap",
        "PPA": "Defensie en strategische weerbaarheid",
        "PAVE": "Netwerk- en infrastructuurcapex",
        "URNM": "Kernenergie- en uraniumcyclus",
        "GLD": "Reële activa / geopolitieke en inflatiehedge",
    }.get(ticker_value)
    return fallback or raw or "Portefeuilleblootstelling"


def nl_action(value: Any) -> str:
    raw = text(value, "Hold")
    if raw in ACTION_NL:
        return ACTION_NL[raw]
    low = raw.lower()
    if "add" in low or "buy" in low:
        return "Toevoegen"
    if "reduce" in low:
        return "Verlagen"
    if "close" in low or "sell" in low:
        return "Sluiten"
    if "review" in low:
        return "Aanhouden, onder herbeoordeling"
    return "Aanhouden"


def nl_existing(value: Any) -> str:
    return "Bestaand" if text(value, "Existing").lower() == "existing" else "Nieuw"


def nl_yes_no(value: Any) -> str:
    raw = text(value, "No").lower()
    return "Ja" if raw in {"yes", "ja", "true", "1"} else "Nee"


def nl_fresh_cash(value: Any) -> str:
    raw = text(value, "")
    if raw in FRESH_CASH_NL:
        return FRESH_CASH_NL[raw]
    low = raw.lower()
    if "review" in low:
        return "Kleiner / onder herbeoordeling"
    if "reduce" in low:
        return "Verlagen"
    if "hold" in low:
        return "Aanhouden"
    return raw or "Onder herbeoordeling"


def lane_name_nl(value: Any) -> str:
    raw = text(value, "Thema")
    return LANE_NL.get(raw, raw)


def promoted_lanes(state: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = state.get("lane_assessment", {}).get("assessed_lanes", []) or []
    return [lane for lane in lanes if lane.get("promoted_to_live_radar") is True][:8]


def omitted_lanes(state: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = state.get("lane_assessment", {}).get("assessed_lanes", []) or []
    return [lane for lane in lanes if lane.get("promoted_to_live_radar") is not True][:6]


def lane_summary_nl(lane: dict[str, Any]) -> str:
    name = lane_name_nl(lane.get("lane_name"))
    primary = ticker(lane.get("primary_etf"))
    if "AI" in name or primary in {"SMH", "SOXX"}:
        return "AI-rekenkracht en semiconductor-capex blijven de sterkste structurele groeibronnen."
    if "Cyber" in name:
        return "Cybersecurity-uitgaven profiteren van AI, cloud, datacenters en geopolitieke weerbaarheid."
    if "Net" in name or primary in {"PAVE", "GRID"}:
        return "Stroomvraag, netcongestie en reshoring ondersteunen infrastructuurinvesteringen."
    if "grondstoffen" in name or primary in {"GSG", "DBC", "DBA", "CORN"}:
        return "Grondstoffen kunnen inflatie- en aanbodrisico’s diversifiëren, mits prijsbreedte bevestigt."
    if "Defensie" in name or primary in {"PPA", "ITA"}:
        return "Defensie-uitgaven blijven structureel ondersteund, maar ETF-keuze blijft belangrijk."
    if "uranium" in name.lower() or "kern" in name.lower() or primary in {"URNM", "URA", "NLR"}:
        return "Energiezekerheid en nucleaire basislast blijven strategisch relevant."
    if "India" in name:
        return "Binnenlandse groei en industrialisatie ondersteunen de structurele case."
    return f"{name} blijft relevant, maar vraagt om bevestiging in prijs, timing en portefeuillefit."


def lane_need_nl(lane: dict[str, Any]) -> str:
    primary = ticker(lane.get("primary_etf"))
    alt = ticker(lane.get("alternative_etf"))
    if primary == "SMH":
        return "Aanhoudend leiderschap, maar met positiegrootte- en concentratiediscipline."
    if primary == "PAVE" or alt == "GRID":
        return "Bevestiging dat GRID structureel beter past dan PAVE."
    if primary in {"GSG", "DBC", "DBA", "CORN"}:
        return "Bredere grondstoffenbevestiging voordat kapitaal wordt toegewezen."
    if primary in {"PPA", "ITA"}:
        return "Duidelijkere ETF-implementatie en relatieve sterkte tegenover defensiealternatieven."
    return "Sterkere relatieve sterkte en duidelijke aansluiting op de beleggingscase."


def radar_table_nl(state: dict[str, Any]) -> str:
    lines = [
        "| Thema | Primaire ETF | Alternatieve ETF | Waarom relevant | Structurele aansluiting | Macro-timing | Status | Benodigde bevestiging | Tijdshorizon |",
        "|---|---|---|---|---:|---:|---|---|---|",
    ]
    for lane in promoted_lanes(state):
        score = float(lane.get("total_score") or 0.0)
        status = "Actiegericht" if score >= 4.5 else "Volglijst / onder herbeoordeling"
        lines.append(
            f"| {lane_name_nl(lane.get('lane_name'))} | {ticker(lane.get('primary_etf')) or 'Geen'} | {ticker(lane.get('alternative_etf')) or 'Geen'} | "
            f"{lane_summary_nl(lane)} | {lane.get('structural_strength', '')} | {lane.get('macro_alignment', '')} | "
            f"{status} | {lane_need_nl(lane)} | 3-12 maanden |"
        )
    return "\n".join(lines)


def omitted_table_nl(state: dict[str, Any]) -> str:
    lines = [
        "| Thema | Primaire ETF | Waarom niet gepromoveerd | Wat dat zou veranderen |",
        "|---|---|---|---|",
    ]
    for lane in omitted_lanes(state):
        primary = ticker(lane.get("primary_etf"))
        reason = "Scoorde lager dan sterkere gefinancierde posities en alternatieven."
        if lane.get("direct_rs_vs_holding_3m_pct") is not None:
            reason = "Relatieve sterkte tegenover de relevante huidige positie is nog onvoldoende overtuigend."
        lines.append(
            f"| {lane_name_nl(lane.get('lane_name'))} | {primary or 'Geen'} | {reason} | {lane_need_nl(lane)} |"
        )
    return "\n".join(lines)


def short_radar_nl() -> str:
    return "\n".join([
        "| Shortthema | Kandidaat-ETF | Shortthese | Trigger | Invalidering | Tijdshorizon | Vertrouwen |",
        "|---|---|---|---|---|---|---|",
        "| Rentegevoelige small-caps | IWM | Restrictieve reële rentes zetten zwakkere balansen onder druk. | IWM verzwakt verder tegenover SPY terwijl rentes stevig blijven. | Duidelijke renteontspanning en betere kredietbreedte. | 1-3 maanden | Gemiddeld |",
        "| Chinese platformbeta | KWEB | Beleidsvertrouwen blijft kwetsbaar. | Mislukte rally of hernieuwde valuta-/beleidsstress. | Duurzame stimulans en winstherstel. | 1-3 maanden | Gemiddeld |",
        "| Langlopende obligaties | TLT | Hardnekkige inflatie en reëlerenterisico blijven tegenwind. | Reële rentes stijgen opnieuw. | Groeischrik en duidelijke neerwaartse rente-uitbraak. | 1-3 maanden | Gemiddeld |",
        "| Speculatieve cleantechbeta | ICLN | Financieringsdruk en zwakke winstgevendheid blijven knelpunten. | Geen herstel in een brede risk-on-markt. | Scherpe rentedaling of grote beleidsverrassing. | 3-12 maanden | Gemiddeld |",
    ])


def section15_table_nl(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | Aantal aandelen | Prijs lokaal | Valuta | Marktwaarde lokaal | Marktwaarde EUR | Gewicht % |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for p in position_rows(state):
        t = ticker(p.get("ticker"))
        lines.append(f"| {t} | {f2(p.get('shares'))} | {f2(p.get('previous_price_local'))} | {p.get('currency', 'USD')} | {f2(p.get('previous_market_value_local'))} | {f2(p.get('previous_market_value_eur'))} | {f2(w.get(t))} |")
    cash_pct = cash_eur(state) / (total_nav(state) or 1.0) * 100.0
    lines.append(f"| CASH | - | 1.00 | EUR | {f2(cash_eur(state))} | {f2(cash_eur(state))} | {f2(cash_pct)} |")
    return "\n".join(lines)


def valuation_history_points(state: dict[str, Any], history_path: Path = VALUATION_HISTORY_PATH) -> list[dict[str, Any]]:
    points: dict[str, dict[str, Any]] = {}
    if history_path.exists():
        with history_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                date = text(row.get("date"))
                try:
                    nav = float(row.get("nav_eur") or 0.0)
                except ValueError:
                    continue
                if date and nav:
                    points[date] = {"date": date, "nav_eur": round(nav, 2), "comment": nl_history_comment(row.get("comment"))}
    report_date = text(state.get("report_date"))
    if report_date:
        points[report_date] = {"date": report_date, "nav_eur": total_nav(state), "comment": "Doorgeschoven waardering uit prijsaudit en expliciete portefeuillestaat"}
    return [points[d] for d in sorted(points)]


def nl_history_comment(value: Any) -> str:
    raw = text(value)
    mapping = {
        "Inaugural model portfolio established": "Initiële modelportefeuille vastgesteld",
        "Fresh per-ticker repricing using latest completed close set": "Verse herprijzing per ticker op basis van de meest recente volledige slotkoersset",
        "Fresh six-of-six repricing using completed 20 April close set": "Verse herprijzing voor zes van zes posities op basis van de volledige slotkoersset van 20 april",
        "Fresh five-of-six repricing; PPA carried forward": "Verse herprijzing voor vijf van zes posities; PPA doorgeschoven",
        "Fresh six-of-six repricing using persisted 2026-04-29 audit": "Verse herprijzing voor zes van zes posities op basis van de vastgelegde prijsaudit van 2026-04-29",
        "Fresh five-of-six pricing recovery; GLD carried forward": "Prijsherstel voor vijf van zes posities; GLD doorgeschoven",
        "Latest 4 May close basis; +8 SMH executed from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH uitgevoerd vanuit cash",
    }
    return mapping.get(raw, raw or "Historisch waarderingspunt")


def section7_table_nl(state: dict[str, Any]) -> str:
    lines = ["| Datum | Portefeuillewaarde EUR | Opmerking |", "|---|---:|---|"]
    for point in valuation_history_points(state):
        lines.append(f"| {point['date']} | {float(point['nav_eur']):.2f} | {point.get('comment', '')} |")
    return "\n".join(lines)


def action_tickers(state: dict[str, Any], predicate: Callable[[str, dict[str, Any]], bool]) -> str:
    tickers = [ticker(p.get("ticker")) for p in position_rows(state) if predicate(text(p.get("suggested_action")), p)]
    return ", ".join(tickers) if tickers else "Geen"


def current_position_table_nl(state: dict[str, Any]) -> str:
    lines = [
        "| Ticker | Actie | Score | Nieuw-kapitaaltoets | Rol | Volgende toets |",
        "|---|---|---:|---|---|---|",
    ]
    for p in position_rows(state):
        t = ticker(p.get("ticker"))
        lines.append(f"| {t} | {nl_action(p.get('suggested_action'))} | {f2(p.get('total_score'))} | {nl_fresh_cash(p.get('fresh_cash_test'))} | {nl_role(p.get('portfolio_role'))} | {POSITION_NEXT_ACTION_NL.get(t, 'Aanhouden en opnieuw toetsen in de volgende run.')} |")
    return "\n".join(lines)


def final_action_table_nl(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | ETF | Bestaand/nieuw | Vorig gewicht | Doelgewicht | Advies | Convictieniveau | Totaalscore | Portefeuillerol | Sterker alternatief? | Korte toelichting |",
        "|---|---|---|---:|---:|---|---|---:|---|---|---|",
    ]
    for p in position_rows(state):
        t = ticker(p.get("ticker"))
        lines.append(f"| {t} | {ETF_NAMES.get(t, t)} | {nl_existing(p.get('existing_new'))} | {f2(p.get('weight_inherited_pct') or p.get('previous_weight_pct'))} | {f2(p.get('target_weight_pct') or w.get(t))} | {nl_action(p.get('suggested_action'))} | {text(p.get('conviction_tier')).replace('Tier', 'Niveau')} | {f2(p.get('total_score'))} | {nl_role(p.get('portfolio_role'))} | {nl_yes_no(p.get('better_alternative_exists'))} | {POSITION_SHORT_REASON_NL.get(t, 'Geen materiële wijziging deze run.')} |")
    return "\n".join(lines)


def position_changes_table_nl(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | Vorig gewicht % | Nieuw gewicht % | Gewichtswijziging % | Wijziging aantal stukken | Uitgevoerde actie | Financieringsbron / toelichting |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for p in position_rows(state):
        t = ticker(p.get("ticker"))
        prev = float(p.get("previous_weight_pct") or p.get("current_weight_pct") or 0.0)
        new = w.get(t, prev)
        executed = nl_action(p.get("action_executed_this_run")) if text(p.get("action_executed_this_run"), "None") != "None" else "Geen"
        note = {
            "SPY": "Aanhouden; overlapreview tegenover SMH.",
            "SMH": "Gefinancierd uit cash; blijft onder de maximale positiegrootte.",
            "PPA": "Aanhouden, onder herbeoordeling; volgende run vergelijken met ITA.",
            "PAVE": "Aanhouden, onder herbeoordeling; volgende run vergelijken met GRID.",
            "URNM": "Aanhouden; deze run niet beter dan SMH voor cash.",
            "GLD": "Aanhouden, onder hedge-validiteitsreview.",
        }.get(t, "Geen materiële wijziging.")
        lines.append(f"| {t} | {prev:.2f} | {new:.2f} | {new - prev:.2f} | {f2(p.get('shares_delta_this_run'))} | {executed} | {note} |")
    cash_pct = cash_eur(state) / (total_nav(state) or 1.0) * 100.0
    lines.append(f"| CASH | - | {cash_pct:.2f} | - | 0.00 | Geen | Resterende cash |")
    return "\n".join(lines)


def rotation_plan_table_nl(state: dict[str, Any]) -> str:
    close = action_tickers(state, lambda action, p: "close" in action.lower() or "sell" in action.lower())
    reduce = action_tickers(state, lambda action, p: "reduce" in action.lower())
    hold = action_tickers(state, lambda action, p: "hold" in action.lower())
    add = action_tickers(state, lambda action, p: "add" in action.lower() or "buy" in text(p.get("action_executed_this_run")).lower())
    replace = action_tickers(state, lambda action, p: nl_yes_no(p.get("better_alternative_exists")) == "Ja" and ("review" in action.lower() or "hold" in action.lower()))
    return "\n".join(["| Sluiten | Verlagen | Aanhouden | Toevoegen | Vervangen |", "|---|---|---|---|---|", f"| {close} | {reduce} | {hold} | {add} | {replace} |"])


def continuity_table_nl(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | ETF-naam | Richting | Gewicht % | Gem. instap | Huidige prijs | P/L % | Oorspronkelijke thesis | Rol |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for p in position_rows(state):
        t = ticker(p.get("ticker"))
        direction = "Long" if text(p.get("direction"), "Long").lower() == "long" else text(p.get("direction"))
        lines.append(f"| {t} | {ETF_NAMES.get(t, t)} | {direction} | {f2(w.get(t))} | {f2(p.get('avg_entry_local'))} | {f2(p.get('previous_price_local'))} | {f2(p.get('pnl_pct'))} | {nl_thesis(p.get('original_thesis'), t)} | {nl_role(p.get('portfolio_role'))} |")
    return "\n".join(lines)


def watchlist_table_nl() -> str:
    return "\n".join([
        "| Thema | Primaire ETF | Alternatieve ETF | Waarom op de radar | Status |",
        "|---|---|---|---|---|",
        "| AI-rekenkrachtinfrastructuur | SMH | SOXX | Sterkste structurele groeiblootstelling. | Actief |",
        "| Defensie-innovatie / strategische weerbaarheid | PPA | ITA | Defensiethesis is valide, maar ETF-implementatie staat onder herbeoordeling. | Vervangingsanalyse vereist |",
        "| Netuitbreiding / elektrificatie | PAVE | GRID | Infrastructuurcapex blijft valide. | Vervangingsanalyse vereist |",
        "| Herbeoordeling goudhedge | GLD | GSG / BIL | Hedgefunctie moet worden bewezen. | Onder herbeoordeling |",
        "| Ontwikkelde markten buiten de VS | IEFA | EFA | De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS. | Volglijst |",
    ])


def asset_allocation_map_nl() -> str:
    return "\n".join([
        "| Segment | Positionering | Toelichting |",
        "|---|---|---|",
        "| Amerikaanse aandelen | Neutraal | Belegbaar, maar concentratierisico is expliciet aanwezig. |",
        "| Europese aandelen | Neutraal | Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof. |",
        "| Opkomende markten | Onderwogen | USD- en oliegevoeligheid blijven tegenwind. |",
        "| Large-cap | Neutraal | Kwaliteitsleiderschap werkt nog steeds. |",
        "| Small-cap | Onderwogen | Rentes en herfinanciering blijven lastig. |",
        "| Groei | Neutraal | Selectieve groei onder leiding van SMH blijft aantrekkelijk. |",
        "| Kwaliteit | Overwogen | Winstbestendigheid blijft waardevol. |",
        "| Goud | Neutraal | Hedgerol onder herbeoordeling. |",
        "| Industrie / defensie | Overwogen | Structurele thesis is valide; ETF-implementatie onder herbeoordeling. |",
        "| Niet-USD activa | Volglijst | Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht. |",
    ])


def second_order_map_nl() -> str:
    return "\n".join([
        "| Drijver | Eerste-orde-effect | Tweede-orde-effect | Waarschijnlijke winnaars | Kwetsbare segmenten | ETF-implicatie | Timing | Vertrouwen |",
        "|---|---|---|---|---|---|---|---|",
        "| AI-leiderschap | SMH blijft de zuiverste groeiblootstelling | Concentratie moet worden bewaakt | SMH, SOXX | Cyclische waarden van lagere kwaliteit | Aanhouden rond maximale positiegrootte | Direct | Hoog |",
        "| Factorconcentratie | SPY en SMH overlappen | De portefeuille is minder gediversifieerd dan het aantal tickers suggereert | QUAL, IEFA op de volglijst | Overlappende Amerikaanse beta | Houd SPY onder herbeoordeling | 1-3 maanden | Gemiddeld |",
        "| Defensiethesis versus ETF-implementatie | Defensie blijft structureel valide | PPA moet zich bewijzen tegenover ITA | ITA, PPA | Zwakke ETF-selectie | Houd PPA onder herbeoordeling | Direct | Gemiddeld |",
        "| Hedgedrawdown | GLD moet zijn hedgefunctie bewijzen | GSG en BIL blijven alternatieven | GSG, BIL, cash | Onproductieve hedgepositie | Houd GLD onder herbeoordeling | Direct | Gemiddeld |",
    ])


def best_opportunities_nl(state: dict[str, Any]) -> str:
    lines = [
        "- SMH blijft de leidende gefinancierde groeiblootstelling, begrensd door de maximale positiegrootte.",
    ]
    for lane in promoted_lanes(state)[:3]:
        primary = ticker(lane.get("primary_etf"))
        alt = ticker(lane.get("alternative_etf"))
        if primary and primary != "SMH":
            pair = f"{primary} / {alt}" if alt else primary
            lines.append(f"- {pair}: {lane_summary_nl(lane)}")
    lines.append("- Vervangingskandidaten blijven afhankelijk van bewijs: prijsbasis, relatieve sterkte en aansluiting op de beleggingscase moeten zichtbaar zijn vóór allocatie.")
    return "\n".join(lines)


def render_nl_native(state: dict[str, Any]) -> str:
    report_date = text(state.get("report_date"), "unknown")
    nav = total_nav(state)
    inv = invested_eur(state)
    cash = cash_eur(state)
    eurusd = eurusd_used(state)
    holdings = ", ".join(ticker(p.get("ticker")) for p in position_rows(state))
    add = action_tickers(state, lambda action, p: "add" in action.lower() or "buy" in text(p.get("action_executed_this_run")).lower())
    review = action_tickers(state, lambda action, p: nl_yes_no(p.get("better_alternative_exists")) == "Ja" or "review" in action.lower())
    return f"""# Wekelijkse ETF-review {format_dutch_report_date(report_date) if report_date != 'unknown' else report_date}

> *Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde.*

## 1. Kernsamenvatting

- **Primair regime:** Risk-on met smal marktleiderschap.
- **Geopolitiek regime:** Gemengd / nog niet doorslaggevend.
- **Wat is er deze week veranderd:** Macro-, beleids- en regime-input worden meegenomen in de beoordeling, maar alleen de belangrijkste beslissignalen worden getoond.
- **Algemeen portefeuilleoordeel:** Laat de huidige portefeuille voorlopig intact, maar behandel SPY, PPA, PAVE en GLD als posities onder actieve herbeoordeling.
- **Belangrijkste conclusie:** SMH blijft de best onderbouwde kernpositie, maar nieuw kapitaal en vervangingsbeslissingen moeten koersbevestiging, relatieve sterkte en macrosteun doorstaan.

## 2. Portefeuille-acties

| Advies | Tickers / toelichting |
|---|---|
| Toevoegen | {add} |
| Aanhouden | {holdings} |
| Aanhouden, maar vervangbaar | {review} blijven expliciet onder herbeoordeling. |
| Verlagen | Geen |
| Sluiten | Geen |

### Beste alternatieven om te financieren
- Nog geen alternatief is sterk genoeg om direct te financieren. Elk genoemd alternatief moet eerst dezelfde prijsbasis, relatieve-sterkteanalyse en beleggingscase-toets doorstaan.

## 3. Regime-dashboard

### Regimesamenvatting
- Huidig regime: Risk-on met smal marktleiderschap.
- Vertrouwen: 72%.
- Beslisregel: Macro ondersteunt selectiediscipline, niet standaard brede risico-uitbreiding.

### Wat veranderde
- AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.
- Het gedrag van goud als hedge blijft onder herbeoordeling en is geen automatische stabilisator.

### Portefeuille-implicaties
- SMH blijft de best onderbouwde kernpositie, maar smal marktleiderschap mag niet worden verward met brede portefeuillediversificatie.
- Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, PPA en PAVE expliciet worden getoetst aan hun belangrijkste vervangingskandidaten.
- Behoud kasdiscipline, omdat het regime selectiviteit sterker ondersteunt dan brede risico-uitbreiding.

### Beleidscatalysatoren in het rapport
- AI-infrastructuur en semiconductorketens: kapitaaluitgaven en strategisch toeleveringsketenbeleid ondersteunen semiconductor- en infrastructuurthema’s.
- Defensie en strategische weerbaarheid: defensiebudgetten blijven structureel steunend, maar ETF-implementatie blijft bepalend.

## 4. Structurele kansenradar

{radar_table_nl(state)}

### Beste structurele kansen die nog niet actiegericht zijn
- Voedselzekerheid / landbouwinputs
- Waterinfrastructuur / waterbehandeling
- Kritieke mineralen / koper / raffinage

### Opvallende thema’s beoordeeld, maar deze week niet gepromoveerd

{omitted_table_nl(state)}

## 4A. Shortkansenradar

{short_radar_nl()}

## 5. Belangrijkste risico’s / invalidaties

- SPY plus SMH creëert hoge Amerikaanse tech-/AI-factoroverlap.
- GLD blijft een hedgepositie onder herbeoordeling en is geen vanzelfsprekende stabilisator.
- PPA en PAVE blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.
- Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.

## 6. Conclusie

- **Portefeuillehouding:** SMH blijft de best onderbouwde kernpositie, maar smal marktleiderschap mag niet worden verward met brede portefeuillediversificatie.
- **Best onderbouwde blootstelling:** SMH blijft de sterkste bijdrage in de portefeuille en de zuiverste structurele groeiblootstelling.
- **Belangrijkste disciplinepunt:** Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, PPA en PAVE expliciet worden getoetst aan hun belangrijkste vervangingskandidaten.
- **Zwakste implementatievragen:** PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en GLD moet bewijzen dat het nog steeds een stabiliserende hedgefunctie heeft.

## 7. Portefeuillecurve en portefeuilleontwikkeling

- Startkapitaal (EUR): 100000.00
- Huidige portefeuillewaarde (EUR): {nav:.2f}
- Rendement sinds start (%): {(nav / 100000.0 - 1.0) * 100.0:.2f}
- Status portefeuillecurve: aangesloten op sectie 15 met volledige waarderingshistorie
- EUR/USD gebruikt: {eurusd}
- Toelichting: Sectie 7 gebruikt de volledige waarderingshistorie plus de actuele portefeuillewaarde; sectie 15 wordt uit dezelfde genormaliseerde portefeuillestaat opgebouwd.

{section7_table_nl(state)}

`EQUITY_CURVE_CHART_PLACEHOLDER`

## 8. Allocatiekaart

{asset_allocation_map_nl()}

## 9. Tweede-orde-effectenkaart

{second_order_map_nl()}

## 10. Review huidige posities

De positiereview scheidt drie vragen: is de thesis nog geldig, is de ETF nog het juiste instrument, en zou nieuw kapitaal dit vandaag nog kopen op het huidige gewicht?

{current_position_table_nl(state)}

## 11. Beste nieuwe kansen

{best_opportunities_nl(state)}

### Vervangingsanalyse

{replacement_duel_v2_markdown(state, language='nl')}

## 12. Rotatieplan portefeuille

{rotation_plan_table_nl(state)}

## 13. Definitieve actietabel

{final_action_table_nl(state)}

## 14. Positiewijzigingen in deze run

{position_changes_table_nl(state)}

## 15. Huidige posities en cash

- Startkapitaal (EUR): 100000.00
- Belegde marktwaarde (EUR): {inv:.2f}
- Cash (EUR): {cash:.2f}
- Totale portefeuillewaarde (EUR): {nav:.2f}
- Rendement sinds start (%): {(nav / 100000.0 - 1.0) * 100.0:.2f}
- EUR/USD gebruikt: {eurusd}

{section15_table_nl(state)}

## 16. Input voor de volgende run

**Deze sectie is de canonieke standaardinput voor de volgende run tenzij de gebruiker expliciet iets anders opgeeft. Vraag de gebruiker niet opnieuw om portefeuille-input zolang deze sectie beschikbaar is.**

### Portefeuilletabel
{continuity_table_nl(state)}

### Beschikbare cash
- Cash %: {cash / (nav or 1.0) * 100.0:.2f}
- Margegebruik %: 0.00
- Leverage toegestaan: Nee

### Volglijst / dynamisch radargeheugen
{watchlist_table_nl()}

### Continuïteit in aanbevelingsdiscipline
- SPY: overlapreview tegenover SMH blijft actief.
- PPA: directe vervangingsanalyse tegenover ITA vereist.
- PAVE: directe vervangingsanalyse tegenover GRID vereist.
- GLD: hedge-validiteitstest vereist.
- Vervangingskandidaten: niet geschikt voor allocatie zonder afgeronde vervangingsanalyse.

### Randvoorwaarden
- Maximale positiegrootte: 25%
- Maximaal aantal posities: 8
- Alleen UCITS: Nee
- Leveraged ETF’s toegestaan: Nee
- Drawdown-tolerantie: Gemiddeld
- Voorkeur inkomen versus groei: gebalanceerde groei met nadruk op weerbaarheid

### Wijzigingen sinds de vorige review
- Toegevoegd: een gevalideerd productiepad op basis van expliciete portefeuillestaat, prijsaudit en macro-/beleidsregime-input.
- Verlaagd: Geen, tenzij de expliciete portefeuillestaat anders aangeeft.
- Gesloten: Geen.
- Thesiswijzigingen: Geen structurele thesis is losgelaten; implementatie- en macroregimediscipline zijn duidelijk aangescherpt.

## 17. Disclaimer

Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden. Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies, en vormt geen aanbeveling om effecten te kopen, te verkopen of aan te houden. Het rapport houdt geen rekening met individuele beleggingsdoelen, financiële situatie of specifieke behoeften van de ontvanger. Beleggen brengt risico’s met zich mee, waaronder het risico op verlies van inleg.
"""
