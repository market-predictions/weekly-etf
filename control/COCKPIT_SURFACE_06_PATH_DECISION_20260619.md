# Cockpit Surface 06 Path Decision

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Decision layer: decision framework + output contract planning

## 1. Decision status

```text
decision_recorded
```

## 2. Selected path

```text
selected_path: iteration_path
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
runtime_code_change: none
workflow_change: none
next_package: WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE
```

## 3. Options considered

```text
A. iteration_path
B. controlled_attachment_path
```

First-page integration and front-matter replacement were not considered as next implementation choices because WP05 did not approve promotion.

## 4. Evidence reviewed

```text
PR #52 — cockpit preview lane infrastructure
PR #53 — cockpit visual/state-safety contracts
PR #54 — cockpit side-by-side review artifacts
PR #55 — cockpit promotion decision review
WP04 validation: 31 passed
WP05 validation: 16 passed
COCKPIT_SIDE_BY_SIDE_REVIEW_OK | token=260618 | promotion_status=not_promoted
control/COCKPIT_SURFACE_PROMOTION_DECISION_20260619.md
```

Evaluation dimensions:

```text
visual maturity
source/provenance clarity
audit evidence preservation
reader value
delivery safety
operational complexity
rollback complexity
risk of silent promotion
client-grade quality
```

## 5. Why this path was selected

WP05 recorded `not_promoted_needs_iteration`. The cockpit preview is technically safe and reviewable, but the evidence still does not contain an explicit coordinator-approved visual QA decision selecting an implementation path.

The next safest path is to improve source and provenance clarity before any promotion path is designed. This keeps the production report authoritative and prevents silent promotion.

## 6. Explicit non-implementation boundary

This package does not implement the iteration. It only records the selected path.

This package does not change:

```text
production report rendering
delivery behavior
portfolio state
pricing
trade ledger
valuation history
runtime state
run manifests
delivery manifests
workflows
generated output artifacts
```

## 7. Output contract for the next package

The next package may improve only the preview and review layers. It should focus on:

```text
source/provenance clarity
trust evidence visibility
clearer links between cockpit cards and classic report evidence
visual polish without delivery changes
another side-by-side review after iteration
```

The next package must keep cockpit artifacts separate from production output unless a later explicit promotion decision says otherwise.

## 8. Files that must not change

```text
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

## 9. Next work package

```text
WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE
```

## Final path decision

```text
selected_path: iteration_path
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
runtime_code_change: none
workflow_change: none
next_package: WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE
```
