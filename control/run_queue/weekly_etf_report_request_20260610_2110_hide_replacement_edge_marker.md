# Weekly ETF report request — hide replacement-edge marker

## Purpose

Retry ETF delivery after hiding the replacement-edge diagnostic notes marker from client-facing report output.

## Fix included before this retry

```text
Stop emitting replacement-edge marker in reports
Detect replacement-edge notes without marker
Forbid replacement-edge marker in report contract
Test replacement-edge marker hidden from reports
```

## Validation focus

Fresh English and Dutch Markdown, HTML, and PDF outputs must not contain:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
<!-- ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED -->
&lt;!-- ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED --&gt;
```

## Authority boundary that must remain preserved

The replacement-edge notes remain diagnostic-only and must keep the no-authority disclaimer.

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

This retry must not promote replacement-edge diagnostics into:

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
