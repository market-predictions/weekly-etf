# ETF Lane Discovery Contract

## Purpose

This contract defines the discovery layer that sits before runtime state build and report rendering.

The Structural Opportunity Radar must not be a static prompt memory or a small manually curated watchlist. It must be produced from a broad ETF universe, scored lanes, current portfolio gaps, and novelty/challenger rules.

## Four-layer placement

1. **Decision framework** — open discovery, score lanes, promote only the best.
2. **Input/state contract** — `config/etf_discovery_universe.yml`, latest pricing audit, latest portfolio state, prior lane artifacts.
3. **Output contract** — `output/lane_reviews/etf_lane_assessment_YYMMDD.json` with machine-readable evidence fields.
4. **Operational runbook** — workflow runs discovery after pricing pass and before runtime state build.

## Discovery authority order

Lane discovery uses these inputs:

1. `config/etf_discovery_universe.yml` — broad investable ETF universe and lane metadata
2. latest `output/pricing/price_audit_*.json` — close data availability and pricing confidence
3. `output/etf_portfolio_state.json` — current holdings and portfolio gaps
4. latest prior `output/lane_reviews/etf_lane_assessment_*.json` — continuity, retained lanes, prior promotions

## Required discovery behavior

Each run must:

- evaluate all configured lanes
- represent every required breadth bucket
- include candidates outside current holdings where available
- include at least four challengers
- include at least two challengers outside the prior live radar where available
- include at least two challengers outside current held portfolio themes where available
- promote 5 to 8 highest-ranked lanes to the live radar
- publish omitted-but-assessed lanes as proof of breadth without bloating the client report

## Lane scoring fields

Every assessed lane must include at minimum the existing production fields:

- lane_name
- taxonomy_tag
- bucket
- primary_etf
- alternative_etf
- structural_strength
- persistence
- implementation_quality
- macro_alignment
- second_order_relevance
- timing_confirmation
- valuation_crowding
- portfolio_differentiation
- total_score
- prior_run_status
- promoted_to_live_radar
- challenger
- rejection_reason
- what_would_change

Additional discovery fields should include:

- discovery_source
- novelty_status
- portfolio_gap_score
- pricing_confidence
- primary_price_status
- alternative_price_status
- evidence_summary
- why_now
- freshness_note

## What this layer is not

It is not a replacement for the editorial report.
It is not a signal to automatically trade every promoted lane.
It is not allowed to fabricate price history or claim fresh evidence when the pricing audit does not support it.

## Current limitation

Until a full historical price fetch layer is added, this discovery engine is a structured breadth and scoring layer, not a complete technical momentum scanner. It can use latest close availability and configured timing priors, but true 1-month and 3-month relative-strength ranks require a future historical data layer.

## Next maturity step

Add a historical ETF returns layer that computes:

- 1-month relative strength rank
- 3-month relative strength rank
- 20/50-day trend quality
- volatility and drawdown filters
- liquidity filters
- relative strength versus SPY and versus current holdings
