# ETF Review OS — Current State

## Snapshot date

2026-06-13

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP26 are closed. WP27 deterministic regime report integration visual QA is started but pending fresh report artifacts. The latest manifest-linked production baseline remains `260612_08`.**

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

## Active package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

WP27 status:

```text
started / pending fresh report artifact / not closed
```

WP27 status file:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_VISUAL_QA_STATUS.md
```

Required next evidence:

```text
fresh English report artifact after WP26 commits
fresh Dutch report artifact after WP26 commits
visual/readability check of review-only deterministic regime line
```

## Immediate next action

Generate or provide fresh EN/NL report outputs after the WP26 commits, then inspect the deterministic review-only line and record QA evidence.
