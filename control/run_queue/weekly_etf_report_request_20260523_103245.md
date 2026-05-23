# Weekly ETF report request

requested_at_utc: 2026-05-23T10:32:45Z
requested_run_date: 2026-05-23
mode: pro
requested_close_date: 2026-05-22
pricing_basis_requested: completed U.S. regular-session close for 2026-05-22, fetched after Friday close data should be available
strict_fresh_pricing_required: true

## User request
User attached `weekly_analysis_pro_nl_260522.pdf` and noted that the report may not have fetched the latest Friday evening closing prices. Run a new fresh Weekly ETF report that does.

## Fresh-pricing requirements for this rerun
- Run the persistent ETF pricing pass first.
- Reprice every current holding ticker individually against the completed 2026-05-22 U.S. regular-session close where available.
- Current holdings requiring explicit fresh close validation: SPY, SMH, PPA, PAVE, URNM, GLD.
- Validate EUR/USD basis used for EUR conversion.
- Do not publish a portfolio valuation whose latest Section 7 row is merely described as `Doorgeschoven waardering` if fresh 2026-05-22 close data is available.
- If any current holding cannot be confirmed on the 2026-05-22 close, fail loud and list the blocking ticker(s), rather than publishing a stale or carried-forward portfolio valuation.
- Section 7 latest portfolio value must reconcile exactly to Section 15 / current positions and cash.
- The pricing audit should make clear which tickers used 2026-05-22 close data and which, if any, were carried forward.
- Render and send only if pricing, bilingual numeric parity, HTML/PDF validation, and email gates pass.

## Reason for rerun
The attached Dutch PDF contains language suggesting the 2026-05-22 valuation may have been carried forward from the pricing audit and explicit portfolio state rather than clearly refreshed late Friday after all closing prices were available.
