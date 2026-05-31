# ETF Review OS — Current State

## Snapshot date
2026-05-31

## What this repository currently is

This repository is now a validated runtime-driven production-style weekly ETF review system with a new active pricing-lineage hardening track and an approved, shadow-first macro/thesis roadmap.

The existing runtime baseline can generate bilingual reports, show pricing-basis disclosure, and reconcile Section 7/Section 15 internally. However, the current pricing issue is not considered solved until `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md` is implemented and validated end to end.

The team has approved the Macro & Thesis Engine roadmap parked at `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md`, but this approval does **not** make the new macro/thesis engine production authority yet. The sequencing is locked as:

```text
pricing lineage first
→ macro audit foundation
→ deterministic regime and confidence engine
→ macro policy pack schema
→ compliance and methodology gates
→ thesis candidates in shadow mode
→ Stage-2 confirmation and valuation flags
→ client-surface integration only after validation
```

Current canonical components include:

- `etf.txt` as the production masterprompt
- `control/CAPITAL_REUNDERWRITING_RULES.md` as the decision-framework addendum for model discipline
- `control/LANE_DISCOVERY_CONTRACT.md` as the discovery-layer contract
- `control/ETF_RUNTIME_STATE_CONTRACT.md` as the runtime state contract
- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md` as the active pricing-lineage hardening contract
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md` as the central pricing-lineage regression/change log
- `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md` as the approved discussion roadmap for the future macro/thesis workstream, not yet an execution contract
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

The current proven baseline remains:

```text
pricing audit
→ historical relative strength
→ first-pass lane discovery
→ targeted challenger pricing
→ final lane discovery
→ runtime state
→ EN/NL markdown render
→ full valuation-history Section 7 equity curve
→ pricing-basis disclosure
→ polish/linkify
→ Dutch localization contract pass
→ equity-curve history validation
→ Dutch language quality validation
→ bilingual numeric parity validation
→ delivery HTML overrides
→ bilingual delivery HTML contract validation
→ PDF/email delivery
```

This path has solved recurring report-render defects where Section 2 ticker links, Current Position Review layout, Replacement Duel Table layout, Dutch terminology quality, bilingual numeric parity, price-basis visibility, and the Section 7 equity curve could not be made reliable through markdown post-processing alone.

## New active pricing-lineage decision

The latest debugging cycle showed that visible fresh closes and internal NAV reconciliation are not enough.

The active engineering direction remains `ETF_PRICING_LINEAGE_CONTRACT_V1`:

```text
requested_close_date + report_token
→ immutable pricing audit
→ explicit run manifest
→ runtime report state
→ English/Dutch report render
→ delivery assets
→ persisted portfolio state
→ persisted valuation history
```

Do not describe the fresh-closing-price issue as fully solved until the repo has:

- immutable audit identity
- exact audit path passed through runtime/report/delivery steps
- explicit `fresh_exact_close` versus `prior_valid_close` status semantics
- provider-symbol and provider-exchange lineage where available
- independent verification or explicit unverified status
- deterministic update of `output/etf_portfolio_state.json`
- deterministic update of `output/etf_valuation_history.csv`
- valuation-grade pricing for replacement-duel and fundable promoted challengers
- a hard `tools/validate_etf_pricing_lineage_contract.py` gate before delivery

## Approved macro/thesis roadmap decision

The team has approved the Macro & Thesis Engine roadmap as the next major model-quality track, but under strict sequencing:

1. Complete or confirm pricing-lineage proof first.
2. Build a provenance-backed macro audit foundation.
3. Replace hardcoded regime/confidence logic with deterministic classification and derived confidence.
4. Validate a complete macro policy pack schema.
5. Add compliance and methodology gates before any client-facing expansion.
6. Add WP-9 thesis candidates in shadow mode only.
7. Add Stage-2 market-confirmation and valuation/crowding flags.
8. Surface confirmed outputs in the client report only after shadow validation and language/compliance gates pass.

Authority rule:

> Macro/regime modernization is approved as a post-pricing-lineage enhancement. Until validated in fixtures and shadow runs, the new macro engine may produce internal artifacts but must not change client-facing fundable decisions.

Implementation implications:

- WP-1 to WP-4 may be built as internal artifacts first.
- WP-7 compliance gates are mandatory before expanded macro/thesis content reaches the English or Dutch client report.
- WP-9 Stage-1 thesis candidates are internal reasoning artifacts and must not appear as client-facing recommendations.
- A lane may become fundable only after thesis, market confirmation, valuation-grade pricing, and portfolio discipline gates all pass.
- Institutional overlay may cap confidence but may never set regime or portfolio action.
- Schema corrections are required before WP-9 implementation, especially `active_drivers` and difficult central-bank source coverage.

## Stable render decision

Strict branded sections are delivery-render responsibilities, not markdown-polish responsibilities.

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

The next pricing-lineage implementation must go further by persisting the current successful runtime NAV back into `output/etf_valuation_history.csv` and `output/etf_portfolio_state.json`.

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

