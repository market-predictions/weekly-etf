# Weekly ETF report request — WP11A-NL-TERMINOLOGY retry

## Purpose

Retry WP11A-VERIFY after restoring `runtime.nl_localization` alias identity to the central `runtime.nl_terminology` maps.

## Previous failure classification

```text
failed step: Validate Dutch language quality contract
failing command: python tools/validate_nl_terminology_contract.py
failure type: Dutch terminology alias identity contract failure
```

## Exact previous failure

```text
ContractError: ACTION_REPLACEMENTS is not sourced from runtime.nl_terminology
```

## Fix included before this retry

```text
51998e242bb573bb6be55145fe355558b8e9f75b — Source NL localization aliases from central terminology
bfc32d8039ccb5f3c9682892399da8279de29b09 — Record WP11A NL terminology fix
```

## Local validation

```text
ETF_NL_TERMINOLOGY_CONTRACT_OK | source=runtime.nl_terminology
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
