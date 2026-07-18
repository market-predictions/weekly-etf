# Work Package — WP_FRESH_ETF_DELIVERY_RECOVERY

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: closed / delivered / inbox confirmed

## Current issue

Production runs `20260718_134258` and `20260718_140601` generated fresh 2026-07-17 report evidence but stopped before email transport. The guarded recovery runs then reached the render chain but failed at the client-surface gate on residual internal labels in the English report.

## Root cause

GitHub Actions credits were not the cause. Hosted runners were allocated and executed the pricing, render, PDF and validation steps. The blocking exception was:

```text
ETF client-surface clean gate failed:
weekly_analysis_pro_260717_02.md: raw_override, release_score
weekly_analysis_pro_260717_02_delivery.html: raw_override, release_score
```

The language normalizer handled `release score <number>` and several override phrases, but did not cover:

- the bare table header `Release score`;
- the plural phrase `release scores`;
- `System override: Minimum trade size was not met`;
- the `Override status` table header.

## Decision framework

A delivery recovery was permitted only because:

- the source run and reports were immutable and identified;
- no prior delivery manifest existed;
- no matching inbox receipt existed;
- portfolio and trade-ledger writes were explicitly unauthorized;
- both language editions had to pass the same downstream gates;
- delivery success required both a manifest and independent inbox receipts.

## Input/state contract

```text
source_run_id: 20260718_140601
requested_close_date: 2026-07-17
report_token: 260717
english_report: output/weekly_analysis_pro_260717_02.md
dutch_report: output/weekly_analysis_pro_nl_260717_02.md
runtime_state: output/runtime/etf_report_state_20260717_20260718_140601.json
pricing_audit: output/pricing/price_audit_2026-07-17_20260718_140601.json
portfolio_execution_authorized: false
broker_execution_authorized: false
```

## Implemented change

PR #105 expanded `runtime/report_surface_language_contract.py` and its regression tests so the failing internal labels are rewritten to client-safe review-priority and execution-constraint wording. The language-cleanup workflow and exact-current delivery diagnostic both passed.

```text
implementation_pr: 105
implementation_merge: bfba7c2e038eaba9a071008fc33fe09832dd4f5c
language_validation_run: 29659315302 success
exact_current_diagnostic_run: 29659315297 success
```

PR #106 then added a new transport-only recovery trigger.

```text
retrigger_pr: 106
retrigger_merge: ba558abf9c79ecd2066ebe8fc57db41a9c9c44ee
delivery_evidence_commit: a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea
```

## Output contract result

```text
run_manifest: output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260718_140601.json
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
delivery_manifest: output/delivery/weekly_etf_delivery_manifest_2026-07-17_20260718_140601.json
delivery_status: smtp_sendmail_returned_no_exception
language_count: 2
attachments_per_language: 4
```

Independent Gmail receipts:

```text
English subject: Weekly ETF Pro Review 2026-07-17
English received: 2026-07-18 22:19:41 Europe/Amsterdam
Dutch subject: Weekly ETF Pro Review | Nederlands 2026-07-17
Dutch received: 2026-07-18 22:19:43 Europe/Amsterdam
English attachment count: 4
Dutch attachment count: 4
```

## Authority result

- no broker order was placed;
- no new model trade was executed;
- official share quantities were not changed by the recovery;
- the trade ledger was not changed by the recovery;
- the current 9-position `close_first` state remains authoritative;
- delivery success is now confirmed by both GitHub manifests and Gmail receipts.

## Final governance closeout

```text
closeout_pull_request: 107
closeout_merge: f5c8ab979ee227f0adbdd556d100537ede6c50d6
validated_closeout_head: 96f05bccf895a96f32b3a8db68654944393b442c
current_runtime_run: 29659883734 success
wp08_run: 29659883741 success
wp11_run: 29659883739 success
email_inline_run: 29659883756 success
client_language_run: 29659883732 success
position_count_run: 29659883737 success
```

## Acceptance criteria

- [x] work package and claim existed before recovery work;
- [x] root cause distinguished from GitHub billing or credit exhaustion;
- [x] client-surface residuals fixed with regression coverage;
- [x] downstream render, PDF, HTML and language gates passed;
- [x] transport-only recovery executed;
- [x] successful run manifest persisted;
- [x] successful bilingual delivery manifest persisted;
- [x] English inbox receipt confirmed;
- [x] Dutch inbox receipt confirmed;
- [x] handover and control closeout recorded;
- [x] final governance closeout merged and exact receipt recorded.
