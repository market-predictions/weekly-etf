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

## Closed operational packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
PR #72 merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
```

## Cockpit historical status reconciliation

The cockpit lane is not at WP01 creation stage. The implemented history is:

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

Do not recreate WP01–WP07.

## Current package

```text
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION
PR: #74
status: validated_governance_reconciliation_in_progress
```

Confirmed current-runtime fixes:

1. Current post-execution weights override previous/inherited weights.
2. Current market values override previous market values.
3. A legitimate current zero does not fall through to a stale non-zero value.
4. Executed rotations use reader-facing bilingual action wording.
5. The July 14 preview shows URNM reduced and XBI added with the correct weight transitions.
6. The existing cockpit design, preview path and non-promotion boundary remain intact.

Implementation validation:

```text
head_sha: e605eb8de532eed44ec9c44a7be7c6705f128893
workflow_run: 29525632206
conclusion: success
focused_tests: 33 passed
promotion_status: not_promoted
```

The final PR governance head must pass the same read-only workflow before merge.

## Next package after PR #74 closeout

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```

### Purpose

Perform a new side-by-side review using the current July 14 classic report and the corrected current-runtime cockpit, including the provenance iteration and precise executed-action surface.

### Required review dimensions

```text
decision clarity
executed-action clarity
current-weight accuracy
performance and risk accuracy
source and provenance clarity
English/Dutch parity
visual hierarchy
premium client-grade appearance
audit evidence preservation
```

### Required start sequence

Read:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
control/work_packages/WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_01_CURRENT_RUNTIME_REVALIDATION_20260716_2020.md
```

If the WP08 work-package file does not exist, create a narrow review-only package using the existing WP04 builder and WP07 provenance evidence. Do not reopen earlier implementation packages.

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

WP08 may produce a review recommendation, but it may not promote or attach the cockpit to production. Any promotion path requires a separate explicit decision package.
