# Weekly ETF report request

requested_at_utc: 2026-05-10T14:25:00Z
requested_run_date: 2026-05-10
mode: production-fresh-report
reason: User requested generate and mail a new Weekly ETF Pro report after aligning Dutch disclaimer wording with the delivery validator.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- DELIVERY_OK
post_run_checks:
- English and Dutch emails are both sent by GitHub Actions.
- PDF attachments are present.
- Dutch disclaimer passes bilingual pair validation.
- Dutch report uses improved localization contract.
