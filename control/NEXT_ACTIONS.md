# ETF Review OS — Next Actions

## Current authoritative baseline

```text
latest_report_close: 2026-07-16
latest_report_run_id: 20260717_154351
latest_delivered_report: output/weekly_analysis_pro_260716_02.md
latest_delivered_report_nl: output/weekly_analysis_pro_nl_260716_02.md
official_portfolio_state: output/etf_portfolio_state.json
whole_share_status: compliant
nav_eur: 107117.94
cash_eur: 2534.36
active_position_count: 9
maximum_active_positions: 8
position_count_status: close_first
cockpit_production_feature: enabled
client_language_contract: active
inbox_receipt: confirmed_both_languages
```

## Completed position-count reconciliation

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
implementation_pull_request: #91
implementation_merge: 0bcb6af7e243775d876b59719ce9898fa97c690f
closeout_pull_request: #93
closeout_merge: 9cfca787620c73e65a4302d2e4dc403a921f5ffb
status: closed_merged_validated_no_send
claim_status: closed_released
decision: every non-zero whole-share position counts
generic_residual_exception: false
current_status: close_first 9/8
portfolio_change_applied: false
email_sent: false
```

The position-count preflight evaluates projected whole-share positions before official writes. While the official state remains above eight positions, a proposed transition must lower the active count and cannot introduce another ticker.

## Completed close-first execution review

```text
package: WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
pull_request: #95
implementation_merge: 2895bbb5940ead8526ab4c10d0ce3687f8aca423
closeout_pull_request: #96
closeout_merge: b2d32e327023ea515c1c78ccbc66f69b69afab45
metadata_pull_request: #97
status: closed_merged_validated_no_change
evidence_close_date: 2026-07-17
freshness_status: complete
selected_review_source: URNM
reviewed_quantity: 48 whole shares
selected_review_destination: cash
estimated_proceeds_eur: 2022.23
projected_cash_eur: 4556.59
projected_active_count: 8
portfolio_change_applied: false
email_sent: false
```

The no-change review compared all nine holdings. URNM remained the top source after removing size and implementation-practicality points. XLU ranked second, proving that the smallest position was not selected automatically.

Evidence and validation:

```text
workflow_run: 29622365939 success
workflow_job: 88019775095
focused_tests: 7 passed
artifact_id: 8422627986
artifact_digest: sha256:9f0b833f6d9dd5bb7b7558afe598c20246e67707fc5cff974e1bfc661479851a
protected_authority_hashes: identical
historical_report_hashes: identical
```

Persistent records:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
control/handovers/HANDOVER_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md
```

## Completed cockpit email HTML correction

```text
package: WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX
pull_request: #98
cockpit_email_fix_implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3
cockpit_email_fix_closeout_pull_request: #99
status: closed_on_governance_closeout_merge
email_layout: inline_styles_and_presentation_tables
head_style_dependency: false
style_strip_degradation_test: passed_both_languages
PDF_surface: preserved
classic_report_body: preserved
email_sent: false
```

The screenshot-identified defect is corrected for future generated email HTML. A real receiving-mail-client proof requires a separately authorized fresh production delivery with the normal manifest and inbox-receipt controls. Do not rewrite or resend the historical `260716_02` package as part of this correction.

## Immediate next package

Create and claim only after separate explicit approval:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION
```

Required boundaries:

1. refresh URNM and EUR/USD prices at the implementation reference time;
2. rerun the same nine-holding source-selection rubric;
3. stop without changes if URNM is no longer selected or evidence is incomplete;
4. use whole shares and introduce no new ticker;
5. pass the position-count transition contract and NAV reconciliation before official writes;
6. persist portfolio state, ledger and valuation evidence only after all gates pass;
7. do not generate or deliver a report unless separately approved;
8. do not claim delivery without a real manifest and inbox receipt.

## Separate governance cleanup

A later governance-only package may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with portfolio implementation.
