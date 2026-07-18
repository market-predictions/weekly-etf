# Handover — Cockpit trade-weight lineage fix

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Work package: `WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX`
Implementation PR: #109
Status: implementation complete / validated / awaiting merge

## Problem resolved

The cockpit action card could state that PAVE was added and XLU reduced while showing identical before-and-after weights. The action metadata was correct, but pre-trade weight and value fields had been overwritten by post-trade reconciliation.

## Implemented behavior

`runtime/trade_lineage.py` now owns the shared lineage contract:

- preserve or reconstruct `previous_shares`;
- preserve or reconstruct previous local/EUR market values;
- preserve official ledger `previous_weight_pct` and weight change where available;
- repair legacy overwritten state from recorded share and weight deltas;
- reject a material trade when the client-formatted one-decimal weights are identical;
- validate share-delta and weight-delta consistency.

The guarded execution path invokes this contract before persisting post-trade state. The report-state builder invokes it before exposing positions to the renderer. Current NAV remains based on current market value.

## Expected cockpit output

```text
PAVE added · XLU reduced
PAVE 0.0% → 4.9%; XLU 5.5% → 0.5%.
```

## Validation evidence

```text
validated_head: 81e61a5039d28a60a9056156054dec84a8691d29
trade_lineage_and_whole_share_run: 29665973984 success
trade_lineage_and_whole_share_job: 88136341408 success
report_request_authority_run: 29665973971 success
report_request_authority_job: 88136341429 success
```

Regression coverage includes helper behavior, official-ledger precedence, legacy reconstruction, report-state integration, no-trade positions, the identical-display failure gate and cockpit output.

## Protected state

No production report was generated or sent. The package did not intentionally mutate the official portfolio state, trade ledger, valuation history, pricing authority, runtime pointers, historical report files or delivery manifests.

## Follow-up after merge

1. Record the implementation merge SHA and CI results in the claim and work package.
2. Release the claim through a governance-only closeout.
3. Do not regenerate or resend the already delivered 2026-07-17 package without separate authorization.
4. The corrected lineage contract applies automatically to future report generation.
