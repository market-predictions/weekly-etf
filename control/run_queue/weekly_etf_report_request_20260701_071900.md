# Weekly ETF report request

Requested by ChatGPT Project session after ETF Position Attribution Backfill patch.

- Requested at UTC: 2026-07-01T07:19:00Z
- User timezone: Europe/Amsterdam
- User local time: 2026-07-01T09:19:00+02:00
- Task: Generate a fresh Weekly ETF Pro report using the production workflow.
- Required pricing basis: latest available completed U.S. regular-session close; at request time this should normally resolve to the 2026-06-30 close according to `pricing.run_pricing_pass.requested_close_from_now`.
- Required report-quality check: Section 7A ETF Position Performance should use the ledger-backed attribution backfill introduced in `runtime/portfolio_attribution_basis.py` and `runtime/add_etf_position_performance_section.py`.
- Scope: `market-predictions/weekly-etf` production report only.

This file intentionally contains no portfolio override. The production workflow must use the repo state, pricing pass, lane discovery, runtime state builder, validators, render layer, and delivery layer as configured in `.github/workflows/send-weekly-report.yml`.
