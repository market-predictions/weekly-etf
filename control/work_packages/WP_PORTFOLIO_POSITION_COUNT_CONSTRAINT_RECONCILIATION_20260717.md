# Work Package — WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Status: implementation_complete / validation_green / merge_pending

## Current issue

The official portfolio state contains nine non-zero whole-share positions, while the production constraint states a maximum of eight positions. The mismatch arose when guarded execution reduced `XLU` to 14 shares while opening `PAVE` with 107 shares.

This package reconciles the decision rule and execution contract without silently changing current holdings and without sending a report.

## Decision framework

Selected rule: **every non-zero position counts toward the maximum**.

Consequences:

1. `shares > 0` means an active position and counts toward the position limit.
2. Zero-share positions do not count and must not remain as active official holdings.
3. Duplicate active ticker rows are invalid.
4. No generic residual-position exemption exists.
5. When the portfolio is already above the limit, it enters `close_first` status.
6. A no-trade run may preserve the current count while reporting `close_first`.
7. Any proposed trade while above the limit must reduce the active count and may not open a new ticker.
8. When the portfolio is at the limit, opening a new ticker requires one existing source position to reach zero shares in the same projected whole-share execution.
9. A partial reduction that leaves the source non-zero cannot free a position slot.

The current nine-position state is not mutated by this package. It is recorded as a contract breach requiring count-reducing execution before another new ticker may be opened.

## Input/state contract

Authority:

```text
output/etf_portfolio_state.json
```

Implemented machine rules:

- count unique tickers with whole-share `shares > 0`;
- reject duplicate active tickers;
- default maximum active positions to `8`;
- allow an explicit machine-readable maximum only when present in the runtime rotation policy;
- simulate intended post-trade whole-share quantities before any guarded write;
- fail closed when the intended post-trade count exceeds the maximum or an already-over-limit proposed trade does not reduce its count;
- allow a no-trade run to remain `close_first` without mutation;
- preserve current state, ledger and valuation files during this package.

## Output contract

Future English and Dutch reports must not state `Max number of positions: 8` without also presenting the actual official count when the current report holdings exactly match an above-limit official state.

Client-safe language:

```text
Maximum active positions: 8. Current active positions: 9. No new position may be opened until the count is restored.
```

Dutch:

```text
Maximaal aantal actieve posities: 8. Huidig aantal actieve posities: 9. Er mag geen nieuwe positie worden geopend totdat het aantal is hersteld.
```

The output guard is current-state-aware. Historical reports with a different ticker set remain byte unchanged. No raw override, workflow, policy-check or internal error terminology may leak into the client surface.

## Operational runbook

Implemented:

1. shared position-count contract: `runtime/position_count_contract.py`;
2. current-state-aware report guard: `runtime/position_count_report_surface.py`;
3. pre-mutation production integration in `tools/validate_etf_persisted_valuation_state.py`;
4. current client-surface integration in `tools/validate_etf_client_surface_clean.py`;
5. read-only evidence validator: `tools/validate_etf_position_count_contract.py`;
6. 13 focused regressions in `tests/test_etf_position_count_contract.py`;
7. GitHub Actions validation: `.github/workflows/validate-etf-position-count-contract.yml`;
8. receipt-aware validation for the already-closed 20260717 delivery recovery workflow.

## Validation evidence

```text
pull_request: #91
validated_head: 07c4f32456d50a6f624f664cfa87970e9c8dec76
primary_run: 29617207278
primary_job: 88004737784
focused_tests: 13 passed
artifact_id: 8420903168
artifact_digest: sha256:cf98f8d4b4d172bc4f463598a557e8490fd2f188bbd5ae3f0c34347ee1688b5b
report_surface_regression: 29617207295 success
closed_recovery_regression: 29617207264 success
fresh_send_diagnostic_regression: 29617207249 success
current_state_status: close_first 9/8
protected_authority_hashes: identical
historical_report_hashes: identical
portfolio_execution: false
email_sent: false
```

Persistent evidence and decision:

```text
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
```

## Non-goals and authority boundary

This package did not:

- execute trades;
- change `output/etf_portfolio_state.json`;
- append ledger rows;
- change valuation history;
- rewrite historical reports;
- send email;
- weaken whole-share or NAV-drift controls.

## Acceptance status

- package and claim recorded before implementation: complete;
- every non-zero position deterministically counts: complete;
- guarded execution fails closed before mutation on a count breach: complete;
- existing nine-position state classified `close_first` without mutation: complete;
- focused tests and compatibility gates pass: complete;
- protected authority hashes remain unchanged: complete;
- persistent evidence and decision records written: complete;
- PR merge: pending;
- final claim release and handover closeout: pending merge;
- no report or email sent: confirmed.
