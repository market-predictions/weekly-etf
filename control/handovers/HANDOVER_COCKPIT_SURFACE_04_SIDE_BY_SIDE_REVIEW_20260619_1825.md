# Handover — WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-side-by-side-review`
Status: implemented / locally validated

## Summary

This package adds deterministic side-by-side review generation for the US Weekly ETF cockpit preview lane.

Added files:

```text
runtime/build_cockpit_side_by_side_review.py
tests/test_cockpit_side_by_side_review.py
control/work_packages/WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW_20260619_1825.md
```

## Output contract

The builder writes review-only artifacts under:

```text
output/cockpit_review/
```

Expected generated files:

```text
weekly_etf_cockpit_side_by_side_review_<token>.md
weekly_etf_cockpit_side_by_side_review_<token>.html
weekly_etf_cockpit_side_by_side_review_nl_<token>.md
weekly_etf_cockpit_side_by_side_review_nl_<token>.html
weekly_etf_cockpit_side_by_side_review_<token>.json
```

## No-promotion status

```text
promotion_status: not_promoted
```

The cockpit remains preview-only. This package does not promote the cockpit into production and does not change production report generation or delivery behavior.

## Mutation boundary

The implementation writes only to `output/cockpit_review/` during local generation and leaves state, pricing, runtime, run-manifest, delivery, cockpit-preview, and classic production report artifacts unchanged.

## Validation evidence

Codespaces validation completed successfully:

```text
31 passed in 2.39s
ETF_DELIVERY_HTML_CONTRACT_OK | report=weekly_analysis_pro_260618_04.md | post_execution=False
ETF_DELIVERY_HTML_CONTRACT_OK | report=weekly_analysis_pro_nl_260618_04.md | post_execution=False
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
COCKPIT_PREVIEW_OK | language=en | pdf=not_rendered
COCKPIT_PREVIEW_OK | language=nl | pdf=not_rendered
COCKPIT_SIDE_BY_SIDE_REVIEW_OK | token=260618 | promotion_status=not_promoted
git diff --check clean
```

Generated local review artifacts were observed under:

```text
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260618.json
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260618.md
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260618.html
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260618.md
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260618.html
```

## Required cleanup before PR

```bash
git clean -fd __pycache__ runtime/__pycache__ tests/__pycache__ tools/__pycache__ output/cockpit_preview output/cockpit_review
git pull --ff-only origin feature/cockpit-side-by-side-review
git status --short
```

## Remaining work

- Clean generated local artifacts.
- Pull the validation-status commits from the branch.
- Open PR: `Add cockpit side-by-side review artifacts`.
- After merge, continue with `WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW`.
