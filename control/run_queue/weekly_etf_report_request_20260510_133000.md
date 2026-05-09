# Weekly ETF Review report request

requested_at_utc: 2026-05-10T13:30:00Z
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
→ first-pass lane discovery
→ replacement-duel and discovery challenger pricing with max-symbols 24
→ continue pricing fallback after unresolved cached rows
→ final lane discovery
→ runtime state
→ select only lane artifacts that satisfy the primary ETF contract
→ English/Dutch markdown render
→ export explicit runtime report paths inside the same shell step
→ polish/linkify using explicit runtime report paths
→ output-contract fix using explicit runtime report paths
→ ETF report content contract validation
→ simplified delivery HTML contract validation
→ PDF/email delivery

## Hard requirements
- Use fresh pricing before report generation.
- Price Replacement Duel Table v2 target symbols before lane-discovery challengers.
- Use --max-symbols 24 for challenger pricing.
- Do not stop on unresolved cached price rows; continue to fallback sources.
- Use a lane artifact with valid primary ETF fields; do not use legacy lane artifacts that render Primary ETF = None.
- Use the explicit runtime-rendered EN/NL report paths for polish, output-contract fixing, linkification, validation, rendering, and delivery.
- Validate delivery HTML through rendered-output invariants, not brittle radar marker matching.
- Do not deliver placeholder output.
- Fail before delivery if the report contains placeholder text, incomplete client-facing sections, or None/None opportunity labels.
- Do not claim delivery success without a real delivery manifest/receipt.
