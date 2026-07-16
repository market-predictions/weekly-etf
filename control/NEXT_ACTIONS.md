# ETF Review OS — Next Actions

## Current production baseline

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

```text
URNM: Sell -122.008961 shares; 7.01% -> 2.01%
XBI: Buy +40.491749 shares; 0.00% -> 5.00%
```

## Delivered client baseline

```text
report_en: output/weekly_analysis_pro_260714_03.md
report_nl: output/weekly_analysis_pro_nl_260714_03.md
pdf_en: output/weekly_analysis_pro_260714_03.pdf
pdf_nl: output/weekly_analysis_pro_nl_260714_03.pdf
delivery_workflow_run: 29455717158
inbox_receipt_status: verified_bilingual
```

Do not resend `_03`.

## Validated review baseline

```text
report_en: output/weekly_analysis_pro_260714_04.md
report_nl: output/weekly_analysis_pro_nl_260714_04.md
html_en: output/weekly_analysis_pro_260714_04_delivery.html
html_nl: output/weekly_analysis_pro_nl_260714_04_delivery.html
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

Do not describe `_04` as delivered. It is non-sending review evidence.

## Closed packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
PR #70: merged
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
freshness_validation_run: 29461019794
post_execution_validation_run: 29461019772
```

## Recommended next package

Create and execute:

```text
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP
```

### Purpose

Consolidate the correction path into one deterministic reusable runbook without changing portfolio logic or resending a completed report.

### Required scope

1. Align `.github/workflows/resend-corrected-post-execution-report.yml` with the production secret contract:

```text
MRKT_RPRTS_SMTP_HOST
MRKT_RPRTS_SMTP_PORT
MRKT_RPRTS_SMTP_USER
MRKT_RPRTS_SMTP_PASS
MRKT_RPRTS_MAIL_FROM
MRKT_RPRTS_MAIL_TO
MRKT_RPRTS_MAIL_TO_NL
```

2. Replace the incorrect JSON-manifest assumption with the actual production text-manifest/receipt contract.
3. Add a no-resend recovery mode for SMTP-success/post-send-persistence-failure cases.
4. Retire `.github/workflows/dispatch-corrected-etf-report-bridge.yml` after equivalent canonical behavior is validated.
5. Decide whether the current correction/recovery helpers remain canonical or are folded into a smaller module.
6. Preserve all historical evidence.

### Safety boundary

The cleanup package must:

```text
email_send: false
portfolio_model_execution: false
official_state_mutation: false
official_trade_ledger_mutation: false
historical_delivery_evidence_mutation: false
```

Required gates:

- focused correction-runbook tests;
- existing correction manifest validates;
- state hash unchanged;
- trade-ledger hash unchanged;
- no send path works without explicit confirmation;
- no-resend recovery cannot invoke SMTP.

## Roadmap after cleanup

After cleanup, select the next explicit roadmap package. The cockpit-first surface remains preview-only and must not be promoted without a separate decision.
