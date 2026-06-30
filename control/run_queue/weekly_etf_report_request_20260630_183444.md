# Weekly ETF report request

Requested by ChatGPT Project session.

- Requested at UTC: 2026-06-30T18:34:44Z
- User timezone: Europe/Amsterdam
- User local time: 2026-06-30T20:34:44+02:00
- Task: Generate a fresh Weekly ETF Pro report using the production workflow.
- Required pricing basis: latest available completed U.S. regular-session close; because this request is before the 2026-06-30 U.S. regular-session close, the workflow should resolve the latest completed close according to `pricing.run_pricing_pass.requested_close_from_now`.
- Scope: market-predictions/weekly-etf production report only.

This file intentionally contains no portfolio override. The production workflow must use the repo state, pricing pass, lane discovery, runtime state builder, validators, render layer, and delivery layer as configured in `.github/workflows/send-weekly-report.yml`.
