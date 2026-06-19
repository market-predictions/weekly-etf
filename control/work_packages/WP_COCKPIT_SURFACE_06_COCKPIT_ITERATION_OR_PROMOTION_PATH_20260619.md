# WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-iteration-or-promotion-path`
Layer: decision framework + output contract planning
Status: implemented / locally validated

## Purpose

Select the next controlled cockpit-surface path after WP05 recorded `not_promoted_needs_iteration`.

## Scope

Control/planning only. No runtime, workflow, delivery, state, pricing, or generated output changes.

## Selected path

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

## Validation evidence

```text
git diff --check: clean
python -m py_compile runtime/render_cockpit_front_page.py: passed
python -m py_compile runtime/build_cockpit_side_by_side_review.py: passed
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_cockpit_visual_state_contracts.py tests/test_cockpit_side_by_side_review.py: 16 passed in 0.19s
```

## Files added

```text
control/COCKPIT_SURFACE_06_PATH_DECISION_20260619.md
control/work_packages/WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH_20260619_1935.md
```

## Acceptance

- selected path uses one allowed value
- no production or delivery change
- no state/pricing/runtime/delivery mutation
- no generated output committed
