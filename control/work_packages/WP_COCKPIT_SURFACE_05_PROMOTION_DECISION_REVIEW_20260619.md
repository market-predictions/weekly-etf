# WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-promotion-decision-review`
Layer: decision framework only
Status: claimed / in_progress

## Purpose

Record the explicit cockpit promotion decision after the preview renderer, manual preview workflow, visual/state-safety contracts, and side-by-side review package.

## Scope

Decision-only. This package must not implement promotion, change production report rendering, change delivery behavior, mutate state, update pricing, update trade ledger files, or edit runtime/workflow files.

## Decision boundary

Passing tests proves the cockpit preview lane is safe and reviewable. Passing tests does not authorize production promotion.

## Files to add

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
