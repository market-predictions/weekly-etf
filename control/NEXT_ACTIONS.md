# ETF Review OS — Next Actions

## Current authoritative baseline

```text
latest_report_close: 2026-07-17
latest_report_run_id: 20260718_140601
latest_delivered_report: output/weekly_analysis_pro_260717_02.md
latest_delivered_report_nl: output/weekly_analysis_pro_nl_260717_02.md
run_manifest: output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260718_140601.json
delivery_manifest: output/delivery/weekly_etf_delivery_manifest_2026-07-17_20260718_140601.json
workflow_status: workflow_success
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception
inbox_receipt: confirmed_both_languages
attachments_per_language: 4
official_portfolio_state: output/etf_portfolio_state.json
whole_share_status: compliant
nav_eur: 106644.21
cash_eur: 2534.36
active_position_count: 9
maximum_active_positions: 8
position_count_status: close_first
```

## Completed fresh delivery recovery

```text
package: WP_FRESH_ETF_DELIVERY_RECOVERY
status: closed_delivered_inbox_confirmed
claim_status: closed_released
source_run_id: 20260718_140601
client_language_fix_pr: #105
client_language_fix_merge: bfba7c2e038eaba9a071008fc33fe09832dd4f5c
retrigger_pr: #106
retrigger_merge: ba558abf9c79ecd2066ebe8fc57db41a9c9c44ee
delivery_evidence_commit: a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea
```

The missing email was not caused by GitHub Actions credits. The runner executed normally and failed at the client-surface language gate on uncovered `release score` and minimum-trade-size override labels. The shared normalizer and regression tests were corrected, after which the transport-only recovery completed.

No further retry or resend is pending for the 2026-07-17 package. A delivery manifest and both inbox receipts now exist, so another automatic recovery must fail closed.

## Completed position-count reconciliation

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
status: closed_merged_validated_no_send
claim_status: closed_released
decision: every non-zero whole-share position counts
current_status: close_first 9/8
portfolio_change_applied: false
```

Any future transition while above eight positions must reduce the active count and cannot introduce a new ticker.

## Completed close-first execution review

```text
package: WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
status: closed_merged_validated_no_change
evidence_close_date: 2026-07-17
selected_review_source: URNM
reviewed_quantity: 48 whole shares
selected_review_destination: cash
projected_active_count: 8
portfolio_change_applied: false
```

URNM ranked first under the common rubric and XLU ranked second. This result is review evidence, not execution authority.

## Immediate next portfolio package

Create and claim only after separate explicit approval:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION
```

Required boundaries:

1. refresh URNM and EUR/USD pricing at the implementation reference time;
2. rerun the same nine-holding source-selection rubric;
3. stop without changes if URNM is no longer selected or evidence is incomplete;
4. use whole shares and introduce no new ticker;
5. pass the position-count transition contract and NAV reconciliation before official writes;
6. persist portfolio state, ledger and valuation evidence only after all gates pass;
7. do not generate or deliver another report unless separately approved;
8. do not claim delivery without a real manifest and inbox receipts.

## Separate output-quality backlog

A later package may audit the wording extracted from the actual receiving mail-client body. This should focus on client-readable terminology in the cockpit front page and must not alter portfolio authority or resend the delivered 2026-07-17 package without explicit approval.

## Separate governance cleanup

A later governance-only package may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with portfolio implementation.
