# ETF Review OS — Current State

## Snapshot date

2026-07-16

## Repository

```text
market-predictions/weekly-etf
```

## Current status

The July 14 production review remains the latest verified production baseline. The guarded URNM-to-XBI rotation was executed and persisted. The delivered bilingual `_03` package remains the latest verified client-delivery baseline. A subsequent non-sending `_04` review package validates report-freshness fixes and the standalone HTML equity graph. Both post-execution consistency and report-freshness packages are closed.

## Production authority

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
pricing_lineage_status: passed
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

```text
URNM: Sell -122.008961 shares; model weight 7.01% -> 2.01%
XBI: Buy +40.491749 shares; model weight 0.00% -> 5.00%
```

Authority sources:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
output/runtime/etf_report_state_20260714_20260715_175910_executed.json
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
```

## Latest verified delivered client package

```text
english_report: output/weekly_analysis_pro_260714_03.md
english_pdf: output/weekly_analysis_pro_260714_03.pdf
dutch_report: output/weekly_analysis_pro_nl_260714_03.md
dutch_pdf: output/weekly_analysis_pro_nl_260714_03.pdf
corrected_delivery_run: 29455717158
delivery_layer_status: smtp_sendmail_returned_no_exception
inbox_receipt_status: verified_bilingual
```

Do not resend `_03`.

Delivery evidence:

```text
output/delivery/weekly_etf_correction_delivery_receipt_2026-07-14_29455717158.txt
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

## Latest validated non-delivered review package

```text
english_report: output/weekly_analysis_pro_260714_04.md
english_html: output/weekly_analysis_pro_260714_04_delivery.html
english_pdf: output/weekly_analysis_pro_260714_04.pdf
dutch_report: output/weekly_analysis_pro_nl_260714_04.md
dutch_html: output/weekly_analysis_pro_nl_260714_04_delivery.html
dutch_pdf: output/weekly_analysis_pro_nl_260714_04.pdf
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

The `_04` review package proves:

- `What changed / Wat veranderde` is delta-only;
- the 11 June ECB event is not represented as a 14 July report-week event;
- IEFA's current 24.05% allocation is reflected consistently;
- DFEN is the current defense holding and PPA remains an alternative;
- specified Dutch hybrid terms are removed;
- standalone HTML embeds the equity PNG;
- MIME email HTML retains the CID contract;
- portfolio-state and trade-ledger hashes are unchanged.

## Closed package evidence

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
freshness_validation_run: 29461019794
post_execution_validation_run: 29461019772
```

## Operational debt

The correction-resend path still requires a narrow runbook cleanup to align the canonical workflow with the production SMTP secret contract and actual text-manifest format, add no-resend recovery, and retire the one-shot bridge. This cleanup must not resend `_03` or `_04` and must not mutate official state or the trade ledger.

## Cockpit roadmap

The cockpit-first roadmap remains a separate preview lane with no production promotion authority.

## Immediate next action

Execute `WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP`, then select the next explicit ETF roadmap package. Do not mix operational cleanup with cockpit product-surface development.
