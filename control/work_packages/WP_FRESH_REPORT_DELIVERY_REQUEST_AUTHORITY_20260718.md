# Work Package — WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: active / claimed

## Current issue

The user authorized a fresh report generation and delivery, but did not authorize the separate close-first portfolio execution package. The production workflow invokes guarded model execution unconditionally, so the run request must be able to fail closed against unauthorized portfolio mutation.

## Decision framework

Report delivery authorization and portfolio execution authorization are separate decisions. A fresh report request must state both explicitly.

## Input/state contract

The latest `control/run_queue/weekly_etf_report_request_*.md` file is the run authorization record. Missing, malformed or false `portfolio_execution_authorized` means no official portfolio or trade-ledger write.

## Output contract

The fresh EN/NL report may describe current evidence and recommendations, but may not claim a model trade was implemented when portfolio execution was not authorized.

## Operational runbook

1. add a fail-closed request parser to the guarded execution wrapper;
2. emit a validated `guarded_auto/no_trade_intents` artifact when execution is unauthorized;
3. preserve official shares and ledger;
4. trigger the normal production workflow with a request for close 2026-07-17;
5. validate run and delivery manifests;
6. confirm both inbox receipts before claiming success.

## Authority boundary

```text
portfolio_execution_authorized: false
delivery_authorized: true
broker_execution: false
```
