# ETF Lane Discovery Contract

## Purpose

This contract defines the discovery layer that sits before runtime state build and report rendering.

The Structural Opportunity Radar must not be a static prompt memory or a small manually curated watchlist. It must be produced from a broad ETF universe, scored lanes, current portfolio gaps, novelty/challenger rules, historical relative-strength evidence, and targeted challenger pricing where available.

## Four-layer placement

1. **Decision framework** — open discovery, score lanes, promote only the best.
2. **Input/state contract** — `config/etf_discovery_universe.yml`, latest pricing audit, historical relative-strength metrics, targeted challenger pricing, latest portfolio state, prior lane artifacts.
3. **Output contract** — `output/lane_reviews/etf_lane_assessment_YYMMDD.json` with machine-readable evidence fields.
4. **Operational runbook** — workflow runs historical relative-strength fetch, first-pass discovery, targeted challenger pricing, and final discovery before runtime state build.

## Discovery authority order

Lane discovery uses these inputs:

1. `config/etf_discovery_universe.yml` — broad investable ETF universe and lane metadata
2. latest `output/pricing/price_audit_*.json` — holding closes, close data availability, pricing confidence, and top-challenger pricing after augmentation
3. `output/market_history/etf_relative_strength.json` — 1m/3m returns, trend quality, drawdown, volatility, and relative strength versus SPY when available
4. `output/etf_portfolio_state.json` — current holdings and portfolio gaps
5. latest prior `output/lane_reviews/etf_lane_assessment_*.json` — continuity, retained lanes, prior promotions

## Required discovery behavior

Each run must:

- evaluate all configured lanes
- represent every required breadth bucket
- include candidates outside current holdings where available
- include at least four challengers
- include at least two challengers outside the prior live radar where available
- include at least two challengers outside current held portfolio themes where available
- use historical relative-strength metrics when available
- use targeted challenger pricing where available
- promote 5 to 8 highest-ranked lanes to the live radar
- publish omitted-but-assessed lanes as proof of breadth without bloating the client report

## Two-pass challenger pricing rule

The production workflow should use this sequence:

```text
pricing pass for current holdings and known report inputs
→ historical relative-strength fetch
→ first-pass lane discovery
→ targeted pricing for top discovery challengers
→ final lane discovery using the augmented pricing audit
→ runtime state build
→ render/polish/linkify
→ validation
→ PDF/email delivery
```

Targeted challenger pricing is not allowed to weaken the existing holdings pricing gate. If challenger pricing fails, the report may still proceed as long as holdings pricing coverage remains valid; failed challengers must remain non-fundable or under review.

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

Historical relative-strength fields should include when available:

- return_1m_pct
- return_3m_pct
- trend_quality
- max_drawdown_3m_pct
- volatility_3m_pct
- rs_vs_spy_1m_pct
- rs_vs_spy_3m_pct
- relative_strength_score

## What this layer is not

It is not a replacement for the editorial report.
It is not a signal to automatically trade every promoted lane.
It is not allowed to fabricate price history or claim fresh evidence when the market-history fetch does not support it.
It is not allowed to treat a priced challenger as automatically superior; it only makes a fairer comparison possible.

## Current limitation

The historical relative-strength layer uses yfinance daily history as a pragmatic public-source history layer. Targeted challenger pricing extends the persisted pricing audit but is still constrained by available public sources and API rate limits.

Remaining limitations:

- no explicit liquidity screen yet
- no full sector/factor benchmark normalization yet
- no live fundamental/news ingestion yet
- challenger pricing is targeted, not full-universe pricing

## Next maturity step

Add:

- liquidity filters
- relative strength versus current holdings
- sector/factor benchmark normalization
- macro/fundamental freshness inputs
- a separate discovery/pricing manifest for challenger augmentation
