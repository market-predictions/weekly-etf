# ETF Review OS — Current State

## Snapshot date

2026-06-14

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP27 are closed. Normal production report-generation and delivery validation passed via workflow run #250. The latest manifest-linked production baseline is now `260612_11` with run_id `20260614_185627`.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-12
run_id: 20260614_185627
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_11.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_11.md
pricing_audit_path: output/pricing/price_audit_2026-06-12_20260614_185627.json
runtime_state_path: output/runtime/etf_report_state_20260612_20260614_185627.json
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260614_185627.json
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## Closed package status

```text
WP16: closed
WP17: closed
WP18: closed
WP19: closed
WP20: closed as not_promoted
WP21: closed as design-only
WP22: closed as manually validated
WP23: closed as manually validated
WP24: closed as review-only
WP25: closed as proposal-only
WP26: closed as manually validated
WP27: closed as visual QA passed
production_delivery_validation_20260614: closed as workflow_success
```

## Evidence

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_VISUAL_QA_STATUS.md
output/macro/validation/deterministic_regime_report_visual_qa_validation_20260613_codespace.json
control/PRODUCTION_DELIVERY_VALIDATION_STATUS_20260614.md
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260614_185627.json
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260614_185627.json
```

## Immediate next action

No deterministic-regime package is active. No production delivery action is currently pending.
