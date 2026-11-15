# v2 — hoe het werkt

Eén vaste pijplijn per week (`run_weekly.py`, donderdag 05:00 UTC op de slotkoersen van woensdag):

1. **Koersen** (`market.py`): Amerikaanse ETF's in USD (Yahoo), omgerekend naar EUR met EURUSD van dezelfde dag; de Europese spiegelfondsen in EUR.
2. **Controle**: elke positie wordt in USD vergeleken met Alpha Vantage; meer dan 1% verschil stopt de run.
3. **Beslissen** (`engine.py`, regels in `policy.yml`, universum in `universe.yml`): scan, kern SPY/AGG, satellieten, defensieve stand, max. 2 fondswissels per week.
4. **Spiegel** (`mirror.py`): voert het besluit van vorige week uit op de eerste Europese slotkoers erna, waardeert, en plant het volgende. Tweeling, benadering of geldmarkt per fonds staat in `universe.yml` (`mirror`).
5. **Feiten → tekst → rapport** (`facts.py`, `narrate.py`, `render.py`): de AI schrijft alleen tekst en elk getal daarin wordt gecontroleerd tegen de feiten; zonder AI-sleutel een vaste tekst. 5 pagina's NL + EN.
6. **Verzenden** (`mailer.py`, modus in `delivery.yml`: off / trial / live).

De staat (`state/`) wordt alleen opgeslagen als de hele run slaagt; een tweede run voor dezelfde week doet niets.
Proefdraaien zonder de staat te raken: workflow handmatig starten met *rehearsal*.

Hulpmiddelen: `backfill.py` (eenmalig: historie vanaf 7 aug 2026), `discover.py` (spiegelfondsen zoeken en controleren),
`report.py` (voorbeeldrapport zonder opslaan), `acceptance.py` (de toets op `OUTCOME.md`).
