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

## Completed position-count reconciliation

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
implementation_pull_request: #91
implementation_merge: 0bcb6af7e243775d876b59719ce9898fa97c690f
closeout_pull_request: #92
status: closed_merged_validated_no_send
claim_status: closed_released
decision: every non-zero whole-share position counts
generic_residual_exception: false
current_status: close_first 9/8
portfolio_mutation: false
email_sent: false
```

The production preflight now evaluates projected whole-share positions before guarded execution. While the official state remains above eight positions, a proposed transition must lower the active count and cannot introduce another ticker. At eight positions, a new ticker requires another position to reach zero shares in the same projected transition. A no-change review may preserve `close_first`.

Final evidence:

```text
focused_tests: 13 passed
artifact_id: 8420903168
position_count_run: 29618185729 success
report_surface_run: 29618185736 success
current_runtime_cockpit_run: 29618185701 success
wp08_exact_current_run: 29618185711 success
wp11_exact_current_run: 29618185709 success
closed_recovery_run: 29618185751 success
fresh_send_diagnostic_run: 29618185706 success
governance_append_run: 29618612112 success
protected_authority_hashes: identical
historical_report_hashes: identical
```

Persistent records:

```text
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
control/DECISION_LOG.md
control/ETF_SESSION_CHANGELOG.md
```

## Immediate next package

Create and claim only as a separate, explicitly authorized package:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
```

That package must first perform a no-mutation review using fresh pricing, current scores, relative strength, portfolio-role evidence, liquidity and implementation practicality. It must compare all plausible count-reducing paths and must not assume that the smallest holding is automatically the correct source.

Required boundaries:

1. use current authority files and fresh evidence;
2. preserve whole-share, position-count, no-leverage and NAV controls;
3. identify whether a justified path from nine positions to no more than eight exists;
4. keep official state unchanged unless separately authorized;
5. record a new claim, evidence and handover;
6. require a real manifest and inbox receipt for any later delivery claim.

## Separate governance cleanup

A later governance-only package may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with portfolio execution.
