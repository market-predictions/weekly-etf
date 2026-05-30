# Weekly ETF report request

requested_at_utc: 2026-05-30T17:41:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review verification run after fixing the delivery HTML duplicate executive-summary validator.

## Verification focus
- Confirm hidden executive-summary markers are not treated as visible duplicate executive-summary panels.
- Confirm no visible `panel-exec` duplicate remains in delivery HTML/PDF.
- Confirm post-execution/ already-executed wording remains clean: no proposed/pending copy in rendered HTML or PDF.
- Confirm no duplicate portfolio-state or trade-ledger mutation occurs on the already-executed path.
- Confirm GLD/GSG holdings remain arithmetically reconciled.
- Confirm the equity curve remains based on repaired canonical valuation history.
- Confirm final English and Dutch reports pass render and delivery validators.
