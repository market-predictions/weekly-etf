# Weekly ETF Review report request

requested_at_utc: 2026-05-15T00:15:00Z
requested_run_date: 2026-05-15
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review.

## Purpose
Validate the delivery HTML sanitizer fix after the previous run failed on residual raw markdown ticker links in final HTML.

## Fix under validation
`runtime/client_facing_sanitizer.py` now converts residual raw markdown links that survive custom HTML rendering into real HTML anchors before delivery validation.

Example expected conversion:

`[SMH](https://www.tradingview.com/chart/?symbol=SMH)`

must become:

`<a href="https://www.tradingview.com/chart/?symbol=SMH" target="_blank" rel="noopener noreferrer">SMH</a>`

## Hard validation requirements
- English and Dutch reports must both be generated from the same runtime state.
- Dutch report must remain native Dutch, not a translated English markdown clone.
- Dutch cover/header date must match the current report run date, not the historical portfolio inception date.
- Important ETF tickers in tables and bullets must be clickable TradingView links, except CASH.
- Final delivery HTML must not contain raw markdown links such as `[SMH](https://...)`.
- Dutch tables must not contain avoidable English enum values such as Hold, Hold under review, Smaller / under review, Core beta, Growth engine, Strategic energy, Hedge ballast or None.
- Replacement-duel table should remain compact and client-facing.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
Inspect:
1. `ETF_LINKIFY_OK` for both EN and NL reports.
2. `ETF_TICKER_LINKS_OK` for both EN and NL reports.
3. Bilingual pair validation output.
4. HTML/PDF render validation output.
5. `Validate ETF delivery HTML contract` output; it must no longer fail on raw markdown links.
6. Final delivery manifest or receipt.
