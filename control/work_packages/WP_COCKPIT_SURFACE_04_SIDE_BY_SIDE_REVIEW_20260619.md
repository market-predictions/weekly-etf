# WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-side-by-side-review`
Layer: output contract + operational runbook
Status: implemented / locally validated

## Purpose

Produce deterministic side-by-side review artifacts comparing the classic Weekly ETF report surface against the cockpit preview surface.

## Scope

Review-only. The cockpit remains preview-only and `promotion_status` remains `not_promoted`.

## Output path

```text
output/cockpit_review/
```

## Protected paths

State, pricing, runtime, run-manifest, delivery, cockpit preview, and production report artifacts are read-only for this package.

## Validation evidence

```text
31 passed in 2.39s
ETF_DELIVERY_HTML_CONTRACT_OK for EN/NL 260618_04
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
COCKPIT_PREVIEW_OK for EN/NL
COCKPIT_SIDE_BY_SIDE_REVIEW_OK token=260618 promotion_status=not_promoted
git diff --check clean
```

## Acceptance

- focused tests pass
- production validators remain green
- review artifacts generate locally
- no protected artifacts are changed
- handover records no-promotion status
