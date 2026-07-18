# Work Package — WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: implementation validated / production delivery pending

## Current issue

The user authorized fresh report generation and delivery, but did not authorize the separate close-first portfolio execution package. The production workflow invokes guarded model execution, so the report request needed a fail-closed boundary against unauthorized official portfolio mutation.

## Decision framework

Report delivery authorization and portfolio execution authorization are separate decisions. A fresh report request must state both explicitly.

## Input/state contract

The latest `control/run_queue/weekly_etf_report_request_*.md` file is the production authorization record. The CLI production route enforces request authority. Missing, malformed or false `portfolio_execution_authorized` means no official portfolio or trade-ledger write.

Direct programmatic calls used by internal tests retain their existing behavior unless they explicitly set `enforce_request_authority=True`; the production CLI always sets that flag. The persisted-valuation position-count preflight applies the same production-only boundary: a report-only run reports the current `close_first` state but does not project an unauthorized rotation.

## Output contract

The fresh EN/NL report may describe current evidence and recommendations, but may not claim that a model trade was implemented when portfolio execution was not authorized.

## Operational runbook

1. parse the latest report request fail closed;
2. enforce request authority in the production CLI;
3. emit a validated `guarded_auto/no_trade_intents` artifact when execution is unauthorized;
4. preserve official share quantities and the trade ledger;
5. reprice official holdings and persist valuation history;
6. report the current position-count status without projecting an unauthorized transition;
7. trigger the normal production workflow with requested close 2026-07-17;
8. validate pricing, whole shares, position count, client language, HTML/PDF and manifests;
9. send English and Dutch editions;
10. confirm both inbox receipts before claiming delivery success.

## Implementation

```text
runtime/model_execution_guarded_auto.py
tools/validate_etf_persisted_valuation_state.py
tests/test_model_execution_request_authority.py
.github/workflows/validate-report-request-execution-authority.yml
control/run_queue/README.md
control/run_queue/weekly_etf_report_request_20260718_125324.md
```

## Final implementation validation

```text
pull_request: #101
validated_head: 1ae719b3c5ddf1e110013fe66447b174e99d6c27
request_authority_run: 29646502090 success
whole_share_run: 29646502094 success
position_count_run: 29646502091 success
protected_portfolio_and_ledger: unchanged
```

## Authority boundary

```text
portfolio_execution_authorized: false
delivery_authorized: true
broker_execution_authorized: false
```

## Completion condition

The implementation may merge when the authority, whole-share and position-count gates are green. The package remains open until the fresh production run writes a successful run manifest and delivery manifest and both recipient inbox messages are independently confirmed.