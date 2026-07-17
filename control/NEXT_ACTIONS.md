# ETF Review OS — Next Actions

## Current authoritative baseline

```text
latest_report_close: 2026-07-16
latest_report_run_id: 20260717_154351
latest_delivered_report: output/weekly_analysis_pro_260716_02.md
latest_delivered_report_nl: output/weekly_analysis_pro_nl_260716_02.md
official_portfolio_state: output/etf_portfolio_state.json
whole_share_status: compliant
nav_eur: 107117.94
cash_eur: 2534.36
active_position_count: 9
maximum_active_positions: 8
position_count_status: close_first
cockpit_production_feature: enabled
client_language_contract: active
inbox_receipt: confirmed_both_languages
```

The current delivered package is the first real production proof combining whole-share official state, one cockpit page per language, preserved classic report bodies, client-language gates, passed pricing lineage, a real delivery manifest and confirmed English/Dutch Gmail receipts.

## Completed delivery recovery

```text
package: WP_FRESH_WEEKLY_ETF_SEND_RECOVERY
source_run: 20260717_154351
persisted_rotation: XLU -> PAVE
repeat_portfolio_execution: false
language_fix_PR: #89
recovery_workflow_PR: #90
delivery_evidence_commit: ddc745fddf0e80a31c4309658743f6435a4d486b
status: closed_delivered
```

## Position-count reconciliation

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
pull_request: #91
status: implementation_complete_validation_green_merge_pending
decision: every non-zero whole-share position counts
generic_residual_exception: false
current_status: close_first 9/8
portfolio_mutation: false
email_sent: false
```

The production preflight now evaluates projected whole-share positions before guarded mutation. While above eight positions, a proposed trade must reduce the active count and may not introduce a new ticker. At eight positions, a new ticker requires a full source close in the same transition. A no-trade review may preserve the current count while reporting `close_first`.

Validation:

```text
primary_run: 29617207278 success
primary_job: 88004737784
focused_tests: 13 passed
artifact_id: 8420903168
report_surface_regression: 29617207295 success
closed_recovery_regression: 29617207264 success
fresh_send_diagnostic_regression: 29617207249 success
protected_authority_hashes: identical
historical_report_hashes: identical
```

Persistent records:

```text
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
```

## Immediate next package

Create and claim only after PR #91 closeout:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
```

### Current issue

The official state remains at nine active positions. The reconciliation contract blocks a new ticker but deliberately does not choose which holding should be closed or reduced to zero.

### Required decision framework

The next package must:

1. use fresh pricing and current evidence rather than the historical size of a residual alone;
2. compare all plausible closure/funding sources by portfolio role, score, relative strength, thesis validity, opportunity cost, liquidity and execution practicality;
3. choose a path that reduces the active count from nine to no more than eight;
4. avoid introducing a new ticker while the state remains above the maximum;
5. distinguish clearly between:
   - close to cash;
   - close and reallocate to an already-held ticker;
   - no-trade because evidence is insufficient;
6. not assume that XLU is the correct source merely because it is the smallest position.

### Required input/state contract

Use:

```text
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
latest immutable pricing audit
latest recommendation scorecard
latest lane and relative-strength evidence
latest macro/policy evidence with current authority rules
```

All quantities and projected deltas remain whole shares. The existing NAV-drift tolerance and no-leverage rule remain unchanged.

### Required output contract

The review must state:

- current active count and maximum;
- whether a count-reducing action is supported;
- the selected source and destination, if any;
- why alternatives were rejected;
- projected whole-share quantities, cash and active count;
- client-safe EN/NL wording without internal implementation terms.

### Required operational runbook

- claim the package before implementation;
- run a no-mutation review first;
- use the position-count preflight on every proposed transition;
- do not mutate state unless the user separately and explicitly authorizes execution;
- do not claim delivery without a real manifest and inbox receipt;
- create a handover and update control files after closure.

## Separate governance cleanup

A later governance-only package may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with portfolio execution.
