# Weekly ETF report request

requested_at_utc: 2026-05-30T13:56:20Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the execution validator follow-up fixes.

## Checks requested
- Use official portfolio state as execution authority.
- Clear stale prior-run execution metadata before shadow and guarded execution.
- Treat zero current weights as valid values; do not fall through to stale legacy weight fields.
- Validate row-level arithmetic before delivery.
- Confirm final EN/NL reports are rebuilt from executed portfolio state only.
- This is model-portfolio state handling only, not broker order placement.
