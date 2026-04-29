# ETF run queue

This folder contains small operational trigger files for repo-native pre-report actions.

## Persistent ETF pricing audit

To run the persistent pricing preflight before generating a new Weekly ETF Review, create a file matching:

`control/run_queue/etf_pricing_request_YYYYMMDD_HHMMSS.md`

The `Persist ETF pricing audit` workflow will:
1. run `python -m pricing.run_pricing_pass`,
2. write `output/pricing/price_audit_YYYY-MM-DD.json`,
3. validate the audit shape,
4. commit the audit back to GitHub if it changed.

The production send workflow no longer runs pricing itself. It validates that a persisted audit exists before rendering or sending.

This prevents temporary runner-only pricing files and avoids a race between report publication and pricing persistence.
