# Handover — WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-promotion-decision-review`
Status: implemented / validation pending in Codespaces

## Summary

This package records the explicit cockpit promotion decision after WP01 through WP04.

Added files:

```text
control/COCKPIT_SURFACE_PROMOTION_DECISION_20260619.md
control/work_packages/WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW_20260619_1855.md
```

## Decision selected

```text
decision: not_promoted_needs_iteration
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
next_package: WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH
```

## Evidence basis

```text
PR #52 — cockpit preview lane infrastructure
PR #53 — cockpit visual/state-safety contracts
PR #54 — cockpit side-by-side review artifacts
WP04 validation: 31 passed
COCKPIT_SIDE_BY_SIDE_REVIEW_OK | token=260618 | promotion_status=not_promoted
```

## Boundary

This package did not add or modify runtime code, workflow code, delivery code, production renderer code, pricing, portfolio state, valuation history, trade ledger, runtime state, run manifests, or delivery manifests.

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

Optional review artifact generation, if desired:

```bash
python -m runtime.render_cockpit_front_page --output-dir output --html-only
python -m runtime.build_cockpit_side_by_side_review --output-dir output
ls -la output/cockpit_preview/
ls -la output/cockpit_review/
```

Then clean generated files:

```bash
git clean -fd __pycache__ runtime/__pycache__ tests/__pycache__ tools/__pycache__ output/cockpit_preview output/cockpit_review
git status --short
```

## Remaining work

- Run validation in Codespaces.
- Confirm only the three control files are changed.
- Open PR: `Record cockpit promotion decision review`.
- After merge, start `WP_COCKPIT_SURFACE_06_COCKPIT_ITERATION_OR_PROMOTION_PATH` only if explicitly requested.
