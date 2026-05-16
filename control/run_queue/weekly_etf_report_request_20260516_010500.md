# Weekly ETF report request

requested_at_utc: 2026-05-16T01:05:00Z
requested_run_date: 2026-05-16
mode: diagnostic-fresh-bilingual-runtime-report
source: ChatGPT

## Request
Generate and send a fresh bilingual Weekly ETF Pro Review using the current runtime production path.

## Diagnostic focus
This run is primarily intended to expose the exact source of the repeated Main takeaway / Kernconclusie text.

Validate `tools/validate_etf_delivery_html_contract.py` commit `9b450057f8dd6148e51e993685f3b4bda1b71bd9`, which adds forensic duplicate-takeaway diagnostics.

If the duplicate executive takeaway still appears, the validator must print:
- `DUPLICATE_TAKEAWAY_CONTEXT_BEGIN`
- the exact duplicated phrase
- the number of plain-text occurrences
- occurrence offsets
- nearest label
- nearest known title
- nearest opening HTML tag
- surrounding plain-text context
- surrounding HTML context
- `DUPLICATE_TAKEAWAY_CONTEXT_END`

## Existing validation focus
- Section 1 must appear only once visually: as the three hero cards.
- The Main takeaway / Kernconclusie must not be repeated as a stray sentence outside the hero cards.
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
