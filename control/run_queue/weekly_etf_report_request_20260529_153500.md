# Weekly ETF report request

requested_at_utc: 2026-05-29T15:35:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Run a fresh Weekly ETF Review after moving guarded model execution into the effective report path by rebuilding the report from the executed portfolio state.

## Regression focus
- Confirm guarded_auto model execution writes official model trade-ledger rows when all hard gates pass.
- Confirm output/etf_portfolio_state.json is updated before final report delivery.
- Confirm final EN/NL report pair is rebuilt from the executed portfolio state, not from the pre-execution runtime state.
- Confirm Section 15 shows the reduced GLD position and added GSG position if GLD -> GSG still passes generic rules.
- Confirm Section 14 shows executed model changes rather than only proposed trade intents after execution.
- Confirm continuity input for next run starts from the executed holdings.
- Confirm the delivered PDF no longer says the GLD -> GSG trade is still pending if the guarded execution has already written the ledger and portfolio state.
- Confirm this remains model execution only and does not imply broker execution.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
