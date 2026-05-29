# Weekly ETF report request

requested_at_utc: 2026-05-29T02:35:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue a fresh Weekly ETF Review run after wiring client-surface cleanliness validators into the workflow.

## Regression focus
- Confirm runtime reports receive the exact runtime-state path in post-render scripts.
- Confirm markdown Final Action Table uses client-facing rationale/toelichting instead of internal reason-code labels.
- Confirm English and Dutch markdown contain no internal snake_case labels.
- Confirm Dutch markdown contains no Redencodes / Reason codes.
- Confirm delivery HTML contains no internal snake_case labels.
- Confirm prose does not say reduce/verlaag a ticker by/met a negative percentage.
- Confirm proposed rotation intent remains proposed and not executed while warning mode is active.
- Confirm actual holdings remain separate from trade_intents until a model-execution layer is explicitly enabled.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
