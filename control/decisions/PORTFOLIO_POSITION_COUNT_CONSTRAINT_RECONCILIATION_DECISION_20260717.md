# Decision — Portfolio Position-Count Constraint Reconciliation

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION`
Status: approved / implemented / merged / active authority
Implementation PR: #91
Implementation merge: `0bcb6af7e243775d876b59719ce9898fa97c690f`

## Decision

Every unique ticker with `shares > 0` counts as one active position. Zero-share rows do not count. Duplicate active ticker rows are invalid. The default maximum is eight active positions. There is no generic exception for a small residual holding.

The current official state contains nine active positions and is therefore classified `close_first`. This package records and enforces that state without changing it.

## Stable transition rules

1. A no-trade review may preserve an above-limit official state while reporting `close_first`.
2. While the current count is above eight, a proposed transition may not introduce a new ticker.
3. While above eight, any proposed trade must reduce the active count.
4. At exactly eight, a new ticker requires another active ticker to reach zero shares in the same projected whole-share transition.
5. A partial reduction that leaves positive shares does not free a slot.
6. Validation uses projected whole-share quantities rather than requested percentages.
7. The preflight must pass before guarded execution may mutate official state or append ledger rows.

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

## Operational consequence

Until the official count is restored:

```text
new ticker opening: blocked
no-trade review: allowed
count-reducing close to cash: eligible only after separate authorization
full close with reallocation to an existing holding: eligible only after separate authorization
partial reduction preserving nine positions: blocked
```

This decision does not identify the correct closure source. It does not grant automatic authority to sell XLU merely because XLU is the smallest position.

## Validation and evidence

```text
focused tests: 13 passed
final position-count run: 29618185729 success
final report-surface run: 29618185736 success
final current-runtime cockpit run: 29618185701 success
final WP08 run: 29618185711 success
final WP11 run: 29618185709 success
final recovery run: 29618185751 success
final fresh-send diagnostic run: 29618185706 success
protected authority hashes: identical
historical report hashes: identical
portfolio execution: false
email sent: false
```

Persistent evidence:

```text
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
control/DECISION_LOG.md
```

## Authority boundary

This package changed no holdings, ledger rows, valuation history, pricing authority, or historical report files. It sent no email.

Restoring the active count requires a separately claimed `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW` using fresh current evidence. Any resulting portfolio mutation or delivery remains separately authorized.
