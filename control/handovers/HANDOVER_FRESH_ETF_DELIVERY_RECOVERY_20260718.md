# Handover — Fresh ETF Delivery Recovery

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Package: `WP_FRESH_ETF_DELIVERY_RECOVERY`
Status: closed / delivered / inbox confirmed

## Executive summary

The fresh Weekly ETF Pro report for close date 2026-07-17 has been generated and delivered in English and Dutch. The final source run is `20260718_140601` and the delivered package uses the `_02` filenames.

The delay was not caused by GitHub Actions credits. GitHub allocated hosted runners and executed the workflows. Recovery failed at the client-surface clean gate because the English report still contained the internal labels `release score` and `System override: Minimum trade size was not met`.

PR #105 expanded the existing client-language normalizer and added regression coverage. PR #106 retriggered the transport-only recovery. The recovery then completed and persisted commit `a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea`.

## 1. Decision framework

The recovery was allowed only because the source reports, runtime state and pricing audit were already persisted; no delivery manifest or inbox receipt existed; and portfolio execution remained unauthorized.

Success required all of the following:

1. client-surface, bilingual, HTML and PDF gates pass;
2. no portfolio-state or trade-ledger write occurs;
3. both language editions are sent;
4. a delivery manifest is linked to the run manifest;
5. both messages are independently visible in the receiving inbox.

## 2. Input/state contract

```text
source_run_id: 20260718_140601
requested_close_date: 2026-07-17
report_token: 260717
pricing_audit: output/pricing/price_audit_2026-07-17_20260718_140601.json
runtime_state: output/runtime/etf_report_state_20260717_20260718_140601.json
english_report: output/weekly_analysis_pro_260717_02.md
dutch_report: output/weekly_analysis_pro_nl_260717_02.md
portfolio_state: output/etf_portfolio_state.json
trade_ledger: output/etf_trade_ledger.csv
```

Current valuation authority:

```text
cash_eur: 2534.36
invested_market_value_eur: 104109.85
nav_eur: 106644.21
active_positions: 9
maximum_positions: 8
position_count_status: close_first
```

Current whole-share holdings remain:

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

The delivery recovery did not change these share quantities or the trade ledger.

## 3. Output contract

Final run manifest:

```text
output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260718_140601.json
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
```

Final delivery manifest:

```text
output/delivery/weekly_etf_delivery_manifest_2026-07-17_20260718_140601.json
delivery_status: smtp_sendmail_returned_no_exception
language_count: 2
```

English package:

```text
output/weekly_analysis_pro_260717_02.md
output/weekly_analysis_pro_260717_02_clean.md
output/weekly_analysis_pro_260717_02_delivery.html
output/weekly_analysis_pro_260717_02.pdf
output/weekly_analysis_pro_260717_02_equity_curve.png
```

Dutch package:

```text
output/weekly_analysis_pro_nl_260717_02.md
output/weekly_analysis_pro_nl_260717_02_clean.md
output/weekly_analysis_pro_nl_260717_02_delivery.html
output/weekly_analysis_pro_nl_260717_02.pdf
output/weekly_analysis_pro_nl_260717_02_equity_curve.png
```

Independent inbox receipts were confirmed at 22:19 Europe/Amsterdam. Each message contains four attachments.

## 4. Operational runbook

Implementation and recovery sequence:

```text
PR #105: client-surface residual language fix
merge: bfba7c2e038eaba9a071008fc33fe09832dd4f5c
language validation run: 29659315302 success
exact-current diagnostic run: 29659315297 success

PR #106: transport-only recovery retrigger
merge: ba558abf9c79ecd2066ebe8fc57db41a9c9c44ee
recovery evidence commit: a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea
```

The stable diagnostic lesson is that a red Actions run must be classified from its actual failing step. In this case the runner had started and performed the expensive render work, so a normal Actions-minute credit block was ruled out immediately.

## Remaining boundaries

- No resend is pending.
- Do not run another delivery recovery for this source run because a delivery manifest and inbox receipts now exist.
- Do not treat this report-only recovery as authorization for `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION`.
- The official portfolio remains at nine positions and retains `close_first` status.
- A separate future output-quality package may audit wording extracted from the actual receiving-mail-client body; it must not resend this package without explicit approval.

## Evidence

```text
control/evidence/FRESH_ETF_DELIVERY_RECOVERY_EVIDENCE_20260718.json
control/work_packages/WP_FRESH_ETF_DELIVERY_RECOVERY_20260718.md
control/work_package_claims/WP_FRESH_ETF_DELIVERY_RECOVERY_20260718.md
```
