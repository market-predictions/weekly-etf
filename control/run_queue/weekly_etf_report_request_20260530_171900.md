# Weekly ETF report request

requested_at_utc: 2026-05-30T17:19:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the Dutch standalone month localization fix.

## Checks requested
- Confirm Dutch date localization no longer leaves standalone English month tokens such as `May`.
- Continue to validate trade-ledger idempotency before and after guarded execution.
- Use `runtime.model_execution_guarded_auto` for guarded execution.
- Confirm already-executed same-date GLD to GSG rotation does not mutate portfolio state or ledger.
- Confirm equity curve remains based on repaired canonical valuation history and does not inflate from duplicate execution.
- Confirm final EN/NL reports pass render and delivery validators.
