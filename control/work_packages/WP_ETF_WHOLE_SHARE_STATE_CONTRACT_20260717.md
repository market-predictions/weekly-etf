# WP_ETF_WHOLE_SHARE_STATE_CONTRACT

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Layer: input/state contract + operational runbook
Status: closed

## Current issue

The production framework required whole shares, while official state and guarded model execution stored fractional quantities. The latest state also retained a leveraged `DFEN` remainder despite the active no-leverage constraint.

## Root cause

1. Notional was converted directly to fractional shares.
2. Execution persisted six-decimal quantities.
3. No residual-cash contract reconciled whole-unit source and destination values.
4. No validator blocked fractional official state or guarded Buy/Sell deltas.
5. Legacy fractional state had no explicit migration path.

## Implemented change

1. Added `runtime/whole_share_contract.py`.
2. Guarded execution now blocks fractional pre-trade official state.
3. Source sales and destination purchases are floored to whole units.
4. Unspent proceeds become explicit EUR cash.
5. Guarded NAV drift is limited to EUR 0.05.
6. Added official-state and execution-artifact validators.
7. Added an idempotent one-time reconciliation tool and request-file workflow.
8. Added focused tests covering migration, idempotency, FX rounding, integer deltas, residual cash and NAV preservation.
9. Reconciled the official state using the persisted 2026-07-16 pricing and FX basis.
10. Closed `DFEN` under the active no-leverage policy.

## Files

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

## Validation evidence

```text
implementation_PR: #85
implementation_merge: d5532ea15801a3888633ccb824797ab254305433
validation_run: 29580018310
compile: passed
focused_tests: 4 passed
reconciliation_request_commit: 3a54f5fb12be1c47420c0922ade4a82213bb3677
reconciliation_commit: 50b93740efbed537ed9d0daed6e1d88ce912be1e
reconciliation_artifact: output/runtime/etf_whole_share_reconciliation_20260716_20260717_094728.json
```

Reconciliation result:

```text
status: reconciled
adjusted_position_count: 10
ledger_rows_appended: 10
policy_closed_tickers: DFEN
cash_before_eur: 1936.52
cash_after_eur: 2519.05
cash_released_eur: 582.53
invested_before_eur: 105181.42
invested_after_eur: 104598.89
nav_before_eur: 107117.94
nav_after_eur: 107117.94
nav_drift_eur: 0.00
whole_share_validation_errors: []
portfolio_state_written: true
trade_ledger_written: true
email_sent: false
cockpit_enablement_changed: false
```

## Stable authority rules

- Official positions and future guarded Buy/Sell mutations use whole shares.
- Long-only quantities are floored and never rounded upward beyond funded or available capacity.
- Released value and unspent proceeds remain explicit EUR cash.
- Guarded execution fails closed when official state is fractional.
- Legacy fractional deltas remain historical reconciliation evidence only.
- NAV drift after reconciliation or guarded execution may not exceed EUR 0.05.

## Closeout

All implementation, validation, migration, ledger-evidence, state-persistence and NAV-preservation gates are satisfied. The package is closed. WP11 cockpit production enablement may resume using the reconciled official state.
