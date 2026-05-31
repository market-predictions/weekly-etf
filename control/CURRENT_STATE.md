# ETF Review OS — Current State

## Snapshot date
2026-05-31

## What this repository currently is

`market-predictions/weekly-etf` is now a runtime-driven production-style weekly ETF review system with:

- explicit pricing audits in `output/pricing/`
- explicit run manifests in `output/run_manifests/`
- runtime report-state artifacts in `output/runtime/`
- persisted portfolio state and valuation history
- English canonical and Dutch companion report generation
- delivery HTML overrides for strict branded sections
- a hard pricing-lineage validator before send
- an approved, shadow-first macro/thesis roadmap

The pricing-lineage hardening cycle has moved from active repair to **closed baseline / active regression guard** after the confirmation run:

```text
run_id: 20260531_200843
requested_close_date: 2026-05-29
pricing_lineage_status: passed
workflow_conclusion: success
english_report_path: output/weekly_analysis_pro_260529_22.md
dutch_report_path: output/weekly_analysis_pro_nl_260529_22.md
runtime_state_path: output/runtime/etf_report_state_20260529_20260531_200843.json
pricing_audit_path: output/pricing/price_audit_2026-05-29_20260531_200843.json
total_portfolio_value_eur: 109964.97
```

Do **not** claim independent email delivery success from this status alone. The run produced report/PDF artifacts and a successful workflow conclusion, but `delivery_manifest_path` was `null` in the manifest. Delivery success still requires a delivery receipt/manifest or explicit user confirmation.

## Four-layer operating status

### 1. Decision framework

The current decision framework remains:

- capital re-underwriting discipline from `control/CAPITAL_REUNDERWRITING_RULES.md`
- broad lane discovery from `control/LANE_DISCOVERY_CONTRACT.md`
- valuation-grade challenger discipline
- no indefinite `Hold but replaceable` inertia
- macro/thesis modernization approved only as a future phased enhancement

### 2. Input/state contract

Current authoritative state inputs are:

- `output/pricing/price_audit_<requested_close_date>_<run_id>.json`
- `output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json`
- `output/runtime/etf_report_state_<report_token>_<run_id>.json`
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `output/etf_trade_ledger.csv`
- `output/etf_recommendation_scorecard.csv`
- `output/lane_reviews/etf_lane_assessment_<report_token>.json`
- `output/market_history/etf_relative_strength.json`
- `output/macro/latest.json`

The latest confirmed run proves the chain:

```text
pricing audit
→ runtime state
→ EN/NL report artifacts
→ persisted portfolio state
→ valuation history
→ run manifest
→ pricing-lineage validator
```

### 3. Output contract

The report output contract remains:

- English is canonical.
- Dutch is a companion render from the same runtime state, not a separate research pass.
- Section 7 equity curve and Section 15 holdings reconcile to the same runtime NAV.
- Pricing-basis disclosure must show requested close, close date used, source, status, and close used.
- Strict branded sections are rendered from runtime state at delivery HTML level, not fixed through markdown-only patches.
- Client-facing reports must not leak internal plumbing labels.

### 4. Operational runbook

The current production path is:

```text
run-queue request or manual dispatch
→ resolve run identity
→ persistent ETF pricing pass
→ historical relative-strength fetch, with cached fallback if public history is unavailable
→ macro policy pack build, with Phase 2 macro audit shadow-only / non-blocking
→ first-pass lane discovery
→ challenger pricing augmentation
→ final lane discovery
→ challenger fundability validation
→ portfolio rotation plan
→ runtime report state
→ EN/NL markdown reports
→ pricing-basis disclosure
→ report polish / localization / ticker links
→ model execution shadow artifact
→ run manifest
→ persisted valuation state
→ equity-curve validation
→ Dutch quality validation
→ delivery HTML validation
→ hard pricing-lineage pre-send gate
→ PDF/email delivery workflow step
→ final manifest update
```

## Pricing-lineage closure status

The pricing-lineage contract is now implemented as an active regression guard.

Current evidence:

- `tools/validate_etf_pricing_lineage_contract.py` validates manifest → pricing audit → runtime state → report tables → recalculated NAV → persisted portfolio state → valuation history → fundable challenger pricing.
- `tools/validate_etf_client_surface_clean.py` calls the pricing-lineage validator before send and writes `pricing_lineage_status=passed` into the manifest when validation succeeds.
- The latest successful run manifest records `pricing_lineage_status: passed` for run `20260531_200843`.
- The same manifest records `workflow_conclusion: success`.
- The validator confirmed holdings: GLD, GSG, PAVE, PPA, SMH, SPY, URNM.
- Pricing coverage was 100%, with 7 fresh holdings, 0 carried-forward holdings, and no unresolved tickers.

