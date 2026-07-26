# WP_REPORT_PORTFOLIO_INTEGRITY_AND_STALE_SURFACE

Date: 2026-07-26
Repository: `market-predictions/weekly-etf`
Layer: decision framework + input/state contract + output contract + operational runbook
Status: claimed / implementation active

## Purpose

Remove portfolio-versus-watchlist category errors and stale client-surface content from the Weekly ETF report, then protect the report with deterministic bilingual integrity checks.

## Triggering defects

1. PPA and SPY were described as current portfolio risks or active position reviews although neither ticker is held.
2. The continuity table used stale P/L fields while section 7A used reconstructed ledger entry bases.
3. A fully fresh valuation was described as carried forward and one Dutch history row retained English wording.
4. Zero-trade output retained stale current-run execution/churn language.
5. Regime duration counted repeated production runs as weekly observations.
6. ECB wording did not reflect the 2026-07-23 unchanged-rate decision.
7. Raw English reason codes and duplicate rationale fragments leaked into the Dutch action table.
8. Static allocation labels conflated Europe, developed ex-US and non-USD exposure.

## Authority rules

- `output/etf_portfolio_state.json` and the run-scoped runtime state define current holdings.
- Non-held ETFs may appear only as explicitly labelled benchmarks, challengers, alternatives, short candidates or watchlist instruments.
- Holdings-oriented sections may not describe a non-held ticker as held, replaceable, reducible, closable or under current-position review.
- Section 7A and continuity input must use one attribution basis.
- A run with zero trade intents and no current-run execution may not claim a consumed rotation or an executed/reflected allocation change.
- Fresh pricing coverage may not be described as carried forward.
- Report-regime duration may not be inferred from repeated reruns for the same report date.
- No portfolio execution, share-count change, cash mutation or trade-ledger mutation is authorized by this package.

## Exact implementation scope

- Add a shared bilingual report-integrity contract and validator.
- Apply it in the existing ticker-link/freshness production stage.
- Rebuild state-aware risks, conclusion, second-order effects, continuity watchlist and change summary.
- Reconcile continuity P/L with ledger-derived attribution.
- Normalize valuation-history and action-reason language.
- Remove rerun-count and stale policy wording from the client surface.
- Add exact-state regression tests using the July 24 runtime state.
- Generate a corrected package only after read-only validation passes.

## Delivery boundary

A corrected report may be sent only after the exact English/Dutch Markdown and rendered HTML/PDF surfaces pass the new integrity gate. Delivery success still requires a delivery manifest and inbox receipt.
