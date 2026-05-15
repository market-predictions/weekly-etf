# Weekly ETF Review report request

requested_at_utc: 2026-05-15T00:35:00Z
requested_run_date: 2026-05-15
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review.

## Purpose
Validate the latest post-delivery fixes after the previous successful delivery still showed three quality issues:

1. Tickers in the executive summary / hero cards should not be clickable, to preserve executive look and feel.
2. Dutch hero cards must use the same underlying information as the English report and must parse the native Dutch Section 1 labels.
3. Portfolio valuation must be based on fresh completed close pricing, not stale carried-forward valuation from an older run.

## Fixes under validation
- `runtime/link_runtime_report_tickers.py` skips Section 1 / executive summary ticker linkification while continuing to link tickers in tables and bullet lists.
- `runtime/delivery_html_overrides.py` reads native Dutch Section 1 keys such as `Primair regime`, `Geopolitiek regime`, and `Belangrijkste conclusie` for Dutch hero cards.
- `pricing/run_pricing_pass.py` now requests the latest completed U.S. cash close instead of blindly using the UTC run date, and blocks stale holding closes when coverage is insufficient.
- `runtime/build_etf_report_state.py` revalues holdings from fresh `price_results` so NAV, market values and weights are recalculated from fresh closes rather than inherited stale portfolio snapshots.

## Hard validation requirements
- English and Dutch reports must both be generated from the same runtime state.
- Section 1 / hero-card ticker mentions must remain plain text, not TradingView links.
- Important tickers in tables and bullet lists must remain clickable TradingView links, except CASH.
- Dutch hero cards must not fall back to generic defaults when the Dutch report contains native labels.
- Dutch hero-card information must be semantically aligned with English hero-card information.
- Pricing audit must show the requested close date as the latest completed U.S. cash close available for this run.
- Runtime state must use fresh `price_results` to revalue holdings.
- Portfolio value for the current run must not silently repeat the older May 5 valuation unless the fresh pricing audit proves no value changed.
- Stale holding closes must fail loudly rather than being presented as fresh valuation.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
Inspect:
1. `PRICING_PASS_OK` / requested close date / stale count.
2. `ETF_RUNTIME_STATE_OK` and `pricing_revalued_from_price_results` validation flag.
3. `ETF_LINKIFY_OK` for both EN and NL reports.
4. `ETF_TICKER_LINKS_OK` for both EN and NL reports.
5. HTML/PDF render validation output.
6. Delivery HTML contract validation output.
7. Final delivery manifest or receipt.
