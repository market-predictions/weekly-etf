# Weekly ETF report request

requested_at_utc: 2026-05-15T18:15:00Z
requested_run_date: 2026-05-15
mode: fresh-bilingual-runtime-report
source: ChatGPT

## Request
Generate and send a fresh bilingual Weekly ETF Pro Review using the current runtime production path.

## Validation focus
- Validate the latest `runtime/client_facing_sanitizer.py` fix that prevents `Pending classification` from reappearing in final delivery HTML.
- Executive summary tickers must not be clickable.
- Dutch hero summary must use the same regime and takeaway substance as the English report.
- Final delivery HTML must not contain forbidden placeholder tokens such as `Pending classification`.
- Final delivery HTML must not contain raw markdown ticker links.
- Important ETF tickers in tables and bulleted lists must remain clickable TradingView links, except CASH.
- Pricing must use the latest completed close available under the pricing freshness guard.
- Runtime NAV must be revalued from the pricing audit, not carried forward silently from an older valuation.
- English and Dutch reports must pass render, language, numeric parity, delivery HTML, and delivery receipt/manifest checks.

## Do not claim success unless
The workflow emits a real delivery manifest or receipt and both English and Dutch delivery validations pass.
