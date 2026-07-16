# WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-report-freshness-and-html-equity-graph`
Layer: input/state contract + output contract + operational runbook
Status: validated / merge ready

## Current issue

The corrected `260714_03` report resolved the post-execution URNM-to-XBI action contradiction, but a wider client-surface review identified additional freshness and rendering defects:

1. `What changed / Wat veranderde` published persistent threshold states as if they were new weekly changes.
2. The ECB event dated 2026-06-11 was described as occurring `this week / deze week` in the report dated 2026-07-14.
3. IEFA was a funded holding at 24.05%, while several sections described non-U.S. exposure as watchlist-only, a diversification gap, limited, absent or zero.
4. PPA was described as if it were the current defense holding, while official state contained DFEN and did not contain PPA.
5. The standalone HTML equity image was sanitized to `#harmful-link`; neither the MIME CID nor the standalone data URI survived the final client sanitizer.
6. The Dutch surface retained English or hybrid terms.

## Decision framework

`What changed / Wat veranderde` must answer a delta question. It may contain:

- a regime transition;
- a material breadth or cross-asset change;
- a genuinely new policy event in the report week;
- an explicit conclusion that no material change occurred, followed by concise continuity context.

A persistent condition may not be presented as a change merely because it still clears a threshold.

## Input/state contract

Authority order:

1. current official runtime positions and weights;
2. dated event fields in the macro pack;
3. regime-memory transition fields;
4. current market evidence;
5. static editorial templates only where they do not contradict items 1-4.

Consequences:

- IEFA current weight overrides old zero-allocation/watchlist wording;
- DFEN current holding overrides old PPA-as-incumbent wording;
- a dated policy event may use `this week` only inside the report-week window;
- PPA may remain visible as a challenger/candidate where factually relevant.

## Output contract

English and Dutch reports now:

- use delta-only wording in the executive summary and Section 3;
- remove stale relative-date policy wording;
- describe IEFA and DFEN consistently across the report;
- preserve PPA as a candidate rather than a current holding;
- remove specified Dutch mixed-language fragments;
- keep the executed URNM/XBI action surfaces unchanged.

HTML authority is split by surface:

```text
MIME email body: cid:equitycurve
standalone delivery HTML: data:image/png;base64,...
```

The final post-sanitizer helper restores only the identified equity image source. Other links and images are not modified.

## Implemented files

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

Temporary migration scripts and diagnostic workflows were removed after the integrated source and preview evidence were persisted.

## Preview evidence

Exact-artifact, non-sending replay source:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
```

Persisted preview package:

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

## Validation evidence

Final read-only workflow:

```text
workflow: Validate ETF report freshness and HTML equity
run_id: 29460852590
conclusion: success
```

Passed gates:

- affected modules compile;
- focused freshness, production-phrase, equity, post-execution and cockpit tests pass;
- exact-artifact `_04` replay succeeds;
- English and Dutch freshness assertions pass;
- standalone HTML contains an embedded equity PNG and no CID, placeholder or `#harmful-link`;
- MIME email HTML retains the CID contract;
- English and Dutch PDF/PNG assets are non-empty;
- official portfolio-state hash is unchanged;
- official trade-ledger hash is unchanged;
- validation evidence records `email_sent=false` and `model_execution_replayed=false`.

## Safety boundary

This package did not:

- send email;
- rerun portfolio allocation or model execution;
- mutate `output/etf_portfolio_state.json`;
- mutate `output/etf_trade_ledger.csv`;
- overwrite the delivered historical `_03` package.

## Merge boundary

PR #70 is validated and may be promoted and merged after the final governance-head workflow passes. The `_04` package is review evidence, not a delivered report. Any delivery requires separate explicit authorization and real delivery evidence.
