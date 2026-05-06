# ETF Review OS — Current State

## Snapshot date
2026-05-06

## What this repository currently is

This repository is a production-style weekly ETF review system with:

- `etf.txt` as the production masterprompt
- `control/CAPITAL_REUNDERWRITING_RULES.md` as the decision-framework addendum for model discipline
- `control/LANE_DISCOVERY_CONTRACT.md` as the discovery-layer contract
- `control/ETF_RUNTIME_STATE_CONTRACT.md` as the runtime state contract
- `config/etf_discovery_universe.yml` as the broad investable lane universe
- `runtime/discover_etf_lanes.py` and `runtime/score_etf_lanes.py` as the lane discovery/scoring engine
- `runtime/build_etf_report_state.py` as the deterministic runtime state builder
- `runtime/render_etf_report_from_state.py` as the English/Dutch runtime renderer
- `runtime/polish_runtime_reports.py` as the editorial polish layer
- `runtime/link_runtime_report_tickers.py` as the context-aware ticker link layer
- `etf-pro.txt` and `etf-pro-nl.txt` as premium English/Dutch delivery layers
- `send_report.py` as the delivery/rendering script
- `.github/workflows/send-weekly-report.yml` as the production send workflow
- a pricing subsystem in `pricing/`
- archived reports in `output/`
- pricing audits in `output/pricing/`
- lane artifacts in `output/lane_reviews/`
- explicit ETF state files:
  - `output/etf_portfolio_state.json`
  - `output/etf_valuation_history.csv`
  - `output/etf_trade_ledger.csv`
  - `output/etf_recommendation_scorecard.csv`

## What changed in this step

This update implements the first production lane discovery engine.

The key additions are:

- `control/LANE_DISCOVERY_CONTRACT.md`
- `config/etf_discovery_universe.yml`
- `runtime/discover_etf_lanes.py`
- `runtime/score_etf_lanes.py`
- workflow step: `Discover and score ETF opportunity lanes`
- stricter `validate_lane_breadth.py` discovery metadata validation

## Why this matters

The Structural Opportunity Radar had become structurally valid but too static. It proved that required buckets were present, but did not prove that a broad discovery process had run.

The new discovery layer moves the radar from:

- memory + fixed taxonomy + manually retained lane artifact

toward:

- broad ETF universe + pricing context + portfolio gaps + novelty/challenger scoring + machine-readable lane artifact

## Current strengths

- Runtime pipeline has successfully delivered bilingual reports.
- Pricing pass and validation run before render/send.
- Lane discovery now runs before runtime state build.
- Lane artifact now includes discovery provenance and novelty metadata.
- Breadth validation now checks discovery metadata, not just static bucket coverage.
- Portfolio/radar reporting no longer needs manually patched markdown to pass.

## Current weaknesses

### 1. Discovery is still config-driven, not fully market-history-driven
The discovery universe is now broad, but the first engine still uses configured priors and latest pricing availability. It does not yet compute true 1-month and 3-month relative strength rankings from historical ETF prices.

### 2. ETF universe is broader but still curated
`config/etf_discovery_universe.yml` is the first broad universe. It needs periodic expansion and review.

### 3. Challenger pricing coverage is limited by the current pricing pass
The discovery engine can score and rotate challengers, but not every challenger has fresh same-day pricing unless the pricing pass includes it.

### 4. Fundamental evidence is encoded, not fetched live
The first engine stores evidence summaries and why-now fields, but does not yet fetch current macro/fundamental news or official data automatically.

## Immediate priorities

### Priority A — run one live workflow after lane discovery merge
Confirm that:
- lane discovery writes a matching artifact
- runtime state uses the newly written artifact
- breadth validation passes with discovery metadata
- report is delivered

### Priority B — inspect radar freshness after the first discovery-driven run
Check whether promoted and omitted lanes change versus prior reports and whether the added challengers are useful, not filler.

### Priority C — add historical ETF relative-strength layer
Future enhancement:
- compute 1-month and 3-month returns
- compute trend quality
- compute volatility/drawdown filters
- feed those values into `runtime/score_etf_lanes.py`

### Priority D — expand challenger pricing coverage
Future enhancement:
- pricing pass should price top discovery challengers after lane discovery or use a two-pass workflow.

## Current status label

**ETF now has a deterministic lane discovery engine. The next live run should prove whether the Structural Opportunity Radar is no longer just static memory, while acknowledging that full market-history and live fundamental discovery remain future maturity steps.**
