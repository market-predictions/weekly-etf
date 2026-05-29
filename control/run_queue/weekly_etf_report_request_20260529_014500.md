# Weekly ETF report request

requested_at_utc: 2026-05-29T01:45:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue one more fresh Weekly ETF Review run to validate the branded PDF/HTML delivery layer after making delivery HTML overrides rotation-aware.

## Regression focus
- Confirm the PDF delivery layer no longer overwrites rotation-aware markdown with legacy Section 2, Current Position Review, or Portfolio Rotation Plan labels.
- Confirm Section 2 / Portfolio Action Snapshot shows rotation-aware buckets: add/destination, hold, hold-with-override, proposed replace/reduce, close.
- Confirm Section 2 no longer says no replacement is promoted when trade_intents[] proposes GLD to GSG.
- Confirm Current Position Review shows rotation-engine action where available, especially GLD as Replace partial to GSG when applicable.
- Confirm Portfolio Rotation Plan is derived from rotation_decisions and not legacy suggested_action labels.
- Confirm Final Action Table remains rotation-aware with target weights, release scores and trade-intent destination.
- Confirm Section 14 remains Proposed Position Changes / Rotation Trade Intents and does not imply execution while warning mode is active.
- Confirm Section 16 continuity notes proposed rotation and preserves actual holdings/state as separate from trade intent.
- Keep rotation discipline in warning-only mode for this test.
- Continue existing pricing, Dutch quality, bilingual parity, HTML/PDF render and delivery gates.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
