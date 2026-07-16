# ETF Report Freshness and Standalone HTML — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`

## 2026-07-16 — Client-surface freshness defects identified

The `260714_03` English and Dutch reports correctly reflected the executed URNM-to-XBI rotation, but retained stale editorial memory elsewhere.

Confirmed defects:

- persistent AI and gold conditions appeared under `What changed / Wat veranderde`;
- the 2026-06-11 ECB event was described as happening `this week` in the 2026-07-14 report;
- IEFA was funded at 24.05% while non-U.S. exposure was described as absent, limited, watchlist-only, a diversification gap or zero;
- PPA was described as the current defense implementation although official state contained DFEN;
- Dutch output contained mixed-language fragments;
- the client HTML sanitizer replaced the equity image source with `#harmful-link`, so the standalone HTML graph did not display.

## 2026-07-16 — Stable authority decisions

```text
What changed / Wat veranderde is delta-only.
Current runtime positions override static portfolio-memory wording.
Dated events may use relative-week wording only inside the report-week window.
PPA may remain a challenger but may not masquerade as the current holding.
Standalone HTML embeds the equity PNG; MIME email HTML uses CID.
```

## 2026-07-16 — Implementation completed

Added:

```text
runtime/report_freshness_contract.py
runtime/standalone_html_equity_embed.py
tools/render_report_freshness_preview.py
tests/test_report_freshness_and_html_equity.py
tests/test_report_freshness_production_variants.py
.github/workflows/validate-etf-report-freshness-and-html-equity.yml
```

Integrated into:

```text
runtime/build_macro_policy_pack.py
runtime/macro_report_surface.py
runtime/link_runtime_report_tickers.py
send_report_runtime_html.py
```

Behavior changes:

- executive and Section 3 change text is derived from regime-memory deltas;
- unchanged regimes state explicitly that no material change occurred;
- the June ECB event is no longer emitted as a July report-week catalyst;
- IEFA's current 24.05% weight is reflected in the radar, risk, allocation and second-order sections;
- DFEN is treated as the current defense holding, while PPA remains a challenger where appropriate;
- specified Dutch hybrid terms are localized;
- post-sanitizer equity image sources are restored to CID for MIME and embedded data URI for standalone HTML.

Temporary migration and diagnostic helpers were removed after integration.

## 2026-07-16 — Preview package persisted

A non-sending exact-artifact replay created:

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

The `_04` package is review evidence and was not emailed.

## 2026-07-16 — Validation completed

```text
workflow: Validate ETF report freshness and HTML equity
run_id: 29460852590
conclusion: success
```

Verified:

- affected modules compile;
- focused and existing regression tests pass;
- exact-artifact EN/NL replay passes;
- stale relative-date and current-holding contradictions are absent;
- standalone EN/NL HTML embeds the graph and contains no CID, placeholder or `#harmful-link`;
- MIME HTML retains CID for the equity image;
- PDFs and PNGs are present and non-empty;
- state and trade-ledger hashes remain unchanged;
- `email_sent=false` and `model_execution_replayed=false`.

## 2026-07-16 — Merge-ready status

PR #70 is implementation- and governance-complete, subject to one final read-only validation run on the latest PR head. No `_04` delivery claim is authorized.