Remaining pricing-related improvement, not a blocker:

- independent cross-provider verification could upgrade some rows from `fresh_exact_unverified` to `fresh_exact_close` when multiple sources agree.

## Macro/thesis roadmap status

The Macro & Thesis Engine roadmap is approved but remains **shadow-first**.

Locked sequence:

```text
pricing lineage baseline confirmed
→ macro audit foundation
→ deterministic regime and confidence engine
→ macro policy pack schema
→ compliance and methodology gates
→ thesis candidates in shadow mode
→ Stage-2 confirmation and valuation flags
→ client-surface integration only after validation
```

Authority rule:

> Macro/regime modernization is approved as a post-pricing-lineage enhancement. Until validated in fixtures and shadow runs, the new macro engine may produce internal artifacts but must not change client-facing fundable decisions.

Current macro status:

- Phase 2 macro audit foundation exists, but remains shadow-only.
- `runtime/build_macro_policy_pack.py` records macro audit availability as metadata only.
- Macro audit unavailability is non-blocking while the layer has no production authority.
- Existing regime logic still uses the legacy macro policy pack path.
- Deterministic regime/confidence, schema correction, methodology, compliance, and WP-9 thesis candidates are not production authority yet.

## Current strengths

- Pricing retrieval and report reconciliation are validated at artifact level.
- Hard pricing-lineage validation is now implemented and passed in a fresh run.
- Runtime pipeline produces bilingual report artifacts from the same state.
- Section 7 and Section 15 reconcile to the runtime NAV.
- Portfolio state and valuation history are persisted after successful valuation.
- Challenger pricing/fundability discipline is active.
- Relative-strength refresh is more robust because cached fallback is explicit and marked.
- Shadow macro audit no longer blocks production report delivery while it remains non-authoritative.
- Dutch report generation remains governed by language-contract and quality checks.
- Macro/thesis roadmap is approved and sequenced behind the now-confirmed pricing-lineage baseline.

## Current weaknesses / watch items

### 1. Email delivery evidence is still separate from workflow success

A successful workflow and generated PDF artifacts are not the same as a delivery receipt. Do not claim delivery unless a delivery manifest/receipt exists or the user confirms receipt.

### 2. Independent price verification is not yet upgraded

Rows can remain `fresh_exact_unverified` when one provider gives exact requested-date closes but no independent cross-provider verification has been recorded.

### 3. Macro/thesis schema and compliance gates do not yet exist

The approved roadmap still requires macro policy pack schema correction, active-driver vocabulary, thesis candidate artifacts, methodology, and compliance gates before expanded macro/thesis content can become client-facing.

### 4. Dutch aliases are still distributed across several files

Dutch terminology and validator aliases work, but they remain spread across localization, send-time parity, and delivery validation layers. Consolidation remains useful.

### 5. Direct challenger-vs-current-holding scoring is still a model enhancement

The system has challenger pricing and broad relative strength, but direct 1m/3m replacement-edge scoring versus each current holding remains a future improvement.

## Immediate priorities

### Priority A — move into macro/thesis roadmap Phase 2/3 carefully

Next architecture track:

- keep Phase 2 macro audit as shadow-only
- add fixture replay discipline
- define the full macro policy pack schema
- design deterministic regime/confidence classification without changing production decisions yet

### Priority B — preserve pricing-lineage regression guard

Going forward:

- do not weaken `tools/validate_etf_pricing_lineage_contract.py`
- keep manifest → audit → runtime → reports → persisted state validation before send
- keep state and valuation history updates deterministic
- keep challenger fundability tied to valuation-grade pricing

### Priority C — consolidate Dutch language/alias handling

Next cleanup after pricing-lineage closure:

- keep Dutch terminology and aliases in one source of truth
- reuse that source from markdown localization, send-time parity checks, Dutch quality validation, and delivery HTML validation

### Priority D — add direct challenger-vs-current-holding scoring

Next model enhancement:

- map challenger lanes to the holding they may replace
- compute direct 1m and 3m relative strength versus that holding
- feed direct replacement edge into lane scoring and replacement-duel notes

## Current status label

**ETF has a production-tested runtime-driven bilingual baseline with pricing-lineage proof now passed for run `20260531_200843`. Pricing lineage is closed as a baseline and remains an active regression guard. The next major roadmap is macro/regime/thesis modernization, but only through the approved shadow-first sequence and without client-facing decision impact until fixture, schema, compliance, and bilingual gates pass.**
