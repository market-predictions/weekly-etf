# Nederlandse terminologie — Weekly ETF Review

## Doel

Dit bestand is het taalcontract voor de Nederlandse companion van de Weekly ETF Review.

De Engelse rapportage blijft de canonieke analyse. De Nederlandse rapportage gebruikt dezelfde runtime state, dezelfde cijfers en dezelfde beslissingen, maar moet als premium Nederlandstalig klantdocument lezen.

## Vertaalbeleid

### Altijd vertalen in klantgerichte tekst

| Engels | Voorkeur Nederlands | Vermijd |
|---|---|---|
| Executive Summary | Kernsamenvatting | Executive Summary als hoofdterm |
| Main takeaway | Kernconclusie | Main takeaway |
| Portfolio implication | Portefeuille-implicatie | Portfolio implication |
| Risk appetite | Risicobereidheid | Risk appetite |
| Fresh capital / fresh cash | Vers kapitaal | Fresh cash in NL-zinnen |
| Position-size room | Ruimte binnen de positielimiet | position-size room |
| Pricing confirmation | Prijsbevestiging | pricing confirmation |
| Current holding | Huidige positie | current holding |
| Challenger | Alternatief | uitdager |
| Replacement duel | Vervangingsanalyse | duel als klantterm |
| Decision | Beoordeling | decision |
| Required trigger | Benodigde bevestiging | required trigger |
| Required next action | Volgende toets | required next action |
| Current holding still leads | Huidige positie blijft sterker | Current holding still leads |
| No replacement | Geen vervanging | no replacement |
| Needs sustained relative outperformance | Vereist aanhoudende relatieve outperformance | needs sustained |
| Replacement trigger watch | Vervangingssignaal op watchlist | replacement trigger watch |
| Funding source | Financieringsbron | funding source |
| Disclaimer | Disclaimer | half-Engelse disclaimer |
| None | Geen | None |
| Added | Toegevoegd | Added |
| Reduced | Verlaagd | Reduced |
| Closed | Gesloten | Closed |

### Mag Engels blijven

Deze termen mogen in het Nederlandse rapport blijven staan als ze in professionele beleggingscontext natuurlijker zijn:

- ETF
- ticker
- cash
- hedge
- drawdown
- beta
- capex
- small-cap
- large-cap
- risk-on / risk-off
- AI
- semiconductor
- relative strength / relatieve sterkte; kies per context, maar gebruik in labels bij voorkeur `relatieve sterkte`
- outperformance
- watchlist

### Interne termen die nooit klantgericht mogen verschijnen

- `portfolio_state_pricing_audit`
- `pricing_audit`
- `runtime rebuild required`
- `Placeholder for runtime replacement`
- `Pending classification`
- `Do not ask the user`
- `and it is not a recommendation`

## Prijsbasis in klanttaal

Interne broninformatie hoort in auditbestanden en manifests, niet in de rapporttekst.

Voorkeur:

> Prijsbasis: huidige positie en alternatief zijn beide gevalideerd op slotkoersen van YYYY-MM-DD.

Als één datum ontbreekt:

> Prijsbasis: sluitkoersbewijs is nog niet volledig; niet geschikt voor allocatiebesluit.

## Disclaimer Nederlands

Gebruik deze tekst als standaard:

> Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden. Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies, en vormt geen aanbeveling om effecten te kopen, te verkopen of aan te houden. Het rapport houdt geen rekening met individuele beleggingsdoelen, financiële situatie of specifieke behoeften van de ontvanger. Beleggen brengt risico’s met zich mee, waaronder het risico op verlies van inleg.

## Implementatieregel

Vertaal vaste labels, decision strings en statuszinnen via `runtime/nl_localization.py`. Gebruik `runtime/polish_runtime_reports.py` alleen om de taalcontractlaag toe te passen, niet als losse verzameling ad-hoc `.replace()`-regels.

## Compatibiliteit

- Houd tickers exact gelijk.
- Houd getallen exact gelijk.
- Houd de sectiestructuur gelijk aan het Engelse canonieke rapport.
- Vertaal klantgerichte labels in delivery HTML, maar behoud technische termen wanneer dat professioneel leest.
- Section 9 / Second-order Effects Map moet inhoudelijk echte macro-, markt-, beleids-, geopolitieke, sector-, winst-, kosten- of positioneringseffecten bevatten.
