# Weekly ETF report request

requested_at_utc: 2026-05-30T19:42:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review verification run after fixing linked-ticker over-cap scrub timing.

## Verification focus
- Confirm the English Final Action Table no longer says `Best earned use of cash, capped below max position size` for SMH.
- Confirm the English continuity watchlist marks AI compute / SMH as `Active / capped` rather than plain `Active`.
- Confirm linked tickers are handled by the over-cap client-surface scrubber.
- Confirm the scrubber runs after guarded-auto finalization and before delivery render/validation.
- Confirm Dutch output remains clean and no regression is introduced.
- Confirm GLD/GSG holdings remain arithmetically reconciled.
- Confirm already-executed GLD to GSG rotation remains no-op and post-execution wording remains clean.
- Confirm equity curve remains based on repaired canonical valuation history and does not inflate.
- Confirm final English and Dutch reports pass render and delivery validators.
