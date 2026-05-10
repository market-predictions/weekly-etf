# Weekly ETF report request

requested_at_utc: 2026-05-10T15:25:00Z
requested_run_date: 2026-05-10
mode: production-fresh-report
reason: Combined scan-fix run after checking send_report.py and tools/validate_etf_delivery_html_contract.py together for Dutch localized section aliases.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- DELIVERY_OK
post_run_checks:
- Dutch delivery HTML contract accepts localized strict section titles.
- Dutch HTML body validates localized section titles such as Structurele kansenradar.
- English and Dutch emails are delivered by GitHub Actions.
- PDF attachments are present.
