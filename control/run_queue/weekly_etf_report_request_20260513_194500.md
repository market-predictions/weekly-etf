# Weekly ETF report request

requested_at_utc: 2026-05-13T17:45:00Z
requested_run_date: 2026-05-13
mode: production-fresh-report
reason: User approved fresh Weekly ETF Review generation after adding ETF Position Performance section comparable to weekly-index performance table.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_RELATIVE_STRENGTH_OK
- ETF_POSITION_PERFORMANCE_SECTION_OK
- ETF_POSITION_PERFORMANCE_OK
- ETF_EQUITY_CURVE_HISTORY_OK
- ETF_NL_LOCALIZATION_OK
- ETF_DUTCH_LANGUAGE_QUALITY_OK
- BILINGUAL_PAIR_OK
- RENDER_OK
- ETF_DELIVERY_HTML_CONTRACT_OK
- DELIVERY_OK
post_run_checks:
- Section 7A ETF Position Performance is present in English report.
- Dutch companion includes ETF-positieperformance.
- Performance table includes all current ETF holdings.
- 1w, 1m, 3m, since-entry, P/L EUR, and contribution columns render correctly.
- English and Dutch emails are both sent by GitHub Actions with PDF attachments.
