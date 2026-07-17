# ETF Review OS — Current State

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`

## Official portfolio authority

```text
portfolio_state: output/etf_portfolio_state.json
trade_ledger: output/etf_trade_ledger.csv
whole_share_status: compliant
cash_eur: 2534.36
invested_market_value_eur: 104583.58
nav_eur: 107117.94
position_count: 9
```

Current whole-share positions:

```text
CIBR 253
GSG 374
IEFA 312
PAVE 107
SMH 59
URNM 48
XBI 40
XLU 14
XLV 37
```

The latest official rotation reduced `XLU` by 134 shares and added 107 shares of `PAVE`. A 14-share `XLU` residual remains. No second execution occurred during delivery recovery.

## Latest successful production run

```text
requested_close_date: 2026-07-16
run_id: 20260717_154351
report_token: 260716
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
report_authority_source: portfolio_state_post_execution
production_rotation: XLU -> PAVE
```

Authority and evidence files:

```text
output/pricing/price_audit_2026-07-16_20260717_154351.json
output/runtime/etf_report_state_20260716_20260717_154351_executed.json
output/runtime/etf_model_execution_20260716_20260717_154351.json
output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json
output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json
control/evidence/WEEKLY_ETF_DELIVERY_RECOVERY_EVIDENCE_20260717.json
```

## Latest delivered client package

```text
English Markdown: output/weekly_analysis_pro_260716_02.md
English PDF: output/weekly_analysis_pro_260716_02.pdf
English HTML: output/weekly_analysis_pro_260716_02_delivery.html
Dutch Markdown: output/weekly_analysis_pro_nl_260716_02.md
Dutch PDF: output/weekly_analysis_pro_nl_260716_02.pdf
Dutch HTML: output/weekly_analysis_pro_nl_260716_02_delivery.html
delivery_status: smtp_sendmail_returned_no_exception
inbox_receipt: confirmed_both_languages
```

Gmail receipt evidence:

```text
English subject: Weekly ETF Pro Review 2026-07-16
English received: 2026-07-17T09:28:00-07:00
English attachments: 4
Dutch subject: Weekly ETF Pro Review | Nederlands 2026-07-16
Dutch received: 2026-07-17T09:28:02-07:00
Dutch attachments: 4
```

Each message contains the `_02` PDF, clean Markdown, full delivery HTML and equity-curve PNG.

## Cockpit and client-language production status

```text
cockpit_feature: MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled
English cockpit front pages: 1
Dutch cockpit front pages: 1
classic report body: preserved
client_language_gate: passed
macro_thesis_leakage_gate: passed
pdf_visual_gate: passed
```

The Dutch delivery-language contract now evaluates visible client text rather than CSS/class identifiers. Visible English remains forbidden; CSS identifiers do not create false failures.

## Delivery recovery closeout

```text
package: WP_FRESH_WEEKLY_ETF_SEND_RECOVERY
language_fix_PR: #89
language_fix_merge: 68e8587ff6032c8cf3fe1c30019fb513cf57058f
recovery_workflow_PR: #90
recovery_workflow_merge: de2464fc81cc1579437ffaad4a62f4add279d6f5
validation_run: 29596023922
validation_job: 87936494610
delivery_evidence_commit: ddc745fddf0e80a31c4309658743f6435a4d486b
status: closed_delivered
```

Stable recovery rules:

1. A failed post-execution delivery must reuse the persisted execution artifact and must not repeat portfolio mutation.
2. Recovery `prepare` must pass whole-share, ledger, pricing-lineage, cockpit, language, leakage and PDF gates before SMTP.
3. Existing sendreceipt artifacts fail closed against duplicate recovery delivery.
4. Delivery success requires both a real delivery manifest and an independently confirmed inbox receipt.
5. Portfolio state, trade ledger and valuation history must retain identical hashes throughout recovery.

## Open portfolio-contract issue

The current official state contains nine positions, while the delivered report lists a maximum of eight positions under its constraints. This arose because the rotation reduced `XLU` to a 14-share residual while adding `PAVE`.

This does not invalidate delivery or whole-share compliance, but it requires a separate decision before the next portfolio mutation:

```text
option A: residual positions count toward the maximum and must be closed
option B: sub-threshold residual positions receive an explicit temporary exception
```

## Immediate next action

```text
WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
```

The next package should reconcile the nine-position official state with the eight-position constraint without silently changing holdings. It must define the decision rule, residual-position treatment, execution behavior and validation evidence before another rotation is allowed.
