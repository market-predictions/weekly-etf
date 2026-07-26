# Weekly ETF report request — final corrected superseding delivery

requested_at_utc: 2026-07-26T13:25:00Z
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: 2026-07-24
strict_fresh_pricing_required: false
portfolio_execution_authorized: false
broker_execution_authorized: false
delivery_authorized: true
supersedes_run_id: 20260726_121721
supersedes_failed_run_id: 20260726_124934
validated_evidence:
  portfolio_constraints: output/run_manifests/weekly_etf_portfolio_constraint_validation_30202454080.json
  action_surface: output/run_manifests/weekly_etf_action_surface_validation_30202762011.json
  cockpit_action_language: output/run_manifests/weekly_etf_cockpit_action_language_validation_30203266909.json
requirements:
  - Use the completed July 24 market close and refresh the standard runtime pipeline.
  - Enforce the 9-active-versus-8-maximum close-first contract.
  - Exclude leveraged DFEN from the client-facing research and allocation surface; use eligible NATO/EUAD vehicles where the Europe-defense lane is shown.
  - Produce zero trade intents and unchanged official position weights while the active count remains above the maximum.
  - The designed HTML/PDF front page, Markdown summary, action snapshot, rotation plan, final action table and Section 14 must all state the same zero-change outcome.
  - Remove all internal override terminology from client-facing English and Dutch surfaces.
  - Preserve official portfolio holdings, valuation authority and trade ledger; no model or broker execution is authorized.
  - Deliver English and Dutch full-report HTML emails with PDF, clean Markdown, HTML and equity-curve attachments.
