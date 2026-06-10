# Weekly ETF report request — WP11A-CONTENT-FIX retry

## Purpose

Retry WP11A-VERIFY after preserving English replacement-edge diagnostic notes through `runtime.fix_report_output_contract`.

## Previous failure classification

```text
failed step: Validate ETF report content contract
failing report: weekly_analysis_pro_260609_04.md
failure type: replacement-edge diagnostic notes missing/incomplete in English report
```

## Fix included before this retry

```text
eb312232d86e2f9ffac5133695b2cf69f71ea64f — Preserve replacement-edge notes in output contract fix
0229ede09541aa9b61b6ff8136d7610a426853b1 — Test output contract replacement-edge notes
```

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
