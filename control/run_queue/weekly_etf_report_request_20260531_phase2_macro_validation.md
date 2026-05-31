# Weekly ETF Report Request

## Requested at
2026-05-31

## Mode
fresh_weekly_etf_report

## Purpose
Run a fresh Weekly ETF Review workflow after Phase 2 macro audit foundation implementation.

## Validation focus

The run should verify the existing production baseline plus the new shadow-mode macro audit foundation.

Expected macro markers:

```text
ETF_MACRO_DATA_AUDIT_OK
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_POLICY_PACK_OK ... macro_audit_present=True
```

Expected pricing-lineage markers:

```text
ETF_PRICING_LINEAGE_CONTRACT_OK
ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK
```

## Authority rule
The Phase 2 macro audit remains shadow-only. It must not change regime, confidence, lane scoring, fundability, portfolio actions, or client-facing report wording.

## Notes
This file is a run-queue trigger only. It is not a report artifact and should not be treated as client-facing output.
