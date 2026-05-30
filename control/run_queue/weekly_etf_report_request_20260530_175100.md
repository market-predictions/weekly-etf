# Weekly ETF report request

requested_at_utc: 2026-05-30T17:51:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the runtime-state scorecard authority fix.

## Checks requested
- Confirm scorecard enrichment cannot overwrite execution-critical fields in runtime state.
- Confirm GLD remains the canonical post-rotation share count, not 29 shares.
- Confirm Section 8 / Section 15 holdings row arithmetic reconciles: shares × price = local market value, FX conversion = EUR value, EUR value / NAV = weight.
- Confirm valuation history remains repaired and the equity curve does not inflate from duplicate execution.
- Confirm already-executed GLD to GSG rotation produces an idempotent artifact and does not mutate state or ledger.
- Validate trade-ledger idempotency before and after guarded execution.
- Confirm final EN/NL reports pass render and delivery validators.
