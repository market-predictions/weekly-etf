# ETF Review OS — Current State

## Snapshot date
2026-05-11

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
- `runtime/nl_localization.py` as the Dutch language-contract module
- `runtime/apply_nl_localization.py` as the Dutch companion localization pass
- `tools/validate_etf_dutch_language_quality.py` as the Dutch markdown quality gate
- `tools/validate_etf_equity_curve_history.py` as the equity-curve history regression guard
- `runtime/polish_runtime_reports.py` as the editorial polish layer
- `runtime/link_runtime_report_tickers.py` as the context-aware markdown ticker link layer
- `runtime/delivery_html_overrides.py` as the delivery-layer HTML authority for strict branded sections
- `tools/validate_etf_delivery_html_contract.py` as the dynamic bilingual delivery HTML regression validator
- `send_report_runtime_html.py` as the production delivery entrypoint that applies runtime-state HTML overrides
- `send_report.py` as the base delivery/rendering script and bilingual parity validator
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
→ full valuation-history Section 7 equity curve
→ polish/linkify
→ Dutch localization contract pass
→ equity-curve history validation
→ Dutch language quality validation
→ bilingual numeric parity validation
→ delivery HTML overrides
→ bilingual delivery HTML contract validation
→ PDF/email delivery
```

This path has solved the recurring report-render defects where Section 2 ticker links, Current Position Review layout, Replacement Duel Table layout, Dutch terminology quality, bilingual numeric parity, and the Section 7 equity curve could not be made reliable through markdown post-processing alone.

## Stable render decision

Strict branded sections are now delivery-render responsibilities, not markdown-polish responsibilities.

Specifically:

- Portfolio Action Snapshot is rendered from runtime state as delivery HTML.
- Current Position Review is rendered from runtime state as delivery HTML.
- Replacement Duel Table / Vervangingsanalyse is rendered from runtime state as delivery HTML.
- The delivery HTML validator dynamically reads current holdings from runtime state.
- The validator checks real TradingView anchors and real HTML tables before email send.
- Dutch localized strict-section aliases are accepted by the delivery HTML contract.

## Stable equity-curve decision

Section 7 is now a state/history render, not a hardcoded start/latest summary.

Specifically:

- `output/etf_valuation_history.csv` is the source for historical NAV points.
- `runtime/render_etf_report_from_state.py` appends or replaces the current runtime NAV for the report date.
- Section 7 renders the full valuation history table.
- The embedded equity-curve chart is generated from the Section 7 table, so it now shows the intermediate valuation dates.
- `tools/validate_etf_equity_curve_history.py` protects the contract with the marker `ETF_EQUITY_CURVE_HISTORY_OK`.
- The validator fails if Section 7 has too few points, has duplicate dates, or if the latest Section 7 NAV does not reconcile with Section 15 total NAV.

## Stable bilingual decision

The Dutch report is a companion language render of the English canonical report, not a separate research pass.

Specifically:

- English remains the canonical analytical report.
- Dutch uses the same runtime state, prices, portfolio totals, holdings, equity-curve values, and recommendation logic.
- `runtime/nl_localization.py` is the central Dutch language-contract source for labels, status phrases, decision strings, trigger phrases, disclaimer text, and allowed English financial terms.
- `runtime/apply_nl_localization.py` applies the Dutch language contract to the markdown companion.
- `tools/validate_etf_dutch_language_quality.py` blocks hard English client-facing leaks and internal source labels.
- `send_report.py` validates bilingual numeric parity before render/send.
- `tools/validate_etf_delivery_html_contract.py` validates both English and Dutch rendered delivery HTML.

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

### Dutch companion localization production-tested

A fresh production run successfully generated and delivered English and Dutch reports after adding the Dutch language-contract layer, Dutch quality gate, bilingual numeric parity fixes, and Dutch aliases for delivery HTML validators.

The important lesson from this debugging cycle is that bilingual localization must be handled as a contract across render, markdown validation, delivery HTML validation, and send-time parity checks. One-off phrase fixes are fragile.

### Equity curve regression fixed and production-tested

A fresh corrected report confirmed that Section 7 now uses the full `output/etf_valuation_history.csv` history plus the current runtime NAV. The embedded equity-curve chart now shows the intermediate valuation dates instead of only the start and latest points.

The workflow is protected by `ETF_EQUITY_CURVE_HISTORY_OK`.

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
- Section 7 now renders full valuation history from `output/etf_valuation_history.csv` plus current runtime NAV.
- Section 7 and Section 15 are reconciled from the same runtime state and protected by `ETF_EQUITY_CURVE_HISTORY_OK`.
- Dutch report is derived from the English runtime state and preserves numeric parity.
- Dutch localization now has a dedicated language-contract module and quality gate.
- Dutch strict-section delivery aliases are validated after render.

## Current weaknesses

### 1. ETF universe is broader but still curated
`config/etf_discovery_universe.yml` is the first broad universe. It needs periodic expansion and review.

### 2. Fundamental evidence is encoded, not fetched live
The first engine stores evidence summaries and why-now fields, but does not yet fetch current macro/fundamental news or official data automatically.

### 3. Relative strength is broad but not yet fully institutional
The relative-strength layer uses pragmatic public yfinance history. It includes early liquidity/tradability metrics, but does not yet include full factor/sector benchmark normalization or complete direct replacement-duel scoring.

### 4. Challenger pricing is targeted, not full-universe pricing
Targeted challenger pricing improves comparison quality, but it intentionally does not price the whole ETF universe to protect runtime and API limits.

### 5. Bilingual aliases are still distributed across several files
Dutch labels and aliases now work in production, but the alias definitions are still duplicated across `runtime/nl_localization.py`, `runtime/apply_nl_localization.py`, `send_report.py`, and `tools/validate_etf_delivery_html_contract.py`. This should be consolidated to reduce future validator drift.

## Immediate priorities

### Priority A — consolidate bilingual alias handling
Next engineering cleanup:

- keep Dutch terminology and aliases in one source of truth
- reuse that source from markdown localization, send-time parity checks, Dutch quality validation, and delivery HTML validation
- avoid future one-error-at-a-time phrase fixes

### Priority B — add direct challenger-vs-current-holding scoring
Next model enhancement:

- map challenger lanes to the holding they may replace
- compute direct 1m and 3m relative strength versus that holding
- feed direct replacement edge into lane scoring and replacement-duel notes

### Priority C — expand macro/fundamental freshness inputs
Future enhancement:

- machine-readable macro/regime input file
- policy/geopolitical catalyst tags
- official or market-based freshness notes

## Current status label

**ETF now has a production-tested runtime-driven bilingual baseline with historical relative-strength scoring, two-pass challenger pricing, Dutch language-contract validation, full valuation-history equity curve rendering, bilingual numeric parity, delivery HTML validation for strict branded sections, and confirmed English/Dutch email delivery. The next engineering cleanup is consolidating bilingual alias handling; the next model phase remains direct challenger-vs-current-holding scoring.**
