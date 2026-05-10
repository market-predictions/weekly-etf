# Weekly ETF report request

requested_at_utc: 2026-05-10T13:55:00Z
requested_run_date: 2026-05-10
mode: production-fresh-report-rerun
reason: Retry after fixing Dutch language quality validator import path.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- DELIVERY_OK
post_run_checks:
- Dutch Vervangingsanalyse contains Dutch decision and trigger phrases.
- Dutch report does not expose internal source labels.
- Dutch disclaimer is fully Dutch.
