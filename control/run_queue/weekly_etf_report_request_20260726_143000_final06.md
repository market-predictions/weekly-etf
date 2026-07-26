# Weekly ETF report request — definitive _06 delivery

requested_at_utc: 2026-07-26T14:30:00Z
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: 2026-07-24
strict_fresh_pricing_required: false
portfolio_execution_authorized: false
broker_execution_authorized: false
delivery_authorized: true
supersedes_all_prior_2026_07_24_deliveries: true
validated_evidence:
  portfolio_constraints: output/run_manifests/weekly_etf_portfolio_constraint_validation_30202454080.json
  action_surface: output/run_manifests/weekly_etf_action_surface_validation_30202762011.json
  cockpit_action_language: output/run_manifests/weekly_etf_cockpit_action_language_validation_30203266909.json
  zero_execution_delivery_status: output/run_manifests/weekly_etf_zero_execution_delivery_status_validation_30203632278.json
  decision_status_copy: output/run_manifests/weekly_etf_decision_status_copy_validation_30204023152.json
requirements:
  - Use the completed July 24 close and refresh the standard runtime pipeline.
  - Enforce the 9-active-versus-8-maximum close-first contract.
  - Exclude leveraged DFEN from all client-facing allocation and research surfaces; use eligible NATO/EUAD vehicles for the Europe-defense research lane.
  - Produce zero trade intents and unchanged official position weights.
  - State consistently on the styled front page, summary, action snapshot, rotation plan, final action table and position-change section that no portfolio change was proposed or executed.
  - Use Portfolio decision status / Status portefeuillebesluit.
  - Replace any generic reflected-rotation boilerplate with the state-neutral statement that the official portfolio state and trade ledger are authoritative for the report.
  - Remove all internal override terminology from client-facing English and Dutch surfaces.
  - Preserve official holdings, valuation authority and trade ledger; no model or broker execution is authorized.
  - Deliver English and Dutch full-report HTML emails with PDF, clean Markdown, HTML and equity-curve attachments.
