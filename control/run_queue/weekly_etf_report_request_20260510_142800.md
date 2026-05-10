# Weekly ETF Review rerun request

requested_at_utc: 2026-05-10T14:28:00Z
requested_run_date: 2026-05-10
mode: production
report_type: weekly_etf_review
reason: Dutch macro localization validation fix

## Execute
Generate and publish a fresh bilingual Weekly ETF Review.

## Required validation focus
- Dutch companion validation must pass.
- Ensure runtime macro/regime injections are localized in Dutch.
- Preserve EN/NL numeric parity.
- Preserve Section 15 reconciliation.
- Preserve runtime-rendered explicit report paths.
- Preserve replacement duel pricing integrity.

## Production requirements
- Fresh pricing first.
- Challenger pricing max-symbols 24.
- Macro policy pack enabled.
- Regime continuity memory enabled.
- Runtime render and bilingual delivery enabled.
- No placeholder output.
- No delivery claim without manifest/receipt.
