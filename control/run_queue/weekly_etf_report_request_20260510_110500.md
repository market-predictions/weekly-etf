# Weekly ETF report request

requested_at_utc: 2026-05-10T11:05:00Z
requested_run_date: 2026-05-10
mode: production-e2e-validation
reason: Validate compact Replacement Duel Table without Current close / Challenger close columns and improved Dutch delivery HTML labels.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_DELIVERY_HTML_CONTRACT_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- RUNTIME_SECTION15_OK
- RUNTIME_EQUITY_CURVE_OK
- DELIVERY_OK
post_run_checks:
- English and Dutch emails are both sent by GitHub Actions.
- Replacement Duel Table no longer contains Current close or Challenger close columns.
- Dutch report uses Dutch labels in strict delivery panels.
- PDF attachments are present.
