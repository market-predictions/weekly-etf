# Weekly ETF report request

requested_at_utc: 2026-05-30T19:05:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review verification run after hardening the over-cap actionability language contract.

## Verification focus
- Confirm over-cap tickers such as SMH do not appear with `Actionable now` unless the same row/sentence clearly states no fresh capital while above cap.
- Confirm over-cap tickers do not appear with `leading funded growth exposure` or `candidate for additional capital` unless the same sentence clearly states no fresh capital while above cap.
- Confirm SMH remains Hold / no fresh cash while above the 25% cap in action tables.
- Confirm Structural Opportunity Radar describes SMH as structurally actionable but capped/no fresh capital while above cap.
- Confirm Best New Opportunities describes SMH as best earned exposure, but no fresh capital while above cap.
- Confirm GLD/GSG holdings remain arithmetically reconciled.
- Confirm already-executed GLD to GSG rotation remains no-op and post-execution wording remains clean.
- Confirm equity curve remains based on repaired canonical valuation history and does not inflate.
- Confirm final English and Dutch reports pass render and delivery validators.
