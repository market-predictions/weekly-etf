# ETF Review OS — Next Actions

## Current production baseline

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

```text
URNM: Sell -122.008961 shares; 7.01% -> 2.01%
XBI: Buy +40.491749 shares; 0.00% -> 5.00%
```

## Delivered client baseline

```text
report_en: output/weekly_analysis_pro_260714_03.md
report_nl: output/weekly_analysis_pro_nl_260714_03.md
pdf_en: output/weekly_analysis_pro_260714_03.pdf
pdf_nl: output/weekly_analysis_pro_nl_260714_03.pdf
delivery_workflow_run: 29455717158
inbox_receipt_status: verified_bilingual
```

Do not resend `_03`.

## Validated non-delivered report baseline

```text
report_en: output/weekly_analysis_pro_260714_04.md
report_nl: output/weekly_analysis_pro_nl_260714_04.md
html_en: output/weekly_analysis_pro_260714_04_delivery.html
html_nl: output/weekly_analysis_pro_nl_260714_04_delivery.html
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

Do not describe `_04` as delivered.

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

## Cockpit history and current contract

Do not recreate WP01–WP07.

```text
WP01 renderer: PR #52
WP02 preview workflow: PR #52
WP03 visual contracts: PR #53
WP04 side-by-side review: PR #54
WP05 promotion review: PR #55
WP06 iteration decision: PR #56
WP07 source/provenance iteration: PR #57
promotion_status: not_promoted
selected_path: iteration
```

Current cockpit authority:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

Current executed-action example from the authoritative July 14 state:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

PR #74 was validated and merged:

```text
final_validated_head: 523bb038db9ccc10c009b88e6c8f6dd489bc7dc5
validation_run: 29525968480
conclusion: success
merge_commit: d80984b7336f343344719a80a29712506926bd26
focused_tests: 33 passed
promotion_status: not_promoted
```

## Immediate next package

Create or claim:

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```

No canonical WP08 work-package file currently exists. The worker should create a narrow review-only package rather than reopening WP01–WP07.

### Purpose

Perform a fresh side-by-side review using:

```text
classic baseline: current July 14 classic report artifacts
cockpit baseline: corrected current-runtime cockpit from PR #74
provenance baseline: WP07 source/evidence surface
```

### Required start sequence

Read:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
control/handovers/HANDOVER_COCKPIT_SURFACE_01_CURRENT_RUNTIME_REVALIDATION_20260716_2020.md
control/handovers/HANDOVER_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619_2015.md
runtime/render_cockpit_front_page.py
runtime/build_cockpit_side_by_side_review.py
```

Then check for an active WP08 claim or overlapping cockpit-review PR.

### Required review dimensions

```text
decision clarity
executed-action clarity
current-weight accuracy
performance and risk accuracy
source and provenance clarity
English/Dutch semantic parity
readability and density
visual hierarchy
premium client-grade appearance
audit evidence preservation
```

### Expected outputs

Review-only artifacts under:

```text
output/cockpit_review/
```

A handover must record:

```text
promotion_status: not_promoted
review conclusion
remaining gaps
recommended next package
```

### Safety boundary

```text
production_promotion: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
preview_output_only: output/cockpit_preview/
review_output_only: output/cockpit_review/
```

WP08 may recommend a subsequent decision package, but it may not attach, promote or replace the production report itself.
