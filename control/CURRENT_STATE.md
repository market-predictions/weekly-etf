# ETF Review OS — Current State

## Snapshot date

2026-07-16

## Repository

```text
market-predictions/weekly-etf
```

## Current production baseline

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
URNM: Sell -122.008961 shares; 7.01% -> 2.01%
XBI: Buy +40.491749 shares; 0.00% -> 5.00%
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

The `_04` package is review evidence only and has not been delivered.

## Canonical post-execution correction runbook

```text
workflow: .github/workflows/resend-corrected-post-execution-report.yml
contract: runtime/post_execution_correction_runbook.py
send_runner: runtime/run_post_execution_correction_delivery.py
recovery_runner: runtime/recover_post_execution_correction_evidence.py
modes: validate_only | recover_no_send | send
```

The runbook is manual-only and requires explicit confirmation for any send operation.

## Cockpit preview lane

Historical implementation:

```text
WP01 preview renderer: PR #52
WP02 manual preview workflow: PR #52
WP03 visual/state-safety contracts: PR #53
WP04 side-by-side review: PR #54
WP05 promotion review: PR #55
WP06 iteration-path decision: PR #56
WP07 source/provenance iteration: PR #57
```

Stable cockpit status:

```text
promotion_status: not_promoted
selected_path: iteration
```

## Cockpit current-runtime authority — closed

```text
package: WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION
status: closed
PR: #74
merge_commit: d80984b7336f343344719a80a29712506926bd26
validation_run: 29525968480
```

Authority precedence:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

A legitimate current zero remains authoritative.

Current action surface:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

## WP08 evidence-based side-by-side review — closed

```text
package: WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
status: closed
PR: #76
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
final_validated_head: 830f79c09cbb170f748f840647ddccfe78d3c68c
WP08_validation_run: 29533435789
current_runtime_validation_run: 29533435716
review_conclusion: iteration_required
promotion_status: not_promoted
```

WP08 replaced the static June review with:

```text
schema_version: cockpit_side_by_side_review_v2
review_type: evidence_based_side_by_side_preview_only
```

The review now selects only the current `_04` classic sources and current bilingual cockpit previews, evaluates artifact contents against runtime state, records input SHA-256 values and produces structured bilingual HTML.

Passed dimensions:

```text
readability
density
visual_hierarchy
executed_action_clarity
current_weight_accuracy
performance_risk_accuracy
trust_provenance_clarity
audit_evidence_preservation
```

Blocking dimensions:

```text
decision_clarity
bilingual_semantic_parity
premium_look_and_feel
```

Blocking findings:

1. The summary says discipline is ahead of activity despite the executed URNM-to-XBI rotation.
2. The cockpit lacks a dedicated next-action trigger available in the classic decision cockpit.
3. The Dutch discipline sentence ends with a comma.
4. Dutch provenance labels retain hybrid English terminology.

These are preview presentation defects, not state, pricing or execution defects.

WP08 evidence:

```text
artifact: cockpit-wp08-evidence-review-29533073516
artifact_digest: sha256:a52ec091725dae17d992d940454cb11daa8dad1c6b7f585beec90f0473a473f0
protected_authority_hashes_before_after: identical
email_send: false
portfolio_model_execution: false
authority_file_mutation: false
```

## Closed operational packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION: closed
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION: closed
```

## Immediate next action

Claim:

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

WP09 remains preview-only. It must correct only the three WP08 blocking dimensions, preserve the current cockpit design and authority contract, and rerun WP08 v2 unchanged.
