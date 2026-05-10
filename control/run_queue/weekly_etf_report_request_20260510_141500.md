# Weekly ETF Review report request

requested_at_utc: 2026-05-10T14:15:00Z
requested_run_date: 2026-05-10
mode: production
report_type: weekly_etf_review
request_source: ChatGPT

## Request
Generate and publish a fresh Weekly ETF Review Report.

## Required production path
Use the validated runtime-driven production baseline:

pricing audit
→ historical relative strength
→ macro policy research pack
→ regime continuity memory
→ first-pass lane discovery with macro policy pack
→ replacement-duel and discovery challenger pricing with max-symbols 24
→ decision-grade replacement duel pricing contract
→ final lane discovery with macro policy pack
→ runtime state
→ English/Dutch markdown render
→ selective macro/regime polish
→ output-contract fix
→ ticker linkification
→ content contract validation
→ delivery HTML contract validation
→ PDF/email delivery

## Hard requirements
- Use fresh pricing before report generation.
- Use Twelve Data, FMP, Alpha Vantage and fallback pricing according to the configured pricing layer.
- Use --max-symbols 24 for challenger pricing.
- Use the macro policy pack before lane discovery.
- Persist regime continuity memory.
- Keep macro/regime content selective and client-facing; do not dump the full macro pack into the report.
- Render the title as "Replacement Duel Table", not "Replacement Duel Table v2".
- Use the explicit runtime-rendered EN/NL report paths for polish, output-contract fixing, linkification, validation, rendering, and delivery.
- Do not deliver placeholder output.
- Do not claim delivery success without a real delivery manifest/receipt.
