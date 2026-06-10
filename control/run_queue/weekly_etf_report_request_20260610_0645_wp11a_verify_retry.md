# Weekly ETF report request — WP11A-VERIFY retry

## Purpose

Retry WP11A-VERIFY fresh report validation after the previous run reached the final artifact commit step but failed to push because `main` had advanced during the workflow run.

## Reason for retry

```text
previous failure type: non-fast-forward push race
failed step: Commit ETF run artifacts back to main
observed error: HEAD -> main (fetch first)
classification: operational push race, not replacement-edge validation failure
```

## Requested validation focus

```text
WP11A-VERIFY — Validate replacement-edge diagnostic notes in CI/fresh report output
```

The workflow should render fresh English and Dutch reports, run the normal report-output validators, and prove that the updated report content contract accepts the replacement-edge diagnostic notes marker and diagnostic-only authority disclaimer.

## Required marker

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

## Authority boundary that must remain preserved

```text
diagnostic_only=true
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
production_recommendation_authority=false
execution_authority=false
portfolio_mutation=false
```

## No-authority-promotion constraints

This validation run must not promote replacement-edge diagnostics into:

```text
ranking
lane scoring
fundability
recommendation
target weights
trade intents
execution
portfolio mutation
```

## Operational note

Avoid additional direct commits to `main` while this workflow is running, otherwise the final artifact push can fail again with a non-fast-forward rejection.
