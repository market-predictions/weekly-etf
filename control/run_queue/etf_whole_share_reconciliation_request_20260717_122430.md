# ETF whole-share reconciliation request

requested_at_utc: 2026-07-17T12:24:30Z
requested_by: ChatGPT
repository: market-predictions/weekly-etf
mode: official-state-reconciliation
runtime_state: output/runtime/etf_report_state_20260716_20260717_094728.json
close_tickers: DFEN
production_send: false
note: Reconcile all legacy fractional holdings to whole shares using the persisted 2026-07-16 runtime pricing and FX basis. Close DFEN because the active portfolio constraints prohibit leveraged ETFs. Transfer released value to EUR cash, preserve NAV within EUR 0.05, append reconciliation ledger evidence, and send no email.
