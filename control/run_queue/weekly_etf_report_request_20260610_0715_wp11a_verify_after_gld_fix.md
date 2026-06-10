# Weekly ETF report request — WP11A-VERIFY after Dutch GLD surface fix

## Purpose

Retry WP11A-VERIFY after fixing stale Dutch GLD client-surface wording in the native Dutch report renderer.

## Previous failure classification

```text
failed step: Build runtime ETF state and reports
failing module: runtime.scrub_nl_client_language
failure type: Dutch client-surface guard failure
root cause: stale fixed GLD wording in native Dutch report surface while GLD is no longer active
```

## Fix included before this retry

```text
48d0b475416772f9428ccee5830925668f1c111d — Remove stale GLD wording from native Dutch report surface
```

## Requested validation focus

```text
WP11A-VERIFY — Validate replacement-edge diagnostic notes in CI/fresh report output
```

The workflow should render fresh English and Dutch reports, run the normal report-output validators, and prove that the updated report content contract accepts the replacement-edge diagnostic notes marker and diagnostic-only authority disclaimer.

## Required replacement-edge marker

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

Avoid additional direct commits to `main` while this workflow is running, otherwise the final artifact push can fail with a non-fast-forward rejection.
