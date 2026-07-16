# Report Freshness and Standalone HTML Equity — Status

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`
PR: #70

## Final status

```text
implementation_status: complete
focused_validation_status: passed
exact_artifact_replay_status: passed
standalone_html_equity_status: passed
merge_status: merged
package_status: closed
preview_delivery_status: not_authorized_not_sent
portfolio_state_mutation_authority: false
trade_ledger_mutation_authority: false
```

## Evidence

```text
validated_head: 2864050289b2bf4259e5c2f0375b6b9c42078fed
freshness_validation_run: 29461019794
post_execution_validation_run: 29461019772
PR: #70
merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
validation_artifact: output/validation/etf_report_freshness_260714_04.json
```

The validation artifact records:

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

The `_04` package is validated review evidence and was not emailed.
