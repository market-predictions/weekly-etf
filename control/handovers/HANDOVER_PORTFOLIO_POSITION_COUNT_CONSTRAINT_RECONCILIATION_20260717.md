# Handover — Portfolio Position-Count Constraint Reconciliation

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION`
Status: implementation complete / validation green / merge pending
Pull request: #91

## Current issue

The official portfolio has nine non-zero whole-share positions while the active constraint allows eight. This arose because the completed `XLU -> PAVE` rotation left a residual 14-share XLU position and opened 107 PAVE shares.

Current official state remains:

```text
CIBR 253
GSG 374
IEFA 312
PAVE 107
SMH 59
URNM 48
XBI 40
XLU 14
XLV 37
cash_eur: 2534.36
nav_eur: 107117.94
active_position_count: 9
maximum_active_positions: 8
position_count_status: close_first
```

## Root cause

The earlier whole-share contract correctly prevented fractional holdings, but the execution path did not separately test whether a partial source reduction plus a new destination increased the number of active tickers. Target-weight and whole-share correctness therefore coexisted with a position-count breach.

## Decision

Every unique ticker with positive shares counts. There is no generic residual exception.

Stable rules:

1. zero-share positions do not count;
2. duplicate active ticker rows are invalid;
3. the default maximum is eight;
4. a no-trade run may preserve an above-limit state as `close_first`;
5. any proposed trade while above the limit must reduce the active count and may not introduce a new ticker;
6. at the limit, opening a new ticker requires another ticker to reach zero shares in the same projected whole-share transition;
7. a partial reduction that leaves positive shares does not free a slot.

## Recommended change implemented

### Decision framework

`runtime/position_count_contract.py` defines deterministic current-state and projected-transition assessments.

### Input/state contract

`tools/validate_etf_persisted_valuation_state.py` now projects the intended post-trade whole-share portfolio before guarded mutation. A breach raises before `runtime.model_execution_guarded_auto` can write official state or ledger rows.

### Output contract

`runtime/position_count_report_surface.py` and `tools/validate_etf_client_surface_clean.py` add a client-safe EN/NL disclosure only when the current report ticker set exactly matches official state. Historical reports with different ticker sets remain unchanged.

### Operational runbook

The existing production sequence already invokes the persisted-valuation validator immediately before guarded execution. No new production step or separate mutation authority is introduced.

## Exact files changed

```text
runtime/position_count_contract.py
runtime/position_count_report_surface.py
tools/validate_etf_persisted_valuation_state.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_position_count_contract.py
tests/test_etf_position_count_contract.py
.github/workflows/validate-etf-position-count-contract.yml
.github/workflows/recover-weekly-etf-delivery-20260717.yml
control/work_packages/WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
control/work_package_claims/WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
control/ETF_SESSION_CHANGELOG.md
```

The closed recovery workflow was made receipt-aware because its historic package has already been delivered. PR validation now validates the existing receipt and cannot re-send it.

## Validation

```text
validated_head: 07c4f32456d50a6f624f664cfa87970e9c8dec76
primary_run: 29617207278
primary_job: 88004737784
primary_result: success
focused_tests: 13 passed
artifact_id: 8420903168
artifact_digest: sha256:cf98f8d4b4d172bc4f463598a557e8490fd2f188bbd5ae3f0c34347ee1688b5b
report_surface_regression_run: 29617207295 success
closed_recovery_regression_run: 29617207264 success
fresh_send_diagnostic_regression_run: 29617207249 success
```

Proven:

```text
current_state: close_first 9/8
partial residual plus new ticker at limit: blocked
full source close plus new ticker at limit: allowed
over-limit plus new ticker: blocked
over-limit count-reducing close: allowed
zero-share positions: excluded
duplicate active tickers: rejected
protected authority hashes: identical
historical report hashes: identical
portfolio execution: false
email sent: false
```

Persistent evidence:

```text
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
```

## Current authority and operational meaning

This package does not decide which holding should be closed. In particular, it does not automatically instruct a sale of the 14-share XLU residual. The next count-reducing action must use current pricing, scores, relative strength, role evidence and funding logic.

Until the count is restored:

```text
new_ticker_opening: blocked
no-trade review: allowed
trade into an existing holding with one full closure: allowed if otherwise authorized
close to cash: allowed if otherwise authorized
partial reduction that preserves nine active positions: blocked
```

## Next action

Create a separate explicitly scoped package:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
```

That package should use fresh evidence to choose whether and how to reduce the active count from nine to no more than eight. It must not assume XLU is the correct source solely because it is the smallest position. Any real mutation or report delivery requires separate explicit authorization and the normal manifest/receipt controls.

## Merge and claim closeout

Before final closure:

1. merge PR #91 after final same-head governance validation;
2. record the exact merge commit in this handover;
3. mark the work package closed;
4. mark the claim closed/released;
5. retain the official nine-position state unchanged until a separately authorized count-reducing package executes.
