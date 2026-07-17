# ETF Review OS — Current State

## Snapshot date

2026-07-17

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

The `_04` package is validation evidence only and has not been delivered.

## Canonical post-execution correction runbook

```text
workflow: .github/workflows/resend-corrected-post-execution-report.yml
contract: runtime/post_execution_correction_runbook.py
send_runner: runtime/run_post_execution_correction_delivery.py
recovery_runner: runtime/recover_post_execution_correction_evidence.py
modes: validate_only | recover_no_send | send
```

The runbook is manual-only and requires explicit confirmation for any send operation.

## Cockpit implementation history

```text
WP01 preview renderer: PR #52
WP02 manual preview workflow: PR #52
WP03 visual/state-safety contracts: PR #53
WP04 side-by-side review: PR #54
WP05 promotion review: PR #55
WP06 iteration-path decision: PR #56
WP07 source/provenance iteration: PR #57
WP01 current-runtime revalidation: PR #74
WP08 evidence-based review: PR #76
WP09 client-surface refinement: PR #79
WP09 closeout: PR #80
promotion decision: PR #81
promotion decision closeout: PR #82
```

Current runtime authority precedence:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

A legitimate current zero remains authoritative.

## WP08 and WP09 review status

```text
schema_version: cockpit_side_by_side_review_v2
review_type: evidence_based_side_by_side_preview_only
review_conclusion: ready_for_promotion_decision
blocking_findings: []
all_eleven_dimensions: pass
promotion_status: not_promoted
```

WP09 closed the initial decision-clarity, bilingual-parity and premium-polish blockers without changing state, pricing, execution or delivery authority.

## Cockpit production-relationship decision — closed

```text
package: WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
selected_option: additive_delivery_front_page
PR: #81
merge_commit: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
closeout_PR: #82
closeout_merge_commit: 61f9a4b27d5e656d566c5679b237b5b31a8f0a47
production_change_in_decision_package: false
promotion_status: not_promoted
```

Selected architecture:

```text
integration_layer: delivery HTML/PDF render pipeline
classic_report_body: preserved
one email body per language: preserved
one PDF per language: preserved
attachment contract: unchanged
manifest contract: unchanged
feature gate: required
implementation default: disabled
failure behavior: unchanged classic output
rollback: disable feature flag
```

## WP10 additive delivery front page — validated

```text
package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
status: validated_ready_for_enablement_decision
PR: #83
validated_code_head: b2ca4b032793f23f13b0d4557a919623366dc501
final_validation_run: 29541727393
visual_artifact_run: 29542004498
feature_flag: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
feature_default: disabled
production_enablement: false
email_sent: false
promotion_status: not_promoted
next_package: WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

Validated behavior:

1. Disabled EN/NL delivery HTML remains byte-identical to the classic output.
2. Enabled EN/NL output adds exactly one client-facing cockpit front page.
3. Each enabled PDF adds exactly one page.
4. The complete classic report follows unchanged.
5. The smaller decision cockpit is suppressed only after successful full-front-page injection.
6. Invalid flag values and planted render failures fail closed to the classic path.
7. Standalone equity embedding and email CID behavior remain valid.
8. Email/PDF counts, attachments and manifest semantics remain unchanged.
9. Protected portfolio, pricing, valuation, ledger and pointer authority remains byte-identical.
10. All eleven WP08 review dimensions remain `pass`.

Persistent evidence:

```text
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Closed operational packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION: closed
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION: closed
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT: closed
WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW: closed
```

WP10 is implementation-validated but remains pending merge and a separate enablement decision.

## Immediate next action

After PR #83 is merged, create:

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

WP11 must decide whether to wire `MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled` into `.github/workflows/send-weekly-report.yml`. It must require validate-only exact-current evidence before any send, preserve rollback to `disabled`, and may not claim delivery without a receipt or manifest.
