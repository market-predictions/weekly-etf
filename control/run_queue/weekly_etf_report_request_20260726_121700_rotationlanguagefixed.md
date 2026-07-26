# Weekly ETF report request — corrected delivery retry

requested_at_utc: 2026-07-26T12:17:00Z
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: 2026-07-24
strict_fresh_pricing_required: false
portfolio_execution_authorized: false
broker_execution_authorized: false
delivery_authorized: true
failed_source_run_id: 20260726_120140
failed_source_manifest: output/run_manifests/weekly_etf_run_manifest_2026-07-24_20260726_120140.json
failure_reason: client_surface_raw_override
fix_commit: b5ed0644d66e11f29e5bc3a2823fca3695c6efa5
regression_commit: 543315c3723811824e3d37cd0aa9b05c55689406
validation_evidence: output/run_manifests/weekly_etf_post_render_diagnostic_30201703137.json
note: Generate and deliver the corrected bilingual Weekly ETF Pro package for the latest completed July 24 close. The prior source run rendered but did not create a delivery manifest or send email. Refresh the standard runtime pipeline, preserve official holdings and trade ledger, and keep all rotations proposal-only.
