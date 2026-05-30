# Weekly ETF report request

requested_at_utc: 2026-05-30T19:25:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review verification run after fixing the last over-cap SMH wording bug.

## Verification focus
- Confirm the Final Action Table no longer says `Best earned use of cash, capped below max position size` for SMH.
- Confirm SMH short reason reads as no fresh cash while above the 25% cap.
- Confirm watchlist / dynamic radar memory marks AI compute / SMH as `Active / capped` rather than plain `Active`.
- Confirm SMH remains Hold / no fresh cash while above the 25% cap in action tables.
- Confirm Structural Opportunity Radar and Best New Opportunities keep the over-cap wording clean.
- Confirm GLD/GSG holdings remain arithmetically reconciled.
- Confirm already-executed GLD to GSG rotation remains no-op and post-execution wording remains clean.
- Confirm equity curve remains based on repaired canonical valuation history and does not inflate.
- Confirm final English and Dutch reports pass render and delivery validators.
