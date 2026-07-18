# Work Package — WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Status: claimed / implementation in progress

## Current issue

The client cockpit correctly identifies the executed PAVE/XLU rotation, but its supporting before-and-after line can show identical weights, for example `PAVE 4.9% → 4.9%; XLU 0.5% → 0.5%`.

## Root cause

The guarded whole-share execution path calculates correct pre-trade and post-trade weights for the official ledger, but the subsequent cash reconciliation overwrites `previous_weight_pct`, `previous_market_value_*` and inherited weight fields with post-trade values. The report-state revaluation path can then repeat the overwrite while retaining a material `shares_delta_this_run` and `weight_change_pct`.

The state contract does not currently preserve explicit pre-trade shares, and no validation gate rejects a material trade whose formatted before-and-after weights are identical.

## Decision framework

1. Preserve an immutable pre-trade snapshot for each executed position: shares, local/EUR market value and portfolio weight.
2. Keep current/post-trade valuation fields independently revaluable.
3. Reconstruct legacy corrupted snapshots deterministically from current quantity plus recorded run deltas when authoritative pre-trade fields are absent or demonstrably overwritten.
4. Reject material executed trades when the client-formatted before and after weights remain identical.
5. Validate quantity, value and weight lineage against recorded deltas.
6. Preserve portfolio NAV, official shares, trade ledger and historical delivered reports.

## Intended implementation

```text
runtime/model_execution_engine.py
runtime/model_execution_guarded_auto.py
runtime/build_etf_report_state.py
runtime/finalize_executed_etf_report.py
runtime/render_cockpit_front_page.py
runtime/trade_lineage.py
tools/validate_etf_model_execution.py
tests/test_etf_trade_lineage.py
control/ETF_SESSION_CHANGELOG.md
control/CURRENT_STATE.md
```

The exact file set may be reduced if a shared lineage helper eliminates duplicate changes.

## Acceptance criteria

- PAVE-like new purchases preserve a zero pre-trade quantity and weight.
- XLU-like reductions preserve the full pre-trade quantity and weight.
- post-trade revaluation does not overwrite immutable pre-trade fields;
- a material executed trade cannot render identical one-decimal before/after weights;
- no-trade positions remain valid and retain current-weight defaults;
- legacy persisted rows with non-zero deltas and overwritten previous fields are repaired in report state without mutating official portfolio state;
- EN and NL cockpit action lines remain aligned;
- focused tests and existing execution/report contract tests pass;
- no report generation, email delivery, portfolio execution or trade-ledger mutation is performed by this package.

## Authority boundary

```text
portfolio_state_write: forbidden
trade_ledger_write: forbidden
valuation_history_write: forbidden
pricing_authority_change: forbidden
historical_report_mutation: forbidden
production_report_generation: forbidden
email_send: forbidden
```
