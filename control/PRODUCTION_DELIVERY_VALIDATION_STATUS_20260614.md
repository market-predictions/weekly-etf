# Production Delivery Validation Status

## Scope

Normal production report-generation and delivery validation after WP27 closeout.

## Status

```text
closed / workflow_success / delivery_layer_manifest_present / not inbox-receipt-proven
```

## Workflow evidence

```text
workflow: Send weekly ETF Pro report
workflow_run_number: 250
trigger: manual workflow_dispatch
observed_status: success
observed_at: 2026-06-14 20:55 GMT+2
```

## Source-of-truth run manifest

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260614_185627.json
```

## Delivery manifest

```text
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260614_185627.json
```

## Production baseline

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
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
```

## Delivery evidence boundary

```text
smtp_sendmail_returned_no_exception means send_report.py returned after smtplib.sendmail without raising and wrote per-language delivery manifests.
This is not an end-recipient inbox receipt.
```

## Attachments recorded by delivery summary

English delivery package:

```text
weekly_analysis_pro_260612_11.pdf
weekly_analysis_pro_260612_11_clean.md
weekly_analysis_pro_260612_11_delivery.html
weekly_analysis_pro_260612_11_equity_curve.png
```

Dutch delivery package:

```text
weekly_analysis_pro_nl_260612_11.pdf
weekly_analysis_pro_nl_260612_11_clean.md
weekly_analysis_pro_nl_260612_11_delivery.html
weekly_analysis_pro_nl_260612_11_equity_curve.png
```
