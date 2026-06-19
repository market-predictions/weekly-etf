# WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-promotion-decision-review`
Layer: decision framework only
Status: implemented / locally validated

## Purpose

Record the explicit cockpit promotion decision after the preview renderer, manual preview workflow, visual/state-safety contracts, and side-by-side review package.

## Scope

Decision-only. This package must not implement promotion, change production report rendering, change delivery behavior, mutate state, update pricing, update trade ledger files, or edit runtime/workflow files.

## Decision boundary

Passing tests proves the cockpit preview lane is safe and reviewable. Passing tests does not authorize production promotion.

## Decision recorded

```text
decision: not_promoted_needs_iteration
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
next_package: WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH
```

## Validation evidence

```text
git diff --check: clean
python -m py_compile runtime/render_cockpit_front_page.py: passed
python -m py_compile runtime/build_cockpit_side_by_side_review.py: passed
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_cockpit_visual_state_contracts.py tests/test_cockpit_side_by_side_review.py: 16 passed in 0.20s
```

## Files added

```text
control/COCKPIT_SURFACE_PROMOTION_DECISION_20260619.md
control/work_packages/WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW_20260619_1855.md
```

## Acceptance

- one allowed decision value is recorded
- production report remains unchanged
- delivery behavior remains unchanged
- state/pricing/runtime/delivery files remain unchanged
- no generated output artifacts are committed
- next package is recorded
