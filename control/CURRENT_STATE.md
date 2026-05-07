# ETF Review OS — Current State

## Snapshot date
2026-05-07

## What this repository currently is

This repository is now a validated runtime-driven production-style weekly ETF review system with:

- `etf.txt` as the production masterprompt
- `control/CAPITAL_REUNDERWRITING_RULES.md` as the decision-framework addendum for model discipline
- `control/LANE_DISCOVERY_CONTRACT.md` as the discovery-layer contract
- `control/ETF_RUNTIME_STATE_CONTRACT.md` as the runtime state contract
- `config/etf_discovery_universe.yml` as the broad investable lane universe
- `runtime/fetch_etf_relative_strength.py` as the historical relative-strength input layer
- `runtime/discover_etf_lanes.py` and `runtime/score_etf_lanes.py` as the lane discovery/scoring engine
- `pricing/augment_challenger_pricing.py` as the targeted second-pass challenger pricing layer
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
- relative-strength metrics in `output/market_history/`
- lane artifacts in `output/lane_reviews/`
- explicit ETF state files:
  - `output/etf_portfolio_state.json`
  - `output/etf_valuation_history.csv`
  - `output/etf_trade_ledger.csv`
  - `output/etf_recommendation_scorecard.csv`

## Stable production baseline

The current proven baseline is now:

```text
pricing audit
→ historical relative strength
→ first-pass lane discovery
→ targeted challenger pricing
→ final lane discovery
→ runtime state
→ EN/NL report render
→ polish/linkify
→ validation
→ PDF/email delivery
```

This path has produced a green workflow run and received bilingual reports. Treat this as the current production baseline before further changes.

## What changed recently

### Runtime production path stabilized

The repo no longer depends on manually patched markdown as the hidden production source. The workflow builds reports from state artifacts and validates them before delivery.

### Lane discovery engine implemented and upgraded

The Structural Opportunity Radar now comes from:

- `config/etf_discovery_universe.yml`
- latest pricing audit
- historical relative-strength metrics
- portfolio state
- prior lane artifact
- novelty/challenger scoring
- targeted challenger pricing where available

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
- Historical relative-strength fetch runs before discovery.
- First-pass discovery identifies top challengers.
- Targeted challenger pricing augments the pricing audit.
- Final discovery uses the augmented pricing audit.
- Lane artifact includes discovery provenance, novelty metadata, and market-strength fields.
- Breadth validation checks discovery metadata, not just static bucket coverage.
- Portfolio/radar reporting no longer needs manually patched markdown to pass.
- Section 7 and Section 15 are reconciled from the same runtime state.
- Dutch report is derived from the English runtime state and preserves numeric parity.
- Current-position review is enriched from portfolio state and recommendation scorecard.

## Current weaknesses

### 1. ETF universe is broader but still curated
`config/etf_discovery_universe.yml` is the first broad universe. It needs periodic expansion and review.

### 2. Fundamental evidence is encoded, not fetched live
The first engine stores evidence summaries and why-now fields, but does not yet fetch current macro/fundamental news or official data automatically.

### 3. Relative strength is broad but not yet fully institutional
The relative-strength layer uses pragmatic public yfinance history. It does not yet include liquidity filters, factor/sector benchmark normalization, or relative strength versus every current holding.

### 4. Challenger pricing is targeted, not full-universe pricing
Targeted challenger pricing improves comparison quality, but it intentionally does not price the whole ETF universe to protect runtime and API limits.

## Immediate priorities

### Priority A — inspect the latest received report after two-pass challenger pricing
Check whether:

- replacement challenger pricing is visible and sensible
- final radar ranking changed logically after challenger pricing
- omitted lanes have useful rejection reasons
- no report formatting regression occurred

### Priority B — add liquidity and tradability filters
Next enhancement:

- average dollar volume filter
- ETF AUM / spread proxy if available
- avoid promoting technically attractive but illiquid ETFs

### Priority C — add relative strength versus current holdings
Future enhancement:

- compare challengers directly versus SPY, SMH, PPA, PAVE, URNM, and GLD where relevant
- use this in replacement-duel scoring

### Priority D — expand macro/fundamental freshness inputs
Future enhancement:

- machine-readable macro/regime input file
- policy/geopolitical catalyst tags
- official or market-based freshness notes

## Current status label

**ETF now has a validated runtime-driven bilingual production baseline with historical relative-strength scoring and two-pass challenger pricing. The next engineering phase is liquidity/tradability filtering and richer macro/fundamental freshness inputs.**
