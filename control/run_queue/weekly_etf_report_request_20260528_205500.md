# Weekly ETF report request

requested_at_utc: 2026-05-28T20:55:00Z
requested_run_date: 2026-05-28
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue a fresh Weekly ETF Review rerun after the replacement-duel model was changed from free-form English prose to canonical decision/trigger codes with language-native EN/NL rendering.

## Regression focus
- Confirm `runtime/replacement_duel_v2.py` no longer leaks English decision text into the Dutch markdown.
- Confirm the Dutch localization gate passes without one-by-one phrase patches.
- Confirm EN/NL reports are generated from the same pricing audit and runtime state.
- Confirm pricing, bilingual numeric parity, HTML/PDF validation, delivery HTML validation and email gates pass before delivery.

## Fresh-pricing requirements
- Run the persistent ETF pricing pass first.
- Use the latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Prefer exact close-date coverage for all current holdings.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
