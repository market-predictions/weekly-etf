# Weekly ETF report request

## Requested by
ChatGPT project workbench

## Purpose
Validate production send workflow after fixing Dutch macro-surface localization at source.

## Previous failure

The prior run reached `Build runtime ETF state and reports` and failed during `runtime.apply_nl_localization` because native Dutch output still contained English phrases:

```text
Keep SMH
Require replacement
earned leader
```

## Expected checks

The run should pass Dutch localization and then prove the runtime HTML delivery entrypoint enforces:

```text
ETF_MACRO_REPORT_PRE_SEND_GUARD_OK
ETF_MACRO_REPORT_SURFACE_OK
ETF_MACRO_COMPLIANCE_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

## Authority boundary

This request does not promote raw macro shadow internals, macro axes, macro axis scores, Stage-1 thesis candidates, or driver IDs to client-facing or portfolio-action authority.

## Delivery note

Delivery receipt work remains paused. Workflow success/send acceptance should not be overstated as recipient receipt.
