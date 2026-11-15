# OUTCOME — weekly-etf (wekelijks rapport, in de VS verhandelde ETF's)

> **Doel bevestigd door de eigenaar op 2026-11-15.** De invulling van "klaar als" volgt bij de herbouw (ronde B).

**Doel:** Elke week een correct rapport over een modelportefeuille van ETF's die in de VS verhandeld worden (breed universum: aandelen, obligaties, grondstoffen, regio's, thema's), bij de lezers, volgens het model van `weekly-etf-eu`.

**Klaar als:**
- Het rapport is op de vaste dag vóór het vaste tijdstip verzonden.
- Beide portefeuille-historieën (VS en spiegel) sluiten op de cent; elk getal komt uit de feiten.
- Elke spiegelpositie hoort bij een Amerikaanse positie volgens de goedgekeurde lijst.
- Eén `acceptance.yml` toetst dit (te bouwen).

**Alleen met akkoord van de eigenaar:** ontvangers en live verzenden; beslisregels, universum en benchmark; startportefeuille; de lijst met tweelingen en benaderingen.

**Status:** laatste run van de wekelijkse workflow (na herbouw).

## Open vragen aan de eigenaar
- Taal: NL en EN?

## Besluiten
- 2026-11-15 — Overgestapt op het outcome-first model (control-plane). Oudere plan-, status- en controledocumenten in deze repo zijn niet meer leidend.
- 2026-11-15 — Actief project, niet dormant.
- 2026-11-15 — Herbouw volgens het model van `weekly-etf-eu`: vaste pijplijn (data → beslissen → feiten → tekst → rapport → mail), AI rekent nooit, één acceptatietoets.
- 2026-11-15 — Doorgaan vanaf de stand van 07-08-2026 (start 28-03-2026, €100k, basis EUR); de weken tot nu worden nagerekend.
- 2026-11-15 — Benchmark 70% S&P 500 / 30% obligaties, in EUR.
- 2026-11-15 — Eén rapport, twee portefeuilles. (1) De Amerikaanse modelportefeuille: volle universum van in de VS verhandelde ETF's (ook niche-thema's), eigen track record ongebroken vanaf 28-03, benchmark 70% SPY / 30% AGG in EUR; hier vallen alle besluiten. (2) De Europese spiegel: volgt die besluiten één op één in UCITS-fondsen, eigen track record vanaf 07-08 met dezelfde startwaarde, UCITS-benchmark 70% S&P 500 / 30% obligaties. Het rapport toont het verschil tussen beide.
- 2026-11-15 — Geen Europese tweeling: een vooraf vastgelegde benadering per fonds (verwant UCITS-fonds), anders een geldmarktfonds; in het rapport gemarkeerd als "benadering". De lijst wordt één keer door de eigenaar goedgekeurd.
- 2026-11-15 — De spiegel voert een besluit uit op de Europese slotkoers van de dag ná het Amerikaanse besluit (de VS sluit later).
