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

## Validated non-delivered baseline

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
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION: closed
```

WP08 closeout:

```text
PR: #76
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
validation_run: 29533435789
review_conclusion: iteration_required
promotion_status: not_promoted
```

## Immediate package

Create and claim:

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

### Layer

```text
output contract
operational runbook
```

### Purpose

Apply only the narrow current-runtime cockpit refinements required by WP08 and rerun the unchanged WP08 evidence contract.

### Required changes

1. Make the short summary action-aware:
   - when actions exist, state that a controlled rotation was executed;
   - do not say discipline was ahead of activity;
   - when no action exists, retain disciplined no-action wording.
2. Add a concise bilingual next-action trigger derived from current runtime authority and existing decision rules.
3. Fix Dutch punctuation without replacing punctuation across the full sentence.
4. Replace hybrid Dutch provenance labels with natural Dutch client-facing wording.
5. Preserve the existing design, cards, metrics, evidence strip and preview-only filenames.

### Required start sequence

Read:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
control/work_packages/WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260716.md
control/decisions/COCKPIT_WP08_EVIDENCE_REVIEW_DECISION_20260716.md
control/handovers/HANDOVER_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260716.md
runtime/render_cockpit_front_page.py
runtime/build_cockpit_side_by_side_review.py
```

Check for an active WP09 claim or overlapping cockpit PR before editing.

### Acceptance

Rerun WP08 v2 unchanged. Expected result:

```text
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
```

Passing the review does not promote the cockpit. A separate promotion decision remains required.

### Safety boundary

```text
production_promotion: false
production_report_replacement: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
preview_output_only: output/cockpit_preview/
review_output_only: output/cockpit_review/
```

## Subsequent report-surface audit

After WP09, inspect the client-facing `_04` report for internal wording that may still be visible, including `shadow engine`. Handle confirmed leakage in a separate report-surface cleanup package using existing macro/thesis validators. Do not combine that report cleanup into WP09.
