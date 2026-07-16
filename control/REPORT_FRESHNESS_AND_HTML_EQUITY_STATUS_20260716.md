# Report Freshness and Standalone HTML Equity — Status

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`
PR: #70

## Current status

```text
implementation_status: complete
focused_validation_status: passed
exact_artifact_replay_status: passed
standalone_html_equity_status: passed
merge_status: ready after final governance-head gate
preview_delivery_status: not_authorized_not_sent
portfolio_state_mutation_authority: false
trade_ledger_mutation_authority: false
```

## Root causes resolved

1. Persistent threshold states are no longer labelled as weekly changes.
2. Dated policy events must fall inside the report-week window before relative wording such as `this week` is allowed.
3. Current runtime holdings and weights override stale editorial memory.
4. PPA remains a candidate where relevant but is not described as the current defense holding.
5. The client sanitizer's `#harmful-link` substitution is corrected only for the identified equity image after normal sanitization.
6. Standalone HTML and MIME email HTML now use separate, correct image-source contracts.

## Validation evidence

```text
workflow: Validate ETF report freshness and HTML equity
run_id: 29460852590
conclusion: success
validation_artifact: output/validation/etf_report_freshness_260714_04.json
```

The validation artifact proves:

```text
email_sent: false
model_execution_replayed: false
official_state_mutated: false
official_trade_ledger_mutated: false
state_sha256_before == state_sha256_after
trade_ledger_sha256_before == trade_ledger_sha256_after
standalone_html_uses_embedded_data_uri: true
mime_email_html_keeps_cid_reference: true
```

## Preview package

```text
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_260714_04.pdf
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.pdf
```

The `_04` files are validated review artifacts. They were not emailed.

## Remaining action

Run the final read-only gate on the governance-complete PR head, promote PR #70 from draft, merge it, and then update canonical control state to record the package as closed.
