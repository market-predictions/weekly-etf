# Weekly ETF report request

requested_at_utc: 2026-05-11T21:05:00Z
requested_run_date: 2026-05-11
mode: production-fresh-report
reason: User requested a new Weekly ETF Review report generation and email delivery via the validated GitHub Actions production path.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- DELIVERY_OK
post_run_checks:
- English and Dutch emails are both sent by GitHub Actions.
- PDF attachments are present.
- Dutch report preserves numeric parity and premium localization.
- Delivery HTML contract accepts localized Dutch strict-section titles.
