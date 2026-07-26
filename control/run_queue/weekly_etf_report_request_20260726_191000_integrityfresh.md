# Weekly ETF report request — fresh integrity-validated delivery

requested_at_utc: 2026-07-26T19:10:00Z
requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: 2026-07-24
strict_fresh_pricing_required: true
portfolio_execution_authorized: false
broker_execution_authorized: false
delivery_authorized: true
supersedes_prior_2026_07_24_deliveries: true
requirements:
  - Run the full production pricing, relative-strength, macro, discovery, rotation, runtime-state, bilingual-render and delivery pipeline from current main.
  - Use the latest completed U.S. regular-session close, 2026-07-24; do not fabricate a later close.
  - Reprice all nine official holdings and fail closed if fresh coverage is insufficient.
  - Preserve official whole-share positions, cash and trade ledger; no model or broker execution is authorized.
  - Enforce the 9-active-versus-8-maximum close-first contract and introduce no new ticker.
  - Apply the portfolio-integrity contract: non-held tickers may appear only as explicit benchmarks, challengers, alternatives, short candidates or watchlist instruments.
  - Do not describe PPA, SPY, DFEN or any other non-held ticker as held, replaceable, reducible, closable or under current-position review.
  - Exclude leveraged ETFs from allocation recommendations because leverage is prohibited.
  - Reconcile holdings, weights, NAV, cash, valuation history, position performance and action surfaces against the run-scoped runtime state.
  - Remove stale execution, rotation-budget, carried-forward-pricing, repeated-regime-duration, untranslated reason-code and duplicate-rationale language.
  - Produce consistent English and Dutch Markdown, designed HTML, PDF and equity-curve outputs.
  - Deliver both languages with PDF, clean Markdown, full HTML and equity-curve attachments.
  - Delivery success requires a successful final run manifest, bilingual delivery manifest and independent inbox receipt.
