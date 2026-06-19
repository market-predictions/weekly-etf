# Handover — WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-iteration-or-promotion-path`
Status: implemented / validation pending in Codespaces

## Summary

This package records the next cockpit-surface path after WP05.

Added files:

```text
control/COCKPIT_SURFACE_06_PATH_DECISION_20260619.md
control/work_packages/WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH_20260619_1935.md
```

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

## Evidence basis

```text
PR #52 — cockpit preview lane infrastructure
PR #53 — cockpit visual/state-safety contracts
PR #54 — cockpit side-by-side review artifacts
PR #55 — cockpit promotion decision review
WP04 validation: 31 passed
WP05 validation: 16 passed
```

## Boundary

This package did not add or modify runtime code, workflow code, delivery code, production renderer code, pricing, portfolio state, valuation history, trade ledger, runtime state, run manifests, delivery manifests, or generated output artifacts.

## Validation to run

```bash
git diff --check

python -m py_compile runtime/render_cockpit_front_page.py
python -m py_compile runtime/build_cockpit_side_by_side_review.py

pytest tests/test_cockpit_front_page_preview.py \
       tests/test_cockpit_preview_workflow.py \
       tests/test_cockpit_visual_state_contracts.py \
       tests/test_cockpit_side_by_side_review.py
```

Then clean generated cache files if present:

```bash
git clean -fd __pycache__ runtime/__pycache__ tests/__pycache__ tools/__pycache__ output/cockpit_preview output/cockpit_review
git status --short
```

## Remaining work

- Run validation in Codespaces.
- Confirm only the three control files are changed.
- Open PR: `Record cockpit iteration or promotion path decision`.
- After merge, start `WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE` only if explicitly requested.
