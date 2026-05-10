# Weekly ETF report request

requested_at_utc: 2026-05-10T14:55:00Z
requested_run_date: 2026-05-10
mode: production-fresh-report
reason: Retry after aligning Dutch shares column header with bilingual parity parser.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- DELIVERY_OK
post_run_checks:
- Bilingual numeric parity passes for share counts.
- English and Dutch emails are delivered by GitHub Actions.
- PDF attachments are present.
