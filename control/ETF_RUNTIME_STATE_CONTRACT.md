# ETF Runtime State Contract

## Purpose

This contract defines the deterministic ETF report runtime layer.

The runtime layer exists to stop treating the latest markdown report as the hidden database for holdings, pricing, continuity, and recommendations.

Markdown reports are presentation output. They are not the primary state authority.

## Authority order

The ETF runtime state must be built from these sources, in this order:

1. `output/etf_portfolio_state.json` — holdings, cash, prior NAV, position metadata, implemented state
2. `output/pricing/price_audit_YYYY-MM-DD.json` — latest market/pricing audit and FX basis
3. `output/lane_reviews/etf_lane_assessment_YYMMDD.json` — research breadth and lane ranking
4. `output/etf_recommendation_scorecard.csv` — capital re-underwriting and recommendation memory
5. prior markdown report — historical display context only, never primary holdings authority

## Normalized runtime output

The runtime builder writes:

`output/runtime/etf_report_state_YYYYMMDD.json`

Minimum fields:

- `report_date`
- `requested_close_date`
- `source_files`
- `portfolio`
- `positions`
- `cash`
- `valuation`
- `pricing`
- `replacement_duels`
- `lane_assessment`
- `recommendation_scorecard`
- `actions`
- `validation_flags`

## Section 15 generation rule

Section 15 must be generated from:

- `output/etf_portfolio_state.json`
- latest pricing audit

Do not parse Section 15 from an older markdown report to generate a new Section 15.

## Pricing pass holdings rule

The pricing pass must price current holdings from:

- `output/etf_portfolio_state.json`

It must not scan `weekly_analysis_pro_*.md` for current holdings.

Markdown can still be used as historical display context, but not as the live holdings source.

## Replacement duel rule

If a report names replacement challengers, they must be present in runtime state with one of these statuses:

- `fundable_replacement_candidate`
- `priced_but_duel_incomplete`
- `not_fundable_pricing_missing`
- `not_fundable_duel_incomplete`

A challenger is not fundable until the runtime state contains verified close data and a completed comparison basis.

## Bilingual render rule

English is canonical. Dutch is a companion render derived from the same runtime state.

The Dutch report must not rerun research, repricing, rankings, actions, numbers, holdings, or caveats.

## Operational consequence

A future production workflow should run:

1. pricing pass from explicit state
2. pricing audit validation
3. runtime state build
4. English markdown render
5. Dutch markdown render
6. report validation
7. PDF render
8. email send
9. delivery manifest write

Until full renderer migration is complete, the runtime builder acts as the normalized bridge between state artifacts and markdown reports.
