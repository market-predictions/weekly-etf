# Weekly ETF production run request

requested_at_utc: 2026-05-27T00:00:01Z
requested_run_date: 2026-05-27
mode: fresh-production-review
note: Generate a fresh Weekly ETF Review using the current production workflow, including immutable pricing audit, fresh close discovery, challenger fundability validation, persisted valuation state, bilingual report render, PDF/email delivery, final run manifest, and artifact commit-back.

## Validation targets

- PRICING_AUDIT_PATH_OK
- LANE_ARTIFACT_PATH_OK
- ETF_CHALLENGER_FUNDABILITY_CONTRACT_OK
- ETF_RUNTIME_STATE_OK
- ETF_PRICE_BASIS_DISCLOSURE_ADDED
- ETF_EQUITY_CURVE_HISTORY_OK
- ETF_VALUATION_STATE_PERSISTED
- ETF_PERSISTED_VALUATION_STATE_OK
- ETF_RUN_MANIFEST_OK
- RENDER_OK
- successful delivery receipt / manifest if email send completes
