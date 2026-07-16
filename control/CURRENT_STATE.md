# ETF Review OS — Current State

## Snapshot date

2026-07-16

## Repository

```text
market-predictions/weekly-etf
```

## Current production status

The July 14 production review remains the latest verified production baseline.

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
pricing_lineage_status: passed
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

Executed mutation:

```text
URNM: Sell -122.008961 shares; model weight 7.01% -> 2.01%
XBI: Buy +40.491749 shares; model weight 0.00% -> 5.00%
```

Authority sources:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
output/runtime/etf_report_state_20260714_20260715_175910_executed.json
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
```

## Latest verified delivered client package

```text
english_report: output/weekly_analysis_pro_260714_03.md
english_pdf: output/weekly_analysis_pro_260714_03.pdf
dutch_report: output/weekly_analysis_pro_nl_260714_03.md
dutch_pdf: output/weekly_analysis_pro_nl_260714_03.pdf
corrected_delivery_run: 29455717158
delivery_layer_status: smtp_sendmail_returned_no_exception
inbox_receipt_status: verified_bilingual
```

Do not resend `_03`.

Delivery evidence:

```text
output/delivery/weekly_etf_correction_delivery_receipt_2026-07-14_29455717158.txt
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

## Latest validated non-delivered report package

```text
english_report: output/weekly_analysis_pro_260714_04.md
english_html: output/weekly_analysis_pro_260714_04_delivery.html
english_pdf: output/weekly_analysis_pro_260714_04.pdf
dutch_report: output/weekly_analysis_pro_nl_260714_04.md
dutch_html: output/weekly_analysis_pro_nl_260714_04_delivery.html
dutch_pdf: output/weekly_analysis_pro_nl_260714_04.pdf
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

The `_04` package is review evidence only. Do not describe it as delivered.

## Canonical post-execution correction runbook

```text
workflow: .github/workflows/resend-corrected-post-execution-report.yml
contract: runtime/post_execution_correction_runbook.py
send_runner: runtime/run_post_execution_correction_delivery.py
recovery_runner: runtime/recover_post_execution_correction_evidence.py
modes: validate_only | recover_no_send | send
```

The runbook is manual-only, uses the established `MRKT_RPRTS_*` mail contract, requires exact dual confirmation for sending, prevents correction-suffix reuse and supports no-send evidence recovery.

## Cockpit preview lane

The cockpit remains a separate preview/review lane with no production promotion authority.

Historical implementation status is reconciled:

```text
WP01 preview renderer: merged in PR #52
WP02 manual preview workflow: merged in PR #52
WP03 visual/state-safety contracts: merged in PR #53
WP04 side-by-side review: merged in PR #54
WP05 promotion decision review: merged in PR #55
WP06 iteration path decision: merged in PR #56
WP07 source/provenance iteration: merged in PR #57
promotion_status: not_promoted
selected_path: iteration
```

The old `WP01: not_started` status was stale and is retired.

## Cockpit current-runtime revalidation — closed

```text
package: WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION
status: closed
PR: #74
merge_commit: d80984b7336f343344719a80a29712506926bd26
final_validated_head: 523bb038db9ccc10c009b88e6c8f6dd489bc7dc5
final_validation_run: 29525968480
final_validation_conclusion: success
promotion_status: not_promoted
```

Closed defects:

```text
previous_weight_pct selected before current_weight_pct
previous_market_value_eur selected before market_value_eur
generic action-present wording for executed rotations
```

Canonical cockpit authority order:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

A legitimate current zero remains authoritative.

Current executed-action surface:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

with the current runtime transitions:

```text
URNM 7.01% -> 2.01%
XBI 0.00% -> 5.00%
```

## Cockpit validation evidence

```text
implementation_head: e605eb8de532eed44ec9c44a7be7c6705f128893
implementation_validation_run: 29525632206
final_governance_head: 523bb038db9ccc10c009b88e6c8f6dd489bc7dc5
final_governance_validation_run: 29525968480
focused_tests: 33 passed
production_delivery_html_contract: passed
macro_thesis_leakage_validator: passed
protected_authority_hashes_before_after: identical
email_send: false
portfolio_model_execution: false
official_state_mutation: false
official_trade_ledger_mutation: false
```

Generated CI artifacts remained preview/review evidence only:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.*
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260714.*
```

They were uploaded as workflow artifacts and were not committed as production output or treated as delivery evidence.

## Closed packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION: closed
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
PR #72 merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
PR #74 merge_commit: d80984b7336f343344719a80a29712506926bd26
```

## Immediate next action

Select and claim:

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```

WP08 must compare the current July 14 classic report with the corrected current-runtime cockpit. It remains review-only and may not make a production promotion, attachment or delivery change.
