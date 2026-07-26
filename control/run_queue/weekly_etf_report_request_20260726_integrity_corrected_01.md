# Weekly ETF report request — portfolio-integrity corrected package

Requested: 2026-07-26
Repository: `market-predictions/weekly-etf`
Mode: production Weekly ETF Pro, English and Dutch
Close basis: latest completed U.S. market close
Portfolio execution authorized: no
Broker execution authorized: no

## Required gates

- Use the official portfolio state and immutable run-scoped pricing audit.
- Apply and pass the portfolio/watchlist integrity contract.
- Non-held tickers may appear only as explicitly labelled benchmarks, challengers, alternatives, short candidates, or watchlist instruments.
- PPA and ITA must not be described as current holdings or portfolio risks.
- SPY must be labelled as a benchmark wherever referenced.
- Continuity P/L must use the same ledger-derived attribution basis as the position-performance section.
- Fresh valuation history must not be described as carried forward.
- Zero-trade output must not claim a consumed rotation limit or a current-run execution.
- Regime duration must not count repeated runs for one report date as separate weekly observations.
- ECB policy wording must reflect the latest decision applicable to the report date.
- Dutch client surfaces must not contain raw English reason codes.
- Preserve the 9/8 close-first constraint and open no new ticker.

Generate, validate, render, and send only if all production gates pass. Persist the run and delivery manifests.
