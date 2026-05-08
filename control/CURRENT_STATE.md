# ETF Review OS — Current State

## Snapshot date
2026-05-08

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
- `runtime/render_etf_report_from_state.py` as the English/Dutch runtime markdown renderer
- `runtime/polish_runtime_reports.py` as the editorial polish layer
- `runtime/link_runtime_report_tickers.py` as the context-aware markdown ticker link layer
- `runtime/delivery_html_overrides.py` as the delivery-layer HTML authority for strict branded sections
- `tools/validate_etf_delivery_html_contract.py` as the dynamic delivery HTML regression validator
- `send_report_runtime_html.py` as the production delivery entrypoint that applies runtime-state HTML overrides
- `send_report.py` as the base delivery/rendering script
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
→ EN/NL markdown render
→ polish/linkify
→ delivery HTML overrides
→ delivery HTML contract validation
→ PDF/email delivery
```

This path has solved the recurring report-render defect where Section 2 ticker links and Current Position Review layout could not be made reliable through markdown post-processing.

## Stable render decision

Strict branded sections are now delivery-render responsibilities, not markdown-polish responsibilities.

Specifically:

- Portfolio Action Snapshot is rendered from runtime state as delivery HTML.
- Current Position Review is rendered from runtime state as delivery HTML.
- The delivery HTML validator dynamically reads current holdings from runtime state.
- The validator checks real TradingView anchors and a real Current Position Review HTML table before email send.

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

### Delivery HTML layer added for strict sections

The recurring Section 2 and Current Position Review rendering issues were resolved by moving those sections into the delivery HTML layer. The validator now fails the workflow before email send if those sections lose anchors or table structure.

## Current strengths

- Runtime pipeline has successfully delivered bilingual reports.
- Pricing pass and validation run before render/send.
- Historical relative-strength fetch runs before discovery.
- First-pass discovery identifies top challengers.
- Targeted challenger pricing augments the pricing audit.
- Final discovery uses the augmented pricing audit.
- Lane artifact includes discovery provenance, novelty metadata, and market-strength fields.
- Delivery HTML overrides protect strict branded sections.
- Delivery HTML validator checks the rendered output contract before email send.
- Section 7 and Section 15 are reconciled from the same runtime state.
- Dutch report is derived from the English runtime state and preserves numeric parity.

## Current weaknesses

### 1. ETF universe is broader but still curated
`config/etf_discovery_universe.yml` is the first broad universe. It needs periodic expansion and review.

### 2. Fundamental evidence is encoded, not fetched live
The first engine stores evidence summaries and why-now fields, but does not yet fetch current macro/fundamental news or official data automatically.

### 3. Relative strength is broad but not yet fully institutional
The relative-strength layer uses pragmatic public yfinance history. It includes early liquidity/tradability metrics, but does not yet include full factor/sector benchmark normalization or complete direct replacement-duel scoring.

### 4. Challenger pricing is targeted, not full-universe pricing
Targeted challenger pricing improves comparison quality, but it intentionally does not price the whole ETF universe to protect runtime and API limits.

## Immediate priorities

### Priority A — final confirmation run
Run one fresh production workflow to confirm:

- delivery HTML validator passes
- PDF/email render still succeeds
- received PDF keeps Section 2 links and Current Position Review table intact

### Priority B — add direct challenger-vs-current-holding scoring
Next enhancement:

- map challenger lanes to the holding they may replace
- compute direct 1m and 3m relative strength versus that holding
- feed direct replacement edge into lane scoring and replacement-duel notes

### Priority C — expand macro/fundamental freshness inputs
Future enhancement:

- machine-readable macro/regime input file
- policy/geopolitical catalyst tags
- official or market-based freshness notes

## Current status label

**ETF now has a validated runtime-driven bilingual production baseline with historical relative-strength scoring, two-pass challenger pricing, and delivery HTML validation for strict branded sections. The next engineering phase is direct challenger-vs-current-holding scoring.**
