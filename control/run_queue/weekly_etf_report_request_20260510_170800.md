# Weekly ETF report request

requested_at_utc: 2026-05-10T15:08:00Z
requested_run_date: 2026-05-10
mode: production-fresh-report
reason: Retry after allowing Dutch localized HTML body section aliases in send_report.py.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- DELIVERY_OK
post_run_checks:
- Dutch HTML body validates localized section titles such as Structurele kansenradar.
- English and Dutch emails are delivered by GitHub Actions.
- PDF attachments are present.
