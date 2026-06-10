# Weekly ETF report request — WP11A-POLICY-CAP retry

## Purpose

Retry WP11A-VERIFY after capping model execution source reductions to the existing policy limit.

## Repository

```text
market-predictions/weekly-etf
```

## Prior failure status

The observe retry exposed the real shadow model-execution blocker:

```text
ETF_MODEL_EXECUTION_BLOCKED | artifact=output/runtime/etf_model_execution_20260609_20260610_181023.json | errors=source_reduction_exceeds_policy:SPY:5.23>5.00
```

The workflow had already passed:

```text
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_NL_DATE_LOCALIZATION_OK
ETF_LINKIFY_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

## Fix included before this retry

```text
951a72c4492cfc72ab46289def755606d35a309c — Cap model execution source reductions to policy
```

The fix enforces the existing runtime policy cap:

```text
max_single_source_reduction_pct_nav=5.00
```

The prior SPY request should now be capped from 5.23% requested to 5.00% executable, with a warning similar to:

```text
source_notional_capped_to_policy:SPY:5555.27->5312.32
```

## Requested validation focus

```text
WP11A-VERIFY — Validate replacement-edge diagnostic notes in CI/fresh report output after model execution source-reduction cap
```

## Required replacement-edge marker

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

## Required model-execution behavior

Shadow model execution should pass the previously failing source-reduction gate or expose the next blocker clearly.

Expected successful shape:

```text
ETF_MODEL_EXECUTION_OK | artifact=... | mode=shadow | trades=1 | status=shadow_ready
```

Expected policy-cap metadata in artifact:

```text
policy_checks.passed=true
policy_checks.errors=[]
source_delta_weight_pct=-5.0
destination_delta_weight_pct=5.0
notional_cap_reason=policy
```

## Authority boundary that must remain preserved

Replacement-edge notes remain diagnostic-only:

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
