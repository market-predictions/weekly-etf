# Weekly ETF Review report request

requested_at_utc: 2026-05-15T00:01:00Z
requested_run_date: 2026-05-15
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review.

## Purpose
Validate the latest client-facing quality fixes after the successful native Dutch report run.

## Fixes under validation
- Report-wide ticker linkification now runs after all markdown insertions and NL cleanup steps.
- Ticker-link validation now checks important report sections before delivery.
- Runtime delivery date parsing now gives authority to the H1 report title so the cover does not pick an older historical valuation date from Section 7.
- Dutch delivery HTML overrides now localize enum values and role labels such as Hold, Hold under review, Smaller / under review, Core beta, Growth engine, Strategic energy, Hedge ballast and None.
- Replacement-duel tables are now compacted centrally through `runtime/replacement_duel_v2.py` with `INVESTOR_REPLACEMENT_DUEL_LIMIT = 8`.

## Hard validation requirements
- English and Dutch reports must both be generated from the same runtime state.
- Dutch report must remain native Dutch, not a translated English markdown clone.
- Dutch cover/header date must match the current report run date, not the historical portfolio inception date.
- Important ETF tickers in tables and bullets must be clickable TradingView links, except CASH.
- Dutch tables must not contain avoidable English enum values such as Hold, Hold under review, Smaller / under review, Core beta, Growth engine, Strategic energy, Hedge ballast or None.
- Replacement-duel table should remain compact and client-facing.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
Inspect:
1. `ETF_LINKIFY_OK` for both EN and NL reports.
2. `ETF_TICKER_LINKS_OK` for both EN and NL reports.
3. Bilingual pair validation output.
4. Dutch language quality validator output.
5. HTML/PDF render validation output.
6. Delivery HTML contract validation output.
7. Final delivery manifest or receipt.
