# Cockpit Surface Promotion Decision

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Decision layer: decision framework only

## 1. Decision status

```text
decision_recorded
```

## 2. Decision selected

```text
decision: not_promoted_needs_iteration
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
next_package: WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH
```

## 3. Options considered

```text
A. extra attachment
B. first page of the existing report
C. replacement for current front matter
D. rejected / continue as experiment
```

Mapped allowed decision values considered:

```text
not_promoted_continue_preview
not_promoted_needs_iteration
approved_as_extra_attachment_pending_implementation
approved_as_first_page_pending_implementation
approved_as_front_matter_replacement_pending_implementation
rejected_continue_classic_report
```

## 4. Evidence reviewed

```text
PR #52 — cockpit preview lane infrastructure
PR #53 — cockpit visual/state-safety contracts
PR #54 — cockpit side-by-side review artifacts
WP04 validation result: 31 passed
COCKPIT_SIDE_BY_SIDE_REVIEW_OK | token=260618 | promotion_status=not_promoted
output/cockpit_preview/ remains preview-only
output/cockpit_review/ contains review-only artifacts when generated locally
```

The side-by-side review assessed:

```text
readability
density
visual hierarchy
decision clarity
trust/provenance clarity
premium look and feel
audit evidence preservation
operational safety
delivery safety
promotion readiness
```

## 5. Why this decision was selected

The cockpit preview is technically safe, deterministic, and reviewable. It improves first-glance readability, visual hierarchy, and decision clarity.

However, the current evidence does not yet contain an explicit coordinator-approved visual QA decision selecting one promotion path. The safe interpretation is therefore not to promote.

The roadmap notes that an extra attachment is the default first promotion direction if promotion is later approved. This decision does not approve that implementation yet. It preserves the production report as the authority while allowing a controlled next package to decide whether the cockpit needs iteration or a formal attachment implementation path.

## 6. Explicit no-promotion / promotion boundary

```text
promotion_status: not_promoted
```

This decision does not promote the cockpit into the production report.

This decision does not make the cockpit:

```text
an email attachment
the first page of the existing report
a replacement for current front matter
a production delivery surface
```

Any future promotion must happen in a separate controlled work package with explicit implementation scope, tests, rollback boundaries, and delivery/runbook updates.

## 7. Required next action

Create a follow-up package:

```text
WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH
```

That package should choose one of two paths:

```text
1. iteration path — improve source/provenance clarity, review notes, and visual details before another side-by-side review
2. controlled attachment path — if explicitly approved by the coordinator, design cockpit as an extra preview/report attachment without replacing the classic report
```

## 8. Files that must not change

This decision package must not edit:

```text
runtime/render_cockpit_front_page.py
runtime/build_cockpit_side_by_side_review.py
.github/workflows/render-cockpit-preview.yml
.github/workflows/send-weekly-report.yml
send_report.py
send_report_runtime_html.py
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/pricing/
output/runtime/
output/run_manifests/
output/delivery/
```

## Final decision

```text
decision: not_promoted_needs_iteration
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
next_package: WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH
```
