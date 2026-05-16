# Weekly ETF report request

requested_at_utc: 2026-05-16T01:15:00Z
requested_run_date: 2026-05-16
mode: fresh-bilingual-runtime-report
source: ChatGPT

## Request
Generate and send a fresh bilingual Weekly ETF Pro Review using the current runtime production path.

## Validation focus
- Validate `runtime/delivery_html_overrides.py` commit `177e322b0523a58707f80209fae85232eb91c532`, which fixes the hero-card replacement source by replacing the full `summary-strip` payload instead of using a nested-div regex that left an orphan `mini-value` duplicate.
- The Main takeaway / Kernconclusie must appear only once inside the hero cards.
- No orphan `<div class='mini-value'>` or duplicate takeaway text may remain inside or below the `summary-strip`.
- Section 1 must appear only once visually: as the three hero cards.
- Executive summary tickers must not be clickable.
- Important ETF tickers in tables and bulleted lists must remain clickable TradingView links, except CASH.
- Dutch hero summary must use the same regime and takeaway substance as the English report.
- Final delivery HTML must not contain forbidden placeholder tokens such as `Pending classification`.
- Final delivery HTML must not contain raw markdown ticker links.
- Pricing must use the latest completed close available under the pricing freshness guard.
- Runtime NAV must be revalued from the pricing audit, not carried forward silently from an older valuation.
- English and Dutch reports must pass render, language, numeric parity, delivery HTML, and delivery receipt/manifest checks.

## Do not claim success unless
The workflow emits a real delivery manifest or receipt and both English and Dutch delivery validations pass.
