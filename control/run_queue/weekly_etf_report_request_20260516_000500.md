# Weekly ETF report request

requested_at_utc: 2026-05-16T00:05:00Z
requested_run_date: 2026-05-16
mode: fresh-bilingual-runtime-report
source: ChatGPT

## Request
Generate and send a fresh bilingual Weekly ETF Pro Review using the current runtime production path.

## Validation focus
- Validate `runtime/client_facing_sanitizer.py` commit `83925a66f32f8c7f367357972ac0a40889d9cb1a`, which removes the hidden `panel-exec` marker and CSS selector from final delivery HTML.
- Validate that the real duplicate `panel-exec` executive-summary block is removed by the div-depth parser before delivery validation.
- The Main takeaway / Kernconclusie card must stay visually contained in its card in both English and Dutch.
- The main takeaway must not be repeated as a stray large sentence outside the hero cards.
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
