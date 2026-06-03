# Weekly ETF report request

## Requested by
ChatGPT project workbench

## Purpose
Final production verification after completing source-level Dutch macro dashboard localization in `runtime/macro_report_surface.py`.

## Previous status

The prior production run succeeded, but the generated Dutch Regime Dashboard still showed two English macro-pack sentences:

```text
Risk-on narrow leadership has persisted...
Do not rotate aggressively unless...
```

A source-level fix was added in commit `b6631167ea94483eff127b6675437882a26e7c29`.

## Expected checks

The run should confirm:

```text
workflow_success
pricing_lineage_status: passed
ETF_NL_LOCALIZATION_OK
ETF_MACRO_REPORT_PRE_SEND_GUARD_OK
```

The generated Dutch report should no longer contain the English macro memory / decision-rule sentences above.

## Authority boundary

This request does not promote raw macro shadow internals, macro axes, macro axis scores, Stage-1 thesis candidates, or driver IDs to client-facing or portfolio-action authority.

## Delivery note

Delivery receipt work remains paused. Workflow success/send acceptance should not be overstated as recipient receipt.
