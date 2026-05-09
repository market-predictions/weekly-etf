# Weekly ETF Review report request

requested_at_utc: 2026-05-09T12:25:00Z
requested_run_date: 2026-05-09
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
→ targeted challenger pricing
→ final lane discovery
→ runtime state
→ English/Dutch markdown render
→ polish/linkify
→ ETF report content contract validation
→ delivery HTML overrides
→ delivery HTML contract validation
→ PDF/email delivery

## Hard requirements
- Use fresh pricing before report generation.
- Use the explicit runtime-rendered EN/NL report paths for output-contract fixing, validation, rendering, and delivery.
- Do not deliver placeholder output.
- Fail before delivery if the report contains placeholder text or incomplete client-facing sections.
- Do not claim delivery success without a real delivery manifest/receipt.
