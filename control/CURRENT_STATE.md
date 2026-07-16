# ETF Review OS — Current State

## Snapshot date

2026-07-16

## Repository

```text
market-predictions/weekly-etf
```

## Current status

The July 14 production review remains the latest verified production baseline. The guarded URNM-to-XBI rotation was executed and persisted. The delivered bilingual `_03` package remains the latest verified client-delivery baseline. The non-sending `_04` package remains the latest validated report-freshness and standalone-HTML review evidence.

The post-execution report consistency, report freshness/HTML equity and post-execution correction-runbook cleanup packages are closed.

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
- IEFA's current allocation and DFEN's incumbent role are reflected consistently;
- specified Dutch hybrid terms are removed;
- standalone HTML embeds the equity PNG;
- MIME email HTML retains the CID contract;
- portfolio-state and trade-ledger hashes were unchanged during validation.

Do not describe `_04` as delivered.

## Canonical post-execution correction runbook

```text
workflow: .github/workflows/resend-corrected-post-execution-report.yml
contract: runtime/post_execution_correction_runbook.py
send_runner: runtime/run_post_execution_correction_delivery.py
recovery_runner: runtime/recover_post_execution_correction_evidence.py
modes: validate_only | recover_no_send | send
```

The correction runbook now:

- is manual-only and has no automatic push-triggered send;
- uses the established `MRKT_RPRTS_*` production mail contract;
- requires exact confirmation in both request and dispatch before sending;
- rejects an already-used correction suffix;
- treats the positive `DELIVERY_OK` text line and English/Dutch `*_delivery_manifest.txt` names as delivery evidence authority;
- provides a no-send recovery mode that strips mail configuration and uses render-only generation;
- restores original bytes and fails if recovery would change existing historical report evidence;
- compares current official state and trade-ledger hashes before and after each operation.

The one-shot bridge was retired:

```text
.github/workflows/dispatch-corrected-etf-report-bridge.yml
```

No send or recovery operation was executed during cleanup.

## Closed package evidence

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
PR #72 merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
correction_runbook_validation_run: 29520607344
post_execution_consistency_run: 29520608204
```

## Cockpit roadmap

The cockpit-first roadmap remains a separate preview lane with no production promotion authority.

## Immediate next action

Select and claim the next explicit ETF roadmap package. The recommended continuation is validation of `WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER`, keeping all cockpit artifacts preview-only under `output/cockpit_preview/` and making no production promotion decision in that package.
