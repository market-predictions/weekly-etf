# Fresh ETF Delivery Recovery Changelog — 2026-07-18

## Scope

Recovered and delivered the already-generated 2026-07-17 Weekly ETF Pro report without authorizing portfolio or broker execution.

## Timeline

1. Fresh report-only production runs generated current pricing, runtime state and bilingual reports but stopped before transport.
2. Guarded recovery runs reached the delivery render chain and failed at the client-surface clean gate.
3. User-provided Actions evidence identified residual `raw_override` and `release_score` labels in the English Markdown and delivery HTML.
4. PR #105 expanded the shared language normalizer and regression coverage.
5. Validation run `29659315302` and exact-current diagnostic run `29659315297` passed.
6. PR #106 retriggered the transport-only recovery.
7. Recovery persisted delivery evidence in commit `a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea`.
8. English and Dutch inbox receipts were independently confirmed, each with four attachments.

## Files changed

```text
runtime/report_surface_language_contract.py
tests/test_report_surface_internal_language_cleanup.py
control/work_packages/WP_FRESH_ETF_DELIVERY_RECOVERY_20260718.md
control/work_package_claims/WP_FRESH_ETF_DELIVERY_RECOVERY_20260718.md
control/evidence/FRESH_ETF_DELIVERY_RECOVERY_EVIDENCE_20260718.json
control/decisions/FRESH_ETF_DELIVERY_RECOVERY_DECISION_20260718.md
control/handovers/HANDOVER_FRESH_ETF_DELIVERY_RECOVERY_20260718.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

## Final result

```text
run_id: 20260718_140601
requested_close_date: 2026-07-17
workflow_status: workflow_success
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception
inbox_receipt: confirmed_both_languages
portfolio_execution: false
broker_execution: false
portfolio_state_mutation_by_recovery: false
trade_ledger_mutation_by_recovery: false
```
