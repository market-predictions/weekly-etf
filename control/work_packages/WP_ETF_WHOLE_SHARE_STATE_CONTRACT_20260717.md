# WP_ETF_WHOLE_SHARE_STATE_CONTRACT

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Layer: input/state contract + operational runbook
Status: implementation complete / validation pending

## Current issue

The production masterprompt requires whole shares, but the official portfolio state and guarded model-execution path historically stored fractional share quantities. The latest production run persisted fractional holdings and fractional Buy/Sell deltas. This creates a direct conflict between the decision framework and the machine-readable state contract.

The current state also retains a small `DFEN` position although the current constraints state that leveraged ETFs are not allowed.

## Root cause

1. `runtime/model_execution_engine.py` converts EUR notional directly to shares.
2. `_mark_position()` stores the resulting quantity at six decimal places.
3. Guarded execution kept cash unchanged because source and destination notionals were identical before share rounding.
4. No validator rejected fractional official positions or fractional guarded Buy/Sell deltas.
5. Legacy fractional positions had no explicit migration path.

## Required change

1. Add a reusable whole-share state contract.
2. Block guarded execution when the official pre-trade state is fractional.
3. Round source sales and destination purchases down to executable whole units.
4. Preserve pre-trade NAV by transferring the difference to residual EUR cash.
5. Validate official positions, guarded artifacts and official Buy/Sell deltas.
6. Add an explicit, idempotent reconciliation tool for legacy fractional positions.
7. Close `DFEN` during the one-time reconciliation because it conflicts with the current no-leverage constraint.
8. Record every legacy adjustment in the official trade ledger and a machine-readable reconciliation artifact.

## Exact files

```text
runtime/whole_share_contract.py
runtime/model_execution_guarded_auto.py
tools/reconcile_etf_whole_share_state.py
tools/validate_etf_whole_share_contract.py
tools/validate_etf_model_execution.py
tests/test_etf_whole_share_contract.py
.github/workflows/validate-etf-whole-share-contract.yml
.github/workflows/reconcile-etf-whole-share-state.yml
```

## Authority rules

- Whole-share compliance applies to official portfolio state and new guarded Buy/Sell mutations.
- Legacy fractional remainders may appear only in one-time reconciliation ledger rows.
- Long-only legacy fractions are floored, never rounded up.
- Explicit policy-forbidden tickers may be fully closed by the reconciliation run.
- Released value and unspent rotation proceeds become EUR cash.
- NAV drift must remain within EUR 0.05.
- The reconciliation workflow may mutate portfolio state and trade ledger only after explicit request-file authorization.
- The package may not send email, rewrite a delivered report or enable the cockpit front page.

## Acceptance criteria

```text
focused tests: pass
Python compile: pass
legacy reconciliation idempotent: true
post-reconciliation official shares: integers
new guarded Buy/Sell deltas: integers
NAV drift tolerance: <= EUR 0.05
DFEN after one-time reconciliation: absent
email_sent: false
cockpit_enablement_changed: false
```

## Execution sequence

1. Merge implementation after focused validation.
2. Create `control/run_queue/etf_whole_share_reconciliation_request_*.md` on `main`.
3. Reconcile using runtime state `output/runtime/etf_report_state_20260716_20260717_094728.json`.
4. Close `DFEN` explicitly.
5. Validate and commit official state, trade ledger and reconciliation artifact.
6. Update `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md` and the decision log.
7. Resume WP11 only after whole-share evidence is persisted.
