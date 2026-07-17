# Handover — ETF Whole-Share State Contract

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_ETF_WHOLE_SHARE_STATE_CONTRACT`
Status: closed

## Current issue resolved

The official portfolio state and guarded model-execution path used fractional shares despite the decision-framework requirement `whole shares only`. A small leveraged `DFEN` remainder also conflicted with the active no-leverage constraint.

## Root cause

Notional-based execution divided value directly by price and persisted six-decimal quantities. No hard state validator, residual-cash contract or legacy migration path existed.

## Implemented architecture

### Input/state contract

```text
runtime/whole_share_contract.py
tools/reconcile_etf_whole_share_state.py
tools/validate_etf_whole_share_contract.py
```

### Execution contract

```text
runtime/model_execution_guarded_auto.py
tools/validate_etf_model_execution.py
```

### Operational runbook

```text
.github/workflows/validate-etf-whole-share-contract.yml
.github/workflows/reconcile-etf-whole-share-state.yml
```

### Governance

```text
control/work_packages/WP_ETF_WHOLE_SHARE_STATE_CONTRACT_20260717.md
control/work_package_claims/WP_ETF_WHOLE_SHARE_STATE_CONTRACT_20260717.md
control/decisions/ETF_WHOLE_SHARE_STATE_CONTRACT_DECISION_20260717.md
```

## Validation

```text
PR: #85
merge_commit: d5532ea15801a3888633ccb824797ab254305433
workflow_run: 29580018310
focused_tests: 4 passed
compile: passed
```

The focused suite proves:

- long-only fractional state is floored;
- explicit policy-close works;
- migration is idempotent;
- USD/EUR cent rounding never grants an unfunded extra unit;
- guarded Buy/Sell deltas are integers;
- unspent proceeds become cash;
- NAV remains unchanged.

## Official reconciliation

```text
request_commit: 3a54f5fb12be1c47420c0922ade4a82213bb3677
result_commit: 50b93740efbed537ed9d0daed6e1d88ce912be1e
source_runtime_state: output/runtime/etf_report_state_20260716_20260717_094728.json
artifact: output/runtime/etf_whole_share_reconciliation_20260716_20260717_094728.json
```

Result:

```text
adjusted_position_count: 10
ledger_rows_appended: 10
DFEN: policy closed
PAVE: fractional remainder below one share converted to cash
SPY: fractional remainder below one share converted to cash
cash_before_eur: 1936.52
cash_after_eur: 2519.05
cash_released_eur: 582.53
invested_before_eur: 105181.42
invested_after_eur: 104598.89
nav_before_eur: 107117.94
nav_after_eur: 107117.94
nav_drift_eur: 0.00
whole_share_validation_errors: []
```

Current official positions:

```text
CIBR 253
GSG 374
IEFA 312
SMH 59
URNM 48
XBI 40
XLU 148
XLV 37
```

## Authority boundary

The delivered `260716` English/Dutch report package was generated before the reconciliation. It remains historical delivery evidence. Current portfolio holdings and cash are authoritative only from `output/etf_portfolio_state.json` until the next fresh report is generated.

No email was sent during this package. No pricing, lane-scoring, macro or cockpit-enablements authority changed.

## Next action

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

WP11 must use the whole-share-compliant official state, perform an exact-current validate-only enabled production-bundle replay before any send, preserve one-flag rollback to `disabled`, and keep state, pricing and ledger immutable during validation.
