# ETF Review OS — Next Actions

## Current production baseline

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

Authoritative mutation:

```text
URNM: Sell -122.008961 shares; 7.01% -> 2.01%
XBI: Buy +40.491749 shares; 0.00% -> 5.00%
```

## Current client-delivery baseline

```text
report_en: output/weekly_analysis_pro_260714_03.md
report_nl: output/weekly_analysis_pro_nl_260714_03.md
pdf_en: output/weekly_analysis_pro_260714_03.pdf
pdf_nl: output/weekly_analysis_pro_nl_260714_03.pdf
delivery_workflow_run: 29455717158
delivery_layer_status: smtp_sendmail_returned_no_exception
inbox_receipt_status: verified_bilingual
```

Delivery evidence:

```text
output/delivery/weekly_etf_correction_delivery_receipt_2026-07-14_29455717158.txt
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

Do not resend `260714_03`.

## Closed active package

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
PR #59: merged
implementation_validation_run: 29442287444
corrected_delivery_run: 29455717158
recovery_and_persistence_run: 29455966433
persistence_commit: d829e89329656b29be4c1d9b3b4aca75ba46f3b4
```

All gates passed:

- executed-state action authority;
- bilingual Markdown and HTML consistency;
- English and Dutch PDF rendering;
- positive delivery-layer receipt;
- bilingual inbox receipt confirmation;
- portfolio-state immutability;
- trade-ledger immutability;
- corrected artifact persistence.

## Recommended next package

Create and execute a narrow operational cleanup package:

```text
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP
```

### Purpose

Consolidate the correction path into one deterministic, reusable operational runbook without changing portfolio logic or resending the completed report.

### Required changes

1. Update `.github/workflows/resend-corrected-post-execution-report.yml` to use the established production secret contract:

```text
MRKT_RPRTS_SMTP_HOST
MRKT_RPRTS_SMTP_PORT
MRKT_RPRTS_SMTP_USER
MRKT_RPRTS_SMTP_PASS
MRKT_RPRTS_MAIL_FROM
MRKT_RPRTS_MAIL_TO
MRKT_RPRTS_MAIL_TO_NL
```

2. Replace the incorrect JSON-manifest assumption with the actual production delivery receipt/manifest format.
3. Add a no-resend recovery mode for the case where SMTP succeeds but post-send evidence persistence fails.
4. Retire the one-shot bridge after equivalent behavior is covered by the canonical correction workflow:

```text
.github/workflows/dispatch-corrected-etf-report-bridge.yml
```

5. Decide whether these helpers remain canonical or are folded into a smaller runbook module:

```text
runtime/run_post_execution_correction_delivery.py
runtime/recover_post_execution_correction_evidence.py
```

6. Preserve all historical correction evidence and do not mutate the official portfolio state or trade ledger.

### Validation boundary

The cleanup package must be validation-only for the completed `260714_03` delivery. It must not send another email and must not execute another portfolio mutation.

Required gates:

```text
python -m py_compile runtime/run_post_execution_correction_delivery.py runtime/recover_post_execution_correction_evidence.py
focused correction-runbook tests
state hash unchanged
trade-ledger hash unchanged
existing correction manifest still validates
no workflow path can resend without explicit confirmation
```

## Roadmap after cleanup

After the correction-runbook cleanup is closed, select the next explicit roadmap package. The cockpit-first surface remains preview-only and must not be promoted into production without a separate decision.

Possible next roadmap action:

```text
resume WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER validation
```

Do not mix the cleanup package with cockpit product-surface development.
