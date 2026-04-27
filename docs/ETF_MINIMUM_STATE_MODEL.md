# ETF minimum state model

This document describes the first **explicit ETF production state layer** in `weekly-etf`.

## Purpose

The goal is to make the ETF system less dependent on prior-report parsing alone by introducing a minimum machine-readable implementation layer.

The first minimum state files are:
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`

## Why this exists

ETF previously relied mainly on:
- prior report parsing
- pricing-pass logic
- prompt-layer continuity

That was workable, but weaker than the explicit state-file model already used in FX.

This minimum state model is the first step toward better authority boundaries and easier downstream comparison work.

## Current authority rule

For ETF, this minimum state layer is currently derived from the latest canonical English pro report, specifically:
- **Section 15** for current holdings, cash, and portfolio totals
- **Section 7** for equity-curve history and valuation context

So this is still a **report-derived explicit state layer**, not yet a fully independent implementation engine.

## Files

### 1. `output/etf_portfolio_state.json`
This file is the machine-readable snapshot of the current ETF portfolio.

It currently captures:
- schema version
- portfolio mode
- base currency
- valuation source
- optional matching pricing-audit filename when present
- inception date
- starting capital
- invested market value
- cash
- NAV
- peak NAV
- max drawdown
- current positions
- last report metadata
- last valuation metadata

### 2. `output/etf_valuation_history.csv`
This file is the machine-readable valuation history for the ETF portfolio.

It currently captures:
- date
- NAV in EUR
- cash in EUR when available
- invested market value in EUR when available
- daily return percent
- since-inception return percent
- drawdown percent
- EUR/USD used when available
- valuation comment
- source report

## Update flow

The state refresh path now has two roles:

### A. Pre-send derivation validation
The production send workflow validates that the latest pro report can be converted into the minimum ETF state model before email delivery.

### B. Persistent repo refresh
A dedicated workflow refreshes and commits:
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`

when a new canonical English pro report is pushed to `main`.

This keeps delivery and state-authority refresh related, but not collapsed into a single risky commit-from-send step.

## Current limitations

This is intentionally a **minimum** state model.

It does **not yet** provide:
- explicit trade history
- recommendation score history
- fully independent valuation logic outside the report
- authoritative average-entry bookkeeping in state

Those belong to later stages.

## Next likely extensions

After this minimum layer stabilizes, the next likely state additions are:
- `output/etf_trade_ledger.csv`
- `output/etf_recommendation_scorecard.csv`

Only after the minimum state model is trusted should ETF add deeper comparison layers such as:
- current portfolio vs optimizer reference portfolios
- concentration-gap diagnostics
- optimizer-vs-discretion QA summaries
