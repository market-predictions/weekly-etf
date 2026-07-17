# Decision — Portfolio Position-Count Constraint Reconciliation

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION`
Status: approved and validated; merge pending

## Decision

Every unique ticker with `shares > 0` counts as one active position. Zero-share rows do not count. Duplicate active ticker rows are invalid. The default maximum is eight active positions. There is no generic exception for a small residual holding.

The current official state contains nine active positions and is therefore classified `close_first`. This package records and enforces that state without changing it.

## Stable transition rules

1. While the current count is above eight, a proposed transition may not introduce a new ticker.
2. While above eight, a proposed transition must reduce the active count.
3. At exactly eight, a new ticker requires another active ticker to reach zero shares in the same projected whole-share transition.
4. A partial reduction that leaves positive shares does not free a slot.
5. Validation uses projected whole-share quantities rather than requested percentages.

## Output rule

A current report whose holdings exactly match official state must disclose both the maximum and actual count when above the limit. Historical reports with a different ticker set remain unchanged.

English:

```text
Maximum active positions: 8. Current active positions: 9. No new position may be opened until the count is restored.
```

Dutch:

```text
Maximaal aantal actieve posities: 8. Huidig aantal actieve posities: 9. Er mag geen nieuwe positie worden geopend totdat het aantal is hersteld.
```

## Authority boundary

This package changes no holdings, ledger rows, valuation history, pricing authority, or historical report files. It sends no email. Restoring the active count requires a separate future package using current evidence.
