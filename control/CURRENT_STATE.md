# ETF Review OS — Current State

## Snapshot date

2026-07-16

## Repository

```text
market-predictions/weekly-etf
```

## Current production status

The July 14 production review remains the latest verified production baseline.

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
pricing_lineage_status: passed
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

Executed mutation:

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

## Latest validated non-delivered report package

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

The `_04` package is review evidence only. Do not describe it as delivered.

It proves:

- `What changed / Wat veranderde` is delta-only;
- stale ECB week-language is removed;
- current IEFA and DFEN authority is reflected;
- Dutch hybrid terms are removed;
- standalone HTML embeds the equity PNG;
- MIME email HTML retains the CID contract;
- official portfolio state and trade ledger were unchanged.

## Canonical post-execution correction runbook

```text
workflow: .github/workflows/resend-corrected-post-execution-report.yml
contract: runtime/post_execution_correction_runbook.py
send_runner: runtime/run_post_execution_correction_delivery.py
recovery_runner: runtime/recover_post_execution_correction_evidence.py
modes: validate_only | recover_no_send | send
```

The runbook is manual-only, uses the established `MRKT_RPRTS_*` mail contract, requires exact dual confirmation for sending, prevents correction-suffix reuse and supports no-send evidence recovery.

No correction send or recovery operation was executed during the cleanup package.

## Cockpit preview lane

The cockpit surface remains a separate preview lane with no production promotion authority.

Historical implementation status is now reconciled:

```text
WP01 preview renderer: merged in PR #52
WP02 manual preview workflow: merged in PR #52
WP03 visual/state-safety contracts: merged in PR #53
WP04 side-by-side review: merged in PR #54
WP05 promotion decision review: merged in PR #55
WP06 iteration path decision: merged in PR #56
WP07 source/provenance iteration: merged in PR #57
promotion_status: not_promoted
selected_path: iteration
```

The old `WP01: not_started` status was stale.

## Cockpit current-runtime revalidation

PR #74 validates the existing cockpit against the authoritative July 14 post-execution state.

Confirmed defects:

```text
previous_weight_pct was selected before current_weight_pct
previous_market_value_eur was selected before market_value_eur
executed rotations were reduced to generic action-present wording
```

Corrected authority order:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

Authoritative zero values are preserved.

Current executed-action surface:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

The action note shows:

```text
URNM 7.01% -> 2.01%
XBI 0.00% -> 5.00%
```

## Cockpit validation evidence

```text
implementation_head: e605eb8de532eed44ec9c44a7be7c6705f128893
workflow_run: 29525632206
workflow_conclusion: success
promotion_status: not_promoted
email_send: false
portfolio_model_execution: false
official_state_mutation: false
official_trade_ledger_mutation: false
```

The workflow passed:

- 33 focused tests;
- production delivery HTML validation;
- macro/thesis surface leakage validation;
- bilingual current-runtime rendering;
- side-by-side review generation;
- exact executed-action assertions;
- before/after SHA-256 equality for nine protected authority files and pointer targets.

Generated CI artifacts are preview/review evidence only:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.*
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260714.*
```

These artifacts were uploaded by the read-only workflow and were not committed as production output.

## Closed packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
PR #72 merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
```

## Immediate next action

Complete PR #74 only after the exact governance head passes the read-only cockpit current-runtime workflow.

After closeout, continue with:

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```

WP08 remains preview-only. It must compare the current classic report with the corrected cockpit and may not make a production promotion decision.
