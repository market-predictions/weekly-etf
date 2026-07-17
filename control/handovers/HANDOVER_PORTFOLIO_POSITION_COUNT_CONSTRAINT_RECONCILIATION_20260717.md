# Handover — Portfolio Position-Count Constraint Reconciliation

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION`
Status: closed / merged / claim released
Implementation pull request: #91
Implementation merge: `0bcb6af7e243775d876b59719ce9898fa97c690f`
Closeout pull request: #92

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

No position, cash amount, ledger row or valuation record was changed by this package.

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
7. a partial reduction that leaves positive shares does not free a slot;
8. validation uses projected whole-share quantities, not target percentages alone.

## Change implemented

### Decision framework

`runtime/position_count_contract.py` defines deterministic current-state and projected-transition assessments.

### Input/state contract

`tools/validate_etf_persisted_valuation_state.py` projects the intended post-trade whole-share portfolio before guarded mutation. A breach raises before `runtime.model_execution_guarded_auto` can write official state or ledger rows.

### Output contract

`runtime/position_count_report_surface.py` and `tools/validate_etf_client_surface_clean.py` add a client-safe EN/NL disclosure only when the current report ticker set exactly matches official state. Historical reports with different ticker sets remain unchanged.

### Operational runbook

The existing production sequence already invokes the persisted-valuation validator immediately before guarded execution. No separate execution authority or hidden mutation step was introduced.

The previously delivered 20260717 recovery workflow is now receipt-aware. Its PR validation detects the existing delivery receipt and validates it instead of attempting a second prepare/send path.

## Exact implementation files

```text
runtime/position_count_contract.py
runtime/position_count_report_surface.py
tools/validate_etf_persisted_valuation_state.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_position_count_contract.py
tests/test_etf_position_count_contract.py
.github/workflows/validate-etf-position-count-contract.yml
.github/workflows/recover-weekly-etf-delivery-20260717.yml
.github/workflows/validate-cockpit-current-runtime.yml
.github/workflows/validate-cockpit-wp08-evidence-review.yml
.github/workflows/validate-cockpit-wp11-production-enablement.yml
```

The three cockpit workflows were rebased only from stale assertions to current authority:

```text
historical action: DFEN -> XLV
current action: XLU -> PAVE
historical source: unsuffixed 260716
current source: delivered 260716_02
historical position count: 8
current position count: 9
```

No cockpit renderer or portfolio authority changed.

## Governance files

```text
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

The append-only decision log and changelog records were written by closeout workflow run `29618612112`; the temporary workflow, trigger and script were removed from the closeout branch before merge.

## Validation

Focused contract proof:

```text
focused_tests: 13 passed
artifact_id: 8420903168
artifact_digest: sha256:cf98f8d4b4d172bc4f463598a557e8490fd2f188bbd5ae3f0c34347ee1688b5b
```

Final implementation same-head proof on `c978153c2dadc2206130e82bb19228e11d494399`:

```text
position_count_run: 29618185729 success
report_surface_run: 29618185736 success
current_runtime_cockpit_run: 29618185701 success
wp08_exact_current_run: 29618185711 success
wp11_exact_current_run: 29618185709 success
closed_recovery_run: 29618185751 success
fresh_send_diagnostic_run: 29618185706 success
```

Closeout governance append:

```text
run: 29618612112
job: 88008928719
result: success
decision_log_updated: true
session_changelog_updated: true
temporary_files_removed: true
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

## Current authority and operational meaning

This package does not decide which holding should be closed. In particular, it does not instruct a sale of the 14-share XLU residual. The next count-reducing decision must use fresh pricing, scores, relative strength, role evidence, liquidity and funding logic.

Until the count is restored:

```text
new_ticker_opening: blocked
no-trade review: allowed
trade into an existing holding with one full closure: allowed only if separately authorized
close to cash: allowed only if separately authorized
partial reduction that preserves nine active positions: blocked
```

## Next action

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
```

That package must be separately claimed. It should first produce a no-mutation review using fresh evidence and must not assume XLU is the correct source solely because it is the smallest position. Any real mutation or report delivery requires separate explicit authorization and the normal whole-share, NAV, manifest and inbox-receipt controls.

## Closure statement

```text
implementation merged: yes
work package closed: yes
claim released: yes
handover finalized: yes
portfolio mutation: no
email sent: no
```
