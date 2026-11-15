# OUTCOME — weekly-etf (wekelijks rapport, VS-aandelen)

> **Doel bevestigd door de eigenaar op 2026-11-15.** De invulling van "klaar als" volgt bij de herbouw (ronde B).

**Doel:** Elke week een correct rapport over een modelportefeuille van ETF's op de Amerikaanse aandelenmarkt bij de lezers, volgens het model van `weekly-etf-eu`.

**Klaar als:**
- Het rapport is op de vaste dag vóór het vaste tijdstip verzonden.
- De portefeuille-historie sluit op de cent; elk getal komt uit de feiten.
- Eén `acceptance.yml` toetst dit (te bouwen).

**Alleen met akkoord van de eigenaar:** ontvangers en live verzenden; beslisregels, universum en benchmark; startportefeuille.

**Status:** laatste run van de wekelijkse workflow (na herbouw).

## Open vragen aan de eigenaar
- Startportefeuille: doorgaan vanaf de laatste bekende stand in deze repo, of opnieuw beginnen?
- Benchmark: S&P 500 (bijv. SPY), of een mix met obligaties zoals bij de EU-versie?
- Taal: NL en EN?

## Besluiten
- 2026-11-15 — Overgestapt op het outcome-first model (control-plane). Oudere plan-, status- en controledocumenten in deze repo zijn niet meer leidend.
- 2026-11-15 — Actief project, niet dormant.
- 2026-11-15 — Herbouw volgens het model van `weekly-etf-eu`: vaste pijplijn (data → beslissen → feiten → tekst → rapport → mail), AI rekent nooit, één acceptatietoets. Rekent in USD met Amerikaanse ETF's.
