# Handover — Cockpit trade-weight lineage fix

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Work package: `WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX`
Implementation PR: #109
Implementation merge: `85d82930e40d37c145727d14468dc8914e041e00`
Status: closed / merged / validated / claim released

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

## Final validation evidence

```text
validated_head: 5aefd9237bbbace490bda3aad0dcb722acd0b05d
trade_lineage_and_whole_share_run: 29666054365 success
trade_lineage_and_whole_share_job: 88136546831 success
report_request_authority_run: 29666054332 success
report_request_authority_job: 88136546755 success
implementation_merge: 85d82930e40d37c145727d14468dc8914e041e00
merged_at_utc: 2026-07-18T23:56:26Z
```

Regression coverage includes helper behavior, official-ledger precedence, legacy reconstruction, report-state integration, no-trade positions, the identical-display failure gate and cockpit output.

## Protected state

No production report was generated or sent. The package did not intentionally mutate the official portfolio state, trade ledger, valuation history, pricing authority, runtime pointers, historical report files or delivery manifests.

## Operational status

The corrected lineage contract is active on `main` and applies automatically to future report generation. The already delivered 2026-07-17 package remains immutable and must not be regenerated or resent without separate authorization.
