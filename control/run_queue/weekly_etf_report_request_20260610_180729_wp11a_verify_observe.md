# Weekly ETF report request — WP11A-VERIFY-OBSERVE

## Purpose

Retry WP11A-VERIFY after adding model-execution observability for hidden policy/input failures.

## Repository

```text
market-predictions/weekly-etf
```

## Prior failure status

The previous retry passed the earlier Dutch GLD/client-surface blocker and reached further into the report-build step.

Observed successful markers:

```text
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_NL_DATE_LOCALIZATION_OK
ETF_LINKIFY_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

The remaining failure appeared to happen inside shadow model execution, but the exact error line was hidden because the workflow captured stdout before the command exited.

## Observability fix included before this retry

```text
887722cc638778ee44809b6556aa54c7ca72f569 — Expose model execution policy failures on stderr
```

The fix makes `runtime.model_execution_engine` print the same `ETF_MODEL_EXECUTION_BLOCKED` message to stderr before `SystemExit(1)`.

## Requested validation focus

```text
WP11A-VERIFY-OBSERVE — Validate replacement-edge diagnostic notes in CI/fresh report output and expose model-execution policy errors if still failing
```

## Required replacement-edge marker

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

## Required failure visibility if model execution still blocks

If shadow model execution fails, GitHub Actions logs must now show a line like:

```text
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=...
```

Expected possible error types include:

```text
source_not_in_portfolio:...
trade_price_invalid:...
trade_below_min_size_after_source_cap:...
source_has_no_executable_value:...
source_reduction_exceeds_policy:...
major_rotation_count_exceeds_policy:...
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
