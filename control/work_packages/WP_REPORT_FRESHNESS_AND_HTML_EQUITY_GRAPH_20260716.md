# WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-report-freshness-and-html-equity-graph`
Layer: input/state contract + output contract + operational runbook
Status: implementation in progress

## Current issue

The corrected `260714_03` report resolved the post-execution URNM-to-XBI action contradiction, but a wider client-surface review identified additional freshness and rendering defects:

1. `What changed / Wat veranderde` publishes persistent threshold states as if they were new weekly changes.
2. The ECB rate event dated 2026-06-11 is still described as occurring `this week / deze week` in the report dated 2026-07-14.
3. IEFA is an approximately 24% funded holding, while several report sections still describe non-U.S. exposure as watchlist-only, a diversification gap, or a zero allocation.
4. PPA is described as if it were the current defense holding, while current official state contains DFEN and does not contain PPA.
5. The attached standalone HTML uses `cid:equitycurve`, which resolves inside the multipart email but not when the HTML file is opened independently.
6. The Dutch surface retains several English or hybrid terms.

## Decision framework

`What changed / Wat veranderde` must answer a delta question. It may contain:

- a regime transition;
- a material breadth or cross-asset change;
- a genuinely new policy event in the report week;
- an explicit conclusion that no material change occurred, followed by concise continuity context.

A persistent condition may not be presented as a change merely because it still clears a threshold.

## Input/state contract

Authority order for freshness corrections:

1. current official runtime positions and weights;
2. dated event fields in the macro pack;
3. regime-memory transition fields;
4. current market evidence;
5. static editorial templates only where they do not contradict items 1-4.

Consequences:

- IEFA current weight overrides old zero-allocation/watchlist wording;
- DFEN current holding overrides old PPA-as-incumbent wording;
- a dated policy event may be called `this week` only when its date falls inside the report-week window;
- PPA may remain visible as a challenger/candidate where factually relevant.

## Output contract

English and Dutch reports must:

- use delta-only wording in the executive summary and Section 3;
- remove stale relative-date policy wording;
- describe current funded holdings consistently across Sections 4-10;
- preserve legitimate challenger analysis;
- remove specified Dutch mixed-language fragments;
- keep the executed URNM/XBI action surfaces unchanged.

Standalone HTML must:

- contain the equity graph as an embedded `data:image/png;base64,...` resource;
- contain no `cid:equitycurve` reference;
- contain no visible equity placeholder.

The MIME email body may continue to use CID because that is the correct transport contract for inline email images.

## Operational runbook

Create a non-sending exact-artifact replay from:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
```

Expected preview artifacts:

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

## Safety boundary

This package must not:

- send email;
- rerun portfolio allocation or model execution;
- mutate `output/etf_portfolio_state.json`;
- mutate `output/etf_trade_ledger.csv`;
- overwrite or rewrite the delivered historical `_03` package.

## Required validation

- deterministic integration patch applies cleanly and idempotently;
- affected Python modules compile;
- focused freshness and standalone-HTML tests pass;
- exact-artifact `_04` replay succeeds;
- EN/NL reports pass freshness validation;
- EN/NL standalone HTML files embed their equity PNG;
- EN/NL PDF and PNG assets exist and are non-empty;
- official state hash remains unchanged;
- official trade-ledger hash remains unchanged;
- validation evidence records `email_sent=false`.

## Completion boundary

The package closes only after:

1. source changes are merged;
2. focused workflow is green;
3. `_04` artifacts and validation evidence are persisted;
4. current control state and next actions are updated;
5. no delivery claim is made for `_04` unless a separate explicit send is authorized and evidenced.
