# Work Package — WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Status: active / claimed

## Current issue

The official portfolio state contains nine non-zero whole-share positions, while the production constraint states a maximum of eight positions. The mismatch arose when guarded execution reduced `XLU` to 14 shares while opening `PAVE` with 107 shares.

This package must reconcile the decision rule and execution contract without silently changing current holdings and without sending a report.

## Decision framework

Selected rule: **every non-zero position counts toward the maximum**.

Consequences:

1. `shares > 0` means an active position and counts toward the position limit.
2. Zero-share positions do not count and must not remain in official state.
3. No generic residual-position exemption exists.
4. When the portfolio is already above the limit, it enters `close_first` status: guarded execution may only preserve or reduce the active count and may not open a new ticker.
5. When the portfolio is at the limit, opening a new ticker requires one existing source position to reach zero shares in the same execution.
6. A partial reduction that leaves the source non-zero cannot fund a new ticker when it would breach the limit.

The current nine-position state is not mutated by this package. It is recorded as a temporary contract breach requiring count-reducing execution before another new ticker may be opened.

## Input/state contract

Authority:

```text
output/etf_portfolio_state.json
```

Required machine rules:

- count unique tickers with whole-share `shares > 0`;
- reject duplicate active tickers;
- default maximum active positions to `8`;
- allow an explicit machine-readable maximum only when present in the runtime rotation policy;
- simulate intended post-trade whole-share quantities before any guarded write;
- fail closed when the intended post-trade count exceeds the maximum or an already-over-limit state does not reduce its count;
- preserve current state, ledger and valuation files during this package.

## Output contract

Future English and Dutch reports must not state `Max number of positions: 8` without also presenting the actual official count when the state is above the limit.

Client-safe language for a breach:

```text
Maximum active positions: 8. Current active positions: 9. No new position may be opened until the count is restored.
```

Dutch:

```text
Maximaal aantal actieve posities: 8. Huidig aantal actieve posities: 9. Er mag geen nieuwe positie worden geopend totdat het aantal is hersteld.
```

No raw override, workflow, policy-check or internal error terminology may leak into the client surface.

## Operational runbook

Implement:

1. a shared position-count contract module;
2. guarded-execution preflight integration before official writes;
3. a current-state validator/evidence builder;
4. focused tests for:
   - reduce-to-residual plus new ticker at the limit: blocked;
   - full source close plus new ticker at the limit: allowed;
   - already-over-limit plus another new ticker: blocked;
   - already-over-limit count-reducing close: allowed;
   - zero-share positions excluded;
   - duplicate active tickers rejected;
5. a GitHub Actions validation workflow.

## Non-goals and authority boundary

This package must not:

- execute trades;
- change `output/etf_portfolio_state.json`;
- append ledger rows;
- change valuation history;
- rewrite historical reports;
- send email;
- weaken whole-share or NAV-drift controls.

## Acceptance criteria

- package and claim are recorded before implementation;
- every non-zero position deterministically counts;
- guarded execution fails closed before mutation on a count breach;
- the existing nine-position official state is classified `close_first` without mutation;
- focused tests pass;
- protected authority hashes remain unchanged;
- persistent evidence and decision records are written;
- PR is merged;
- claim and package are closed;
- handover, `CURRENT_STATE.md`, `NEXT_ACTIONS.md`, `DECISION_LOG.md`, and `ETF_SESSION_CHANGELOG.md` are updated;
- no report or email is sent.
