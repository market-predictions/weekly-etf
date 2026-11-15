# OUTCOME — weekly-etf (wekelijks rapport, in de VS verhandelde ETF's)

**Doel:** Elke week een correct rapport over een modelportefeuille van ETF's die in de VS verhandeld worden (breed universum: aandelen, obligaties, grondstoffen, regio's, thema's), bij de lezers, volgens het model van `weekly-etf-eu`.

**Klaar als** (automatisch getoetst in `acceptance.yml`, behalve het eerste punt):
- Het rapport is elke donderdag vóór 08:00 verzonden (laatste run van `weekly.yml` geslaagd en < 8 dagen oud).
- De Amerikaanse historie sluit elke week op de cent; de spiegel volgt uit zijn transactielijst en slotkoersen.
- Elke spiegelpositie hoort bij een Amerikaanse positie volgens de goedgekeurde lijst (`v2/universe.yml`).
- De regels houden in simulatie (max. 2 fondswissels per week, satelliet ≤ 10%, aantal satellieten).
- Het rapport is NL en EN, ≤ 5 pagina's, zonder lay-outfouten en zonder verzonnen getallen.

**Alleen met akkoord van de eigenaar:** ontvangers en live verzenden; beslisregels, universum en benchmark; startportefeuille; de lijst met tweelingen en benaderingen.

**Status:** laatste run van `.github/workflows/weekly.yml`; verzendmodus in `v2/delivery.yml` (nu: trial, alleen de eigenaar).

## Besluiten
- 2026-11-15 — Overgestapt op het outcome-first model (control-plane). Oudere plan-, status- en controledocumenten in deze repo zijn niet meer leidend.
- 2026-11-15 — Actief project, niet dormant.
- 2026-11-15 — Herbouw volgens het model van `weekly-etf-eu`: vaste pijplijn (data → beslissen → feiten → tekst → rapport → mail), AI rekent nooit, één acceptatietoets.
- 2026-11-15 — Doorgaan vanaf de stand van 07-08-2026 (start 28-03-2026, €100k, basis EUR); de weken tot nu worden nagerekend.
- 2026-11-15 — Benchmark 70% S&P 500 / 30% obligaties, in EUR.
- 2026-11-15 — Eén rapport, twee portefeuilles. (1) De Amerikaanse modelportefeuille: volle universum van in de VS verhandelde ETF's (ook niche-thema's), eigen track record ongebroken vanaf 28-03, benchmark 70% SPY / 30% AGG in EUR; hier vallen alle besluiten. (2) De Europese spiegel: volgt die besluiten één op één in UCITS-fondsen, eigen track record vanaf 07-08 met dezelfde startwaarde, UCITS-benchmark 70% S&P 500 / 30% obligaties. Het rapport toont het verschil tussen beide.
- 2026-11-15 — Geen Europese tweeling: een vooraf vastgelegde benadering per fonds (verwant UCITS-fonds), anders een geldmarktfonds; in het rapport gemarkeerd als "benadering". De lijst wordt één keer door de eigenaar goedgekeurd.
- 2026-11-15 — De spiegel voert een besluit uit op de Europese slotkoers van de dag ná het Amerikaanse besluit (de VS sluit later).
- 2026-11-15 — Lijst met 39 tweelingen, 12 benaderingen en 1 keer geldmarkt (KRE) goedgekeurd door de eigenaar.
- 2026-11-15 — Herbouwd op v2 (archief: branch `archive/v1-pre-outcome-model-2026-11-15`). Rapport NL + EN, 5 pagina's. Startwaarde 7 aug herberekend: € 110.331 tegen € 110.006 in v1 (+0,30%, andere koers- en wisselkoersbron); het rendement sinds 28 maart koppelt beide.
- 2026-11-15 — Geen inflatieregel in deze portefeuille: die is alleen op eurozonedata getoetst.
- 2026-11-15 — Een satelliet die verkocht moet worden maar op de wissellimiet wacht, wordt intussen teruggebracht tot het maximum van 10% (een herweging, geen wissel).
