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

## Cockpit preview lane — historical implementation

```text
WP01 preview renderer: PR #52
WP02 manual preview workflow: PR #52
WP03 visual/state-safety contracts: PR #53
WP04 side-by-side review: PR #54
WP05 promotion review: PR #55
WP06 iteration-path decision: PR #56
WP07 source/provenance iteration: PR #57
```

Stable boundary:

```text
promotion_status: not_promoted
classic_report_evidence_layer: preserved
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

## WP08 evidence-based side-by-side review — closed

```text
package: WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
status: closed
PR: #76
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
WP08_validation_run: 29533435789
initial_review_conclusion: iteration_required
promotion_status: not_promoted
```

WP08 introduced:

```text
schema_version: cockpit_side_by_side_review_v2
review_type: evidence_based_side_by_side_preview_only
```

Its initial exact-current review identified three presentation blockers:

```text
decision_clarity
bilingual_semantic_parity
premium_look_and_feel
```

## WP09 current-runtime client-surface refinement — closed

```text
package: WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
status: closed
PR: #79
merge_commit: 9b679df825fdc4c7ce37cbdc2474acae6d25d67f
closeout_PR: #80
closeout_merge_commit: 009e0f1a910c44b43de0d6c5babf3b1e0eae5cfd
final_validated_head: 739f80854456edc852baa167fcd849b98a56a4ff
WP08_validation_run: 29536333738
current_runtime_validation_run: 29536333731
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
```

Implemented preview refinements:

1. Action-aware controlled-rotation summary.
2. Dedicated bilingual next-action trigger derived from current state.
3. Correct Dutch discipline punctuation.
4. Natural Dutch provenance labels.
5. Preserved design, evidence strip, preview paths and authority precedence.

All eleven WP08 dimensions pass:

```text
readability
density
visual_hierarchy
decision_clarity
executed_action_clarity
current_weight_accuracy
performance_risk_accuracy
trust_provenance_clarity
bilingual_semantic_parity
premium_look_and_feel
audit_evidence_preservation
```

Evidence:

```text
artifact: cockpit-wp08-evidence-review-29535872134
artifact_digest: sha256:0a86df7071453783315c28bb60e9dd620c4eea4fbdf6f2f9fab9812a83fdb628
input_sha256_count: 10
protected_authority_hashes_before_after: identical
email_send: false
portfolio_model_execution: false
authority_file_mutation: false
```

## Cockpit promotion decision review

```text
package: WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
status: decision_recorded_validation_pending
selected_option: additive_delivery_front_page
production_change_in_decision_package: false
promotion_status: not_promoted
next_package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

Decision rationale:

- the cockpit has no remaining review blockers;
- the classic report remains the complete audit/evidence layer;
- the current delivery contract is one HTML body and one PDF per language;
- an additive front page improves the client entry surface without adding attachment or manifest complexity;
- full replacement creates unnecessary migration risk;
- a separate attachment creates avoidable recipient and delivery friction.

Selected implementation architecture:

```text
integration_layer: delivery HTML/PDF render pipeline
classic_report_body: preserved
email_count: unchanged
PDF_count: unchanged
attachment_contract: unchanged
manifest_contract: unchanged
feature_gate: required
implementation_default: disabled
failure_behavior: unchanged classic output
rollback: disable feature flag
```

When the full cockpit front page is enabled, the smaller injected `Decision cockpit / Besliscockpit` must be suppressed to prevent duplication. The underlying classic report sections remain intact.

The decision is recorded in:

```text
control/decisions/COCKPIT_PROMOTION_DECISION_20260716.md
control/decisions/cockpit_promotion_decision_20260716.json
```

## Closed operational packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION: closed
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION: closed
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT: closed
```

## Immediate next action

After the promotion decision package validates and merges, create:

```text
WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

WP10 may implement a feature-gated production render path, but must remain disabled by default, send no email during validation and preserve fail-closed classic output.
