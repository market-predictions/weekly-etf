# Weekly ETF report request — definitive corrected superseding delivery

requested_at_utc: 2026-07-26T13:45:00Z
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: 2026-07-24
strict_fresh_pricing_required: false
portfolio_execution_authorized: false
broker_execution_authorized: false
delivery_authorized: true
supersedes_run_ids:
  - 20260726_121721
  - 20260726_130440
validated_evidence:
  portfolio_constraints: output/run_manifests/weekly_etf_portfolio_constraint_validation_30202454080.json
  action_surface: output/run_manifests/weekly_etf_action_surface_validation_30202762011.json
  cockpit_action_language: output/run_manifests/weekly_etf_cockpit_action_language_validation_30203266909.json
  zero_execution_delivery_status: output/run_manifests/weekly_etf_zero_execution_delivery_status_validation_30203632278.json
requirements:
  - Use the completed July 24 close and refresh the standard runtime pipeline.
  - Enforce the 9-active-versus-8-maximum close-first contract.
  - Exclude leveraged DFEN from the client-facing allocation and research surface; use eligible NATO/EUAD vehicles for the Europe-defense research lane.
  - Produce zero trade intents and unchanged official position weights.
  - State consistently on the styled front page, summary, action snapshot, rotation plan, final action table and position-change section that no portfolio change was proposed or executed.
  - In zero-execution states, use Portfolio decision status / Status portefeuillebesluit and never say a rotation was already reflected.
  - Remove all internal override terminology from client-facing English and Dutch surfaces.
  - Preserve official holdings, valuation authority and trade ledger; no model or broker execution is authorized.
  - Deliver English and Dutch full-report HTML emails with PDF, clean Markdown, HTML and equity-curve attachments.
