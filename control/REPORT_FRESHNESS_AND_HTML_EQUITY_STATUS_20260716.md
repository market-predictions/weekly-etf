# Report Freshness and Standalone HTML Equity — Status

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`

## Current status

```text
implementation_status: in_progress
focused_validation_status: pending
exact_artifact_replay_status: pending
preview_delivery_status: not_authorized
portfolio_state_mutation_authority: false
trade_ledger_mutation_authority: false
```

## Confirmed root causes

1. The macro builder classified current threshold states as `what_changed` output.
2. The ECB event filter checked only whether the report date was after 2026-06-11, not whether the event occurred in the current report week.
3. Static report text could contradict current runtime holdings.
4. The HTML artifact persisted the CID-backed email body instead of a self-contained variant.

## Target proof

```text
preview_report_en: output/weekly_analysis_pro_260714_04.md
preview_report_nl: output/weekly_analysis_pro_nl_260714_04.md
preview_html_en: output/weekly_analysis_pro_260714_04_delivery.html
preview_html_nl: output/weekly_analysis_pro_nl_260714_04_delivery.html
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

## Completion boundary

Merge is blocked until focused tests, exact-artifact replay, standalone HTML graph validation and state/ledger immutability all pass.
