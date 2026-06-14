# ETF Review OS — Current State

## Snapshot date

2026-06-13

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP26 are closed. WP26 deterministic regime report integration implementation is closed based on manual GitHub Codespace validation evidence. The latest manifest-linked production baseline remains `260612_08`. The next package is WP27 — Deterministic regime report integration closeout / visual report QA.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-12
run_id: 20260613_113054
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_08.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_08.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_113054.json
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
```

WP26 evidence:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_IMPLEMENTATION_STATUS.md
output/macro/validation/deterministic_regime_report_integration_validation_20260613_codespace.json
```

## WP26 status

```text
closed / manually validated in GitHub Codespace / not workflow-proven
```

Observed validation evidence:

```text
5 passed in 0.05s
18 passed in 0.06s
ETF_MACRO_REPORT_SURFACE_OK | label=fixture | en_chars=2088 | nl_chars=2318
ETF_MACRO_REPORT_SURFACE_OK | label=output/macro/latest.json | en_chars=2455 | nl_chars=2674
```

## Immediate next action

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```
