# Weekly ETF report request

requested_at_utc: 2026-05-10T13:38:45Z
requested_run_date: 2026-05-10
mode: production-fresh-report
reason: User requested Send weekly ETF Pro report. Validate the new Dutch localization contract and quality gate through the real GitHub Actions production path.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- RUNTIME_SECTION15_OK
- RUNTIME_EQUITY_CURVE_OK
- DELIVERY_OK
post_run_checks:
- English and Dutch emails are both sent by GitHub Actions.
- PDF attachments are present.
- Dutch report contains localized decision strings in the Vervangingsanalyse.
- Dutch report does not expose internal source labels such as portfolio_state_pricing_audit.
- Dutch disclaimer is fully Dutch.
- Replacement Duel Table remains compact without Current close or Challenger close columns.
