# ETF minimum state model

This document describes the first **explicit ETF production state layer** in `weekly-etf`.

## Purpose

The goal is to make the ETF system less dependent on prior-report parsing alone by introducing a machine-readable implementation layer.

The current explicit ETF state files are:
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `output/etf_trade_ledger.csv`

## Why this exists

ETF previously relied mainly on:
- prior report parsing
- pricing-pass logic
- prompt-layer continuity

That was workable, but weaker than the explicit state-file model already used in FX.

This explicit ETF state layer is the next step toward better authority boundaries and easier downstream comparison work.

## Current authority rule

For ETF, the current state layer is derived from the latest canonical English pro report, specifically:
- **Section 7** for equity-curve history and valuation context
- **Section 13** for target weights, suggested actions, conviction, and portfolio role
- **Section 14** for executed change rows and funding notes
- **Section 15** for current holdings, cash, and portfolio totals
- **Section 16** for continuity details such as average entry, thesis, and role

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
- linked trade-ledger filename
- linked future recommendation-scorecard filename placeholder
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

Each current position now also carries richer explicit metadata where available, including:
- inherited weight
- target weight
- suggested action
- conviction tier
- total score
- portfolio role
- continuity average entry
- continuity P/L
- original thesis
- previous weight
- weight change this run
- share delta this run
- action executed this run
- funding note

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

### 3. `output/etf_trade_ledger.csv`
This file is the machine-readable ETF trade/change ledger.

It currently captures explicit report-derived change rows only when the canonical report shows a genuine executed change signal, such as:
- non-zero share delta
- non-`None` action executed in Section 14

The ledger currently stores:
- trade ID
- trade date
- source report
- ticker
- action
- shares delta
- previous weight
- new weight
- weight change
- target weight
- conviction tier
- portfolio role
- funding note

## Update flow

The state refresh path now has two roles:

### A. Pre-send derivation validation
The production send workflow validates that the latest pro report can be converted into:
- the ETF portfolio state
- the ETF valuation history
- the ETF trade ledger

before email delivery.

### B. Persistent repo refresh
A dedicated workflow refreshes and commits:
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `output/etf_trade_ledger.csv`

when a new canonical English pro report is pushed to `main`.

This keeps delivery and state-authority refresh related, but not collapsed into a single risky commit-from-send step.

## Current limitations

This is still an intentionally staged ETF state model.

It does **not yet** provide:
- recommendation score history as a separate machine-readable file
- fully independent valuation logic outside the report
- fully authoritative historical average-entry bookkeeping outside continuity sections
- a fully independent implementation engine equivalent to the more mature FX state path

## Next likely extensions

After this enriched layer stabilizes, the next likely state addition is:
- `output/etf_recommendation_scorecard.csv`

Only after the ETF state layer is trusted should ETF add deeper comparison layers such as:
- current portfolio vs optimizer reference portfolios
- concentration-gap diagnostics
- optimizer-vs-discretion QA summaries
