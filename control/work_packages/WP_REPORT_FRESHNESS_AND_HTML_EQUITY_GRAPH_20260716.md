# WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Layer: input/state contract + output contract + operational runbook
Status: closed

## Outcome

The package corrected stale report wording and restored the equity graph in standalone HTML.

Resolved defects:

1. `What changed / Wat veranderde` now reports a real delta or explicitly states that no material change occurred.
2. The ECB event dated 2026-06-11 is no longer described as occurring in the 2026-07-14 report week.
3. IEFA's current 24.05% allocation overrides stale absent, limited, watchlist-only, diversification-gap and zero-allocation language.
4. DFEN is treated as the current defense holding; PPA remains available as a challenger/candidate.
5. Specified Dutch mixed-language fragments are removed.
6. The post-sanitizer equity image uses:

```text
MIME email body: cid:equitycurve
standalone delivery HTML: data:image/png;base64,...
```

## Authority rules

- Current runtime positions and weights override static editorial memory.
- Dated events may use relative-week wording only inside the report-week window.
- A non-held ETF may be discussed as an alternative but not as the incumbent.
- The delivery layer restores only the uniquely identified equity image after normal client sanitization.

## Implementation

```text
runtime/report_freshness_contract.py
runtime/standalone_html_equity_embed.py
runtime/build_macro_policy_pack.py
runtime/macro_report_surface.py
runtime/link_runtime_report_tickers.py
send_report_runtime_html.py
tools/render_report_freshness_preview.py
tests/test_report_freshness_and_html_equity.py
tests/test_report_freshness_production_variants.py
.github/workflows/validate-etf-report-freshness-and-html-equity.yml
```

## Preview evidence

```text
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_clean.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_260714_04.pdf
output/weekly_analysis_pro_260714_04_equity_curve.png
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_clean.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.pdf
output/weekly_analysis_pro_nl_260714_04_equity_curve.png
output/validation/etf_report_freshness_260714_04.json
```

## Validation and merge evidence

```text
clean_governance_head: 2864050289b2bf4259e5c2f0375b6b9c42078fed
freshness_workflow_run: 29461019794
freshness_workflow_conclusion: success
post_execution_workflow_run: 29461019772
post_execution_workflow_conclusion: success
PR: #70
merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
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

## Safety boundary

The `_04` package is review evidence only. It was not emailed, did not rerun portfolio execution, did not mutate official state or the trade ledger, and did not overwrite the delivered `_03` package.
