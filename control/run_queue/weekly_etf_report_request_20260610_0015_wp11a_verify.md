# Weekly ETF report request — WP11A-VERIFY

## Purpose

Validate WP11A-FIX replacement-edge diagnostic notes in fresh CI/report output.

## Requested validation focus

```text
WP11A-VERIFY — Validate replacement-edge diagnostic notes in CI/fresh report output
```

The workflow should render fresh English and Dutch reports, run the normal report-output validators, and specifically prove that the updated report content contract accepts the replacement-edge diagnostic notes marker and diagnostic-only authority disclaimer.

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

## Notes

This is a validation request only. No feature implementation is requested by this run-queue file.
