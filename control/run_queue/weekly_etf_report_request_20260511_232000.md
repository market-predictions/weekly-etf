# Weekly ETF report request

requested_at_utc: 2026-05-11T21:20:00Z
requested_run_date: 2026-05-11
mode: production-fresh-report
reason: User approved corrected rerun after fixing Section 7 equity curve history to use output/etf_valuation_history.csv plus current runtime NAV.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_EQUITY_CURVE_HISTORY_OK
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- DELIVERY_OK
post_run_checks:
- Section 7 equity curve table contains the full valuation history, not only start and latest point.
- Embedded equity curve chart shows intermediate valuation dates.
- English and Dutch emails are both sent by GitHub Actions.
- PDF attachments are present.