Any future macro/thesis client-surface integration must extend this bilingual contract. New macro/thesis labels, driver language, candidate/fundable vocabulary, and compliance wording must be validated in both English and Dutch before delivery.

## What changed recently

### Macro/thesis roadmap approved and parked

Added:

- `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md`

The team reviewed and approved the roadmap. It is now recorded as the future model-quality track, with the explicit authority rule that it is shadow-first and must not displace pricing-lineage Priority A.

### Pricing-lineage contract created

A new control contract now defines how to solve the recurring fresh-pricing problem at the state/audit/run-manifest level rather than through another report-surface patch.

Added:

- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`

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
- Closing-price disclosure is now visible in the report.
- Dutch report is derived from the English runtime state and preserves numeric parity.
- Dutch localization now has a dedicated language-contract module and quality gate.
- Dutch strict-section delivery aliases are validated after render.
- Macro/thesis roadmap is now approved and parked as a phased, shadow-first model-quality track.

## Current weaknesses

### 1. ETF pricing lineage is not yet fully proven
The report can show fresh close rows, but the repo still needs immutable audit identity, explicit run manifest linkage, state persistence, exact/prior close semantics, independent verification, and a hard lineage validator.

### 2. ETF universe is broader but still curated
`config/etf_discovery_universe.yml` is the first broad universe. It needs periodic expansion and review.

### 3. Fundamental evidence is encoded, not fetched live
The first engine stores evidence summaries and why-now fields, but does not yet fetch current macro/fundamental news or official data automatically. The approved roadmap addresses this through a future macro audit foundation, but that foundation must be implemented in shadow mode first.

### 4. Relative strength is broad but not yet fully institutional
The relative-strength layer uses pragmatic public yfinance history. It includes early liquidity/tradability metrics, but does not yet include full factor/sector benchmark normalization or complete direct replacement-duel scoring.

### 5. Challenger pricing is targeted, not full-universe pricing
Targeted challenger pricing improves comparison quality, but it must now be formalized into valuation-grade pricing for replacement-duel/fundable challengers and research-grade pricing for broad discovery candidates.

### 6. Bilingual aliases are still distributed across several files
Dutch labels and aliases now work in production, but the alias definitions are still duplicated across `runtime/nl_localization.py`, `runtime/apply_nl_localization.py`, `send_report.py`, and `tools/validate_etf_delivery_html_contract.py`. This should be consolidated to reduce future validator drift.

### 7. Macro/thesis schema and compliance gates do not yet exist
The approved roadmap requires macro audit schema, macro policy pack schema corrections, active-driver vocabulary, thesis candidate artifacts, and compliance gates before any new macro/thesis content can become client-facing.

## Immediate priorities

### Priority A — implement ETF pricing lineage contract

Next engineering track:

- add immutable run id / audit identity
- write run manifest
- pass exact pricing audit/runtime/report paths through the workflow
- upgrade price row schema
- persist portfolio state and valuation history after successful pricing
- enforce valuation-grade pricing for replacement-duel and fundable challengers
- add `tools/validate_etf_pricing_lineage_contract.py`

### Priority B — keep macro/thesis roadmap shadow-first behind pricing lineage

Next architecture track after Phase 0:

- start from `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md`
- implement macro audit foundation as internal artifacts first
- keep WP-1 to WP-4 in fixture/shadow mode until validated
- do not let macro/thesis outputs change client-facing fundable decisions before compliance gates and replay tests pass
- update schema before WP-9, especially `active_drivers` and difficult central-bank coverage

### Priority C — consolidate bilingual alias handling

Next engineering cleanup after pricing lineage unless needed by macro/thesis client-surface work:

- keep Dutch terminology and aliases in one source of truth
- reuse that source from markdown localization, send-time parity checks, Dutch quality validation, and delivery HTML validation
- avoid future one-error-at-a-time phrase fixes

### Priority D — add direct challenger-vs-current-holding scoring

Next model enhancement:

- map challenger lanes to the holding they may replace
- compute direct 1m and 3m relative strength versus that holding
- feed direct replacement edge into lane scoring and replacement-duel notes

### Priority E — expand macro/fundamental freshness inputs through the approved roadmap

Future enhancement, not yet production authority:

- machine-readable macro audit input file
- deterministic regime and confidence engine
- policy/geopolitical catalyst tags
- official or market-based freshness notes where possible
- thesis candidates only as internal artifacts until Stage-2 confirmation gates pass

## Current status label

**ETF has a production-tested runtime-driven bilingual baseline with visible pricing-basis disclosure and Section 7/Section 15 reconciliation, plus an approved shadow-first macro/thesis roadmap. The fresh-pricing issue is still not fully closed until `ETF_PRICING_LINEAGE_CONTRACT_V1` is implemented with immutable audit identity, explicit run manifest linkage, state persistence, exact close-date semantics, challenger pricing tiers, and a hard pricing-lineage validator. Macro/thesis modernization may begin only under the approved phased roadmap and must not influence client-facing fundable decisions until fixture, shadow, compliance, and bilingual gates pass.**
