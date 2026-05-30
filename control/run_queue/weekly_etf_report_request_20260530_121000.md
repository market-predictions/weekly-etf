# Weekly ETF report request

requested_at_utc: 2026-05-30T12:10:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Run a fresh Weekly ETF Review after fixing model-execution NAV drift by capping execution notional to the live available value of the source holding.

## Regression focus
- Confirm shadow model execution no longer produces NAV drift when source value is smaller than requested 5% NAV rotation size.
- Confirm source sell notional is capped to available source value when needed.
- Confirm destination buy notional equals actual source sell notional, not stale requested notional.
- Confirm the model does not repeatedly buy another 5% destination without matching funded source value.
- Confirm Section 14 and Section 15 reconcile after guarded execution and final report rebuild.
- Confirm official trade ledger rows reflect actual share deltas and post-trade portfolio state.
- Confirm this remains model execution only and does not imply broker execution.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
