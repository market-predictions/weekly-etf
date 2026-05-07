# ETF Review OS — Current State

## Snapshot date
2026-05-07

## What this repository currently is

This repository is now a stable runtime-driven production-style weekly ETF review system with:

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

## Stable production baseline

The current baseline is now:

```text
pricing audit
→ lane discovery
→ runtime state
→ EN/NL report render
→ polish/linkify
→ validation
→ PDF/email delivery
```

This path has produced received bilingual reports and should be treated as the stable baseline before further renderer changes.

## What changed recently

### Runtime production path stabilized

The repo no longer depends on manually patched markdown as the hidden production source. The workflow now builds reports from state artifacts and validates them before delivery.

### Lane discovery engine implemented

The Structural Opportunity Radar now comes from:

- `config/etf_discovery_universe.yml`
- latest pricing audit
- portfolio state
- prior lane artifact
- novelty/challenger scoring

instead of only static memory.

### Report renderer caught up with discovery metadata

The runtime renderer now uses:

- `evidence_summary`
- `why_now`
- richer rejection reasons
- enriched current-position metadata
- recommendation scorecard fields

so the radar, omitted lanes, Section 10, Section 12, and Final Action Table are no longer analytically thin.

## Current strengths

- Runtime pipeline has successfully delivered bilingual reports.
- Pricing pass and validation run before render/send.
- Lane discovery runs before runtime state build.
- Lane artifact includes discovery provenance and novelty metadata.
- Breadth validation checks discovery metadata, not just static bucket coverage.
- Portfolio/radar reporting no longer needs manually patched markdown to pass.
- Section 7 and Section 15 are reconciled from the same runtime state.
- Dutch report is derived from the English runtime state and preserves numeric parity.
- Current-position review is enriched from portfolio state and recommendation scorecard.

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

### Priority A — add historical ETF relative-strength layer
Next enhancement:

- compute 1-month and 3-month returns
- compute trend quality
- compute drawdown/volatility filters
- compute relative strength versus SPY
- compute relative strength versus current holdings where possible
- feed those values into `runtime/score_etf_lanes.py`

### Priority B — implement two-pass challenger pricing
Future enhancement:

```text
first pass: broad lane discovery
→ identify top challengers
→ second pricing pass for top challengers
→ final scoring
→ report render
```

### Priority C — expand macro/fundamental freshness inputs
Future enhancement:

- machine-readable macro/regime input file
- policy/geopolitical catalyst tags
- official or market-based freshness notes

## Current status label

**ETF now has a stable runtime-driven bilingual production baseline. The next engineering phase is historical relative-strength scoring, followed by two-pass challenger pricing.**
