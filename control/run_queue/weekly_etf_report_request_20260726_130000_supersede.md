# Weekly ETF report request — corrected superseding delivery

requested_at_utc: 2026-07-26T13:00:00Z
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: 2026-07-24
strict_fresh_pricing_required: false
portfolio_execution_authorized: false
broker_execution_authorized: false
delivery_authorized: true
supersedes_run_id: 20260726_121721
supersedes_report: output/weekly_analysis_pro_260724_02.md
supersede_reasons:
  - Front page said no portfolio action while later sections proposed shrinking SMH and adding DFEN.
  - DFEN is a daily leveraged 3x ETF and conflicts with the no-leverage mandate.
  - The official portfolio has 9 active positions versus a maximum of 8, so a partial reduction funding a new ticker is blocked by the close-first contract.
validated_fixes:
  action_surface_evidence: output/run_manifests/weekly_etf_action_surface_validation_30202762011.json
  portfolio_constraint_evidence: output/run_manifests/weekly_etf_portfolio_constraint_validation_30202454080.json
requirements:
  - Enforce instrument eligibility and exclude DFEN from the client-facing radar.
  - Use eligible NATO and EUAD vehicles for the Europe-defense research lane.
  - Enforce the 9/8 close-first transition contract.
  - Produce zero trade intents and no add/replacement proposal while the active position count remains above the maximum.
  - Keep the front page, action snapshot, rotation plan, final action table and Section 14 fully consistent with the runtime authority.
  - Preserve official holdings and the trade ledger; no portfolio or broker execution is authorized.
  - Deliver both English and Dutch full-report HTML emails with PDF, clean Markdown, HTML and equity-curve attachments.
