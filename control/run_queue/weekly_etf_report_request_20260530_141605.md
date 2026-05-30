# Weekly ETF report request

requested_at_utc: 2026-05-30T14:16:05Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the executed-report finalization authority overlay patch.

## Checks requested
- Confirm guarded-auto model execution still passes.
- Confirm the final executed runtime state remains aligned with official `output/etf_portfolio_state.json` after report finalization.
- Confirm scorecard/report enrichment cannot override shares, prices, market values, weights, cash or NAV.
- Validate GLD/GSG row arithmetic in the final executed runtime state and final EN/NL reports.
- Continue delivery only if the execution-state authority validator passes.
- This is model-portfolio state handling only, not broker order placement.
