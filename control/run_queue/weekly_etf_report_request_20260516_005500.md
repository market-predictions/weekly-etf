# Weekly ETF report request

requested_at_utc: 2026-05-16T00:55:00Z
requested_run_date: 2026-05-16
mode: fresh-bilingual-runtime-report
source: ChatGPT

## Request
Generate and send a fresh bilingual Weekly ETF Pro Review using the current runtime production path.

## Validation focus
- Validate `send_report_runtime_html.py` commit `67f0650d64d14e514728526ef55819e4c432a05f`, which patches both the legacy base renderer module attribute and the `send_report_OLD.build_report_html` function globals so duplicate Section 1 / executive-summary rendering is suppressed at the actual call site.
- Validate that Section 1 appears only once visually: as the three hero cards.
- The Main takeaway / Kernconclusie must not be repeated as a stray sentence outside the hero cards.
- The delivery HTML validator must still fail if a visible duplicate executive takeaway remains.
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
