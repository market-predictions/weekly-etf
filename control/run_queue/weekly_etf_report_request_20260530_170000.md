# Weekly ETF report request

requested_at_utc: 2026-05-30T17:00:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the state repair and idempotent guarded execution workflow patch.

## Checks requested
- Use repaired canonical portfolio state and valuation history.
- Validate trade-ledger idempotency before guarded execution.
- Use `runtime.model_execution_guarded_auto`, not the direct guarded-auto mutation path.
- If the same trade-date/source/destination rotation already exists, produce an `already_executed` artifact and do not write portfolio state or trade ledger rows.
- Validate trade-ledger idempotency again after guarded execution.
- Confirm the equity curve does not inflate from duplicate model execution.
- Confirm final EN/NL reports reconcile to official portfolio state and pass render/delivery validators.
- This is model-portfolio state handling only, not broker order placement.
