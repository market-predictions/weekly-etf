# ETF Report Freshness and Standalone HTML — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`

## 2026-07-16 — Defects identified

The `260714_03` reports correctly reflected the executed URNM-to-XBI rotation, but retained stale editorial memory elsewhere:

- persistent AI and gold conditions appeared under `What changed / Wat veranderde`;
- the 2026-06-11 ECB event was described as happening `this week` in the 2026-07-14 report;
- IEFA was funded at 24.05% while non-U.S. exposure was described as absent, limited, watchlist-only, a diversification gap or zero;
- PPA was described as the current defense implementation although official state contained DFEN;
- Dutch output contained mixed-language fragments;
- the client sanitizer replaced the equity image source with `#harmful-link`.

## 2026-07-16 — Stable decisions

```text
What changed / Wat veranderde is delta-only.
Current runtime positions override static portfolio memory.
Dated events may use relative-week wording only inside the report-week window.
PPA may remain a challenger but may not masquerade as the current holding.
Standalone HTML embeds the equity PNG; MIME email HTML uses CID.
```

## 2026-07-16 — Implementation completed

Added or changed:

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

Behavior changes:

- unchanged regimes explicitly say no material change occurred;
- the June ECB event is absent from the July report-week catalyst block;
- IEFA's current allocation is reflected across radar, risk, allocation and second-order sections;
- DFEN is the current defense holding and PPA remains an alternative;
- specified Dutch hybrid terms are localized;
- post-sanitizer image sources are restored to CID for MIME and data URI for standalone HTML.

## 2026-07-16 — Preview and validation

Non-sending review package:

```text
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_260714_04.pdf
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.pdf
output/validation/etf_report_freshness_260714_04.json
```

Final exact-head gates:

```text
validated_head: 2864050289b2bf4259e5c2f0375b6b9c42078fed
freshness_workflow_run: 29461019794
freshness_workflow_conclusion: success
post_execution_workflow_run: 29461019772
post_execution_workflow_conclusion: success
```

Verified:

- compile and focused/existing regressions pass;
- exact-artifact EN/NL replay passes;
- stale date and current-holding contradictions are absent;
- standalone HTML embeds the graph and contains no CID, placeholder or `#harmful-link`;
- MIME HTML retains CID;
- PDF/PNG assets are non-empty;
- state and trade-ledger hashes remain unchanged;
- `email_sent=false` and `model_execution_replayed=false`.

## 2026-07-16 — Merged and closed

```text
PR: #70
merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
package_status: closed
```

The `_04` package was not emailed and is not a delivery receipt.
