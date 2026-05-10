# Weekly ETF report request

requested_at_utc: 2026-05-10T14:15:00Z
requested_run_date: 2026-05-10
mode: production-fresh-report-rerun
reason: Retry after aligning Dutch markdown quality validator with delivery HTML layer boundary for Vervangingsanalyse.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- DELIVERY_OK
post_run_checks:
- Dutch markdown quality gate passes.
- Delivery HTML contract still validates Vervangingsanalyse.
- English and Dutch PDFs are delivered by GitHub Actions.
