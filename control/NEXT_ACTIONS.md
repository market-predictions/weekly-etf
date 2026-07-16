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

## Cockpit status

```text
WP01-WP08: implemented and merged
WP09: validated, PR #79 governance closeout pending
promotion_status: not_promoted
current_runtime_authority_PR: #74
WP08_review_PR: #76
```

Current cockpit authority:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

## WP09 validation result

```text
package: WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
PR: #79
validated_head: d4e6fa7aae9dab98000716b0ecf24f45d9a7b04a
WP08_validation_run: 29535872134
current_runtime_validation_run: 29535872250
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
artifact: cockpit-wp08-evidence-review-29535872134
```

All eleven WP08 v2 dimensions pass.

Implemented refinements:

```text
action-aware summary
bilingual next-action trigger
correct Dutch discipline punctuation
natural Dutch provenance labels
preserved visual and authority contracts
```

## Immediate next package

After PR #79 is merged, create and claim:

```text
WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
```

### Layer

```text
decision framework
output contract
operational runbook
```

### Purpose

Decide the production relationship of the validated cockpit. The package must compare the costs, risks and benefits of these options:

```text
A. remain preview-only experiment
B. additive front page to the current report
C. separate cockpit attachment beside the current report
D. replace the current report entry surface while retaining the classic evidence layer
E. another refinement cycle
```

### Required authority inputs

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_STATUS_20260716.md
control/work_packages/WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260716.md
control/work_packages/WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT_20260716.md
control/decisions/COCKPIT_WP08_EVIDENCE_REVIEW_DECISION_20260716.md
control/decisions/COCKPIT_WP09_REFINEMENT_DECISION_20260716.md
control/handovers/HANDOVER_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT_20260716.md
WP09 exact-current review artifact
```

### Required decision criteria

```text
client decision clarity
premium appearance
preservation of audit evidence
email and PDF usability
operational complexity
determinism
failure isolation
rollback path
English/Dutch parity
impact on current delivery contracts
```

### Decision boundary

The package may make a recommendation and define an implementation package. It must not itself modify production rendering or delivery behavior.

```text
production_change: false
email_send: false
portfolio_model_execution: false
authority_file_mutation: false
promotion_status: not_promoted until separately implemented
```

## Subsequent report-surface audit

After the cockpit promotion decision, inspect client-facing `_04` wording for internal or stale terms that may still be visible, including `shadow engine`. Handle confirmed leakage in a separate report-surface cleanup package using existing macro/thesis leakage validators. Do not combine that report cleanup with the promotion decision.

## Governance cleanup candidate

The next governance maintenance pass should reconcile stale `planned` labels for already implemented cockpit assets in `control/SYSTEM_INDEX.md`. Do not mix that documentation cleanup with production promotion implementation.
