# Weekly ETF Roadmap — Macro & Thesis Engine Work Packages

**Repository:** `market-predictions/weekly-etf`  
**Scope:** Weekly ETF report, not Weekly ETF EU  
**Prepared for:** Team discussion / go-no-go review  
**Date:** 2026-05-31  
**Status:** Proposed conditional roadmap, not yet a repo authority file

---

## 1. Executive recommendation

**Recommendation: Conditional GO.**

The uploaded macro/regime and thesis-selection work packages are directionally valid and implementable, but they should **not** be implemented as one large production change.

The safe roadmap is:

```text
Pricing lineage first
→ macro engine second
→ thesis pipeline third
→ client-surface integration last
```

The work packages are a real upgrade path from a macro-flavored ETF report toward a more systematic, regime-aware ETF decision engine. However, the current `weekly-etf` repo still has an active pricing-lineage hardening track. The macro and thesis work should therefore be sequenced behind, or at minimum gated by, pricing-lineage validation.

---

## 2. First-principles reasoning

A trustworthy weekly ETF report needs four foundations:

1. **Traceable current values**  
   Pricing, NAV, Section 7 equity curve, Section 15 holdings, persisted portfolio state, valuation history, and run manifest must all derive from the same immutable pricing audit.

2. **Evidence-derived macro state**  
   Regime labels, confidence values, central-bank stance, and macro signals must be computed from observable inputs, not static prose or hardcoded confidence numbers.

3. **Separation between thesis and action**  
   A macro thesis may identify a candidate lane, but it must not become a funded ETF decision unless market confirmation, valuation-grade pricing, and portfolio discipline gates also pass.

4. **Restrained client output**  
   The internal pack can be rich. The client report should surface only decision-relevant conclusions, with clear evidence and no internal plumbing language.

The uploaded work packages mostly respect these principles. The strongest architectural choices are:

- deterministic Python-only computation
- no LLM in the numerical/regime computation path
- provenance for every macro value
- stale/unavailable fields instead of silent fallback
- derived confidence rather than hardcoded confidence
- curated institutional overlay instead of live scraped bank research
- Stage-1 thesis candidates kept separate from Stage-2 fundable outputs
- compliance gate before client-facing use

---

## 3. Current issue

The current `weekly-etf` repo has a production-tested runtime-driven bilingual report baseline, but the control layer still identifies pricing lineage as the active hardening priority.

The existing macro pack is useful but still limited:

- regime classification still leans on ETF return proxies
- confidence values are hardcoded
- central-bank language is partly static
- macro/fundamental evidence is encoded rather than fetched from authoritative live sources
- lane discovery already consumes `output/macro/latest.json`, so macro changes can influence lane scoring and portfolio decisions

This means the macro WPs are relevant, but also risky if they are connected too quickly to production scoring.

---

## 4. Root cause

The report has evolved from a prompt/report artifact into a runtime-driven decision system. The architecture now has multiple layers:

1. decision framework
2. input/state contract
3. output contract
4. operational runbook

The uploaded work packages are strong because they continue that direction. The risk is that they introduce too many changes across all four layers at once.

A single mega-change would touch:

- data fetching
- schema
- regime classification
- confidence scoring
- lane scoring
- challenger fundability
- report wording
- Dutch localization
- compliance validation
- CI workflow ordering

That would recreate the same patch-cycle problem the repo has been trying to escape.

---

## 5. WP-by-WP verdict

| Work package | Verdict | Reason |
|---|---:|---|
| **WP-1 — Macro data fetch layer** | **Go, with constraints** | Valid and needed. Replace proxy-only macro input with authoritative, provenance-backed series. Must be run-scoped and fail loud. |
| **WP-2 — Regime classification model** | **Go** | Strong upgrade. Thresholds belong in versioned config, not code. Preserve existing regime memory. |
| **WP-3 — Derived confidence score** | **Go** | Required. Hardcoded confidence values should be removed from the regime path. |
| **WP-4 — Complete pack schema** | **Go, staged** | Needed, but must preserve compatibility with lane discovery until the full pipeline validates. |
| **WP-5 — Institutional consensus overlay** | **Go, defer until engine stable** | Valid only as curated, cited, paraphrased, and non-authoritative. Overlay may cap confidence, never set regime or actions. |
| **WP-6 — Published methodology document** | **Go early as internal draft** | Useful trust and compliance asset. Publish externally only after behavior is stable. |
| **WP-7 — Compliance and language gate** | **Mandatory before client surfacing** | Must block predictive phrasing, uncited overlay entries, orphan macro claims, and Stage-1 candidate leakage. |
| **WP-8 — CI wiring and regression fixtures** | **Go** | Essential. Fixture replay is required before production influence. |
| **WP-9 — Thesis layer and sector-selection pipeline** | **Go, after WP-1 to WP-4** | Valuable but highest compliance-risk layer. Stage 1 must remain internal; Stage 2 can influence decisions only after confirmation gates pass. |

---

## 6. What to discard or change

### 6.1 Discard one-shot implementation

Do not implement all WPs in one PR or one engineering sprint. This should be a phased architecture track.

**Decision:** split into gated phases with fixture validation and shadow comparisons.

### 6.2 Discard live scraping of institutional research

Institutional consensus should be curated, cited, and paraphrased. Live pulling bank research creates copyright, reliability, and compliance risk.

**Decision:** keep WP-5 curated only.

### 6.3 Discard client-facing Stage-1 candidates

Stage-1 thesis candidates are internal reasoning artifacts. They should never appear in the client report as suggestions, tips, or actions.

**Decision:** client-facing output may only show post-confirmation decisions using the existing report vocabulary.

### 6.4 Change schema before WP-9 implementation

The uploaded schema is strong but needs adjustment before WP-9:

- add `active_drivers`
- add driver provenance rules
- ensure central-bank coverage matches real available sources
- define how PBoC or other difficult central-bank data is handled if no clean free source exists

**Decision:** schema correction is a prerequisite.

### 6.5 Keep valuation/crowding as a caution flag

Valuation/crowding checks are useful, but ETF valuation proxies can be noisy. A hard block would create false precision.

**Decision:** valuation/crowding should flag risk, not automatically block funding.

---

## 7. Proposed roadmap

### Phase 0 — Freeze authority and sequencing

Update the repo control layer before implementation.

**Files to update:**

- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`

**Stable decision to record:**

> Macro/regime modernization is approved as a post-pricing-lineage enhancement. Until validated in fixtures and shadow runs, the new macro engine may produce internal artifacts but must not change client-facing fundable decisions.

**Done when:**

- team agrees on sequencing
- pricing-lineage remains Priority A
- macro engine is explicitly marked as shadow-only until validated

---

### Phase 1 — Finish or confirm pricing-lineage baseline

Do not let macro work jump ahead of the pricing-lineage contract.

**Goal:**

Make sure one report can be traced from:

```text
requested_close_date + run_id
→ immutable pricing audit
→ run manifest
→ runtime state
→ English/Dutch reports
→ persisted portfolio state
→ valuation history
→ delivery artifacts
```

**Done when:**

- pricing audit is immutable and run-scoped
- manifest links the exact audit, runtime state, reports, portfolio state, and valuation history
- pricing-lineage validator passes before delivery
- valuation-grade pricing rules are enforced for holdings and fundable challengers

---

### Phase 2 — Macro audit foundation

Implement WP-1 in a run-scoped way.

**New / changed files:**

- `macro_sources/fred_client.py`
- `macro_sources/ecb_client.py`
- `macro_sources/treasury_client.py`
- `macro_sources/vol_client.py`
- `macro_sources/cb_calendar.py`
- `schemas/macro_data_audit.schema.json`
- `output/macro/macro_data_audit_YYYY-MM-DD_<run_id>.json`
- `config/cb_calendar.yml` if official calendar API coverage is insufficient

**Rules:**

- every value has provenance
- every value has `source`, `series_id`, `as_of_date`, `fetched_at_utc`, and `staleness_days`
- stale or unavailable data is flagged, not guessed
- no API secrets appear in logs or output
- fixture mode must work with no network

**Done when:**

- macro audit can be generated from live data
- macro audit can be replayed from fixtures
- no downstream report behavior changes yet

---

### Phase 3 — Deterministic regime engine

Implement WP-2 and WP-3.

**New / changed files:**

- `macro_regime/classify.py`
- `macro_regime/confidence.py`
- `config/regime_thresholds.yml`
- `runtime/regime_memory.py` only if extension is needed

**Rules:**

- no magic numbers in classifier code
- thresholds live in config
- confidence is computed from cross-axis agreement
- confidence ships with decomposition text
- regime memory is preserved and extended, not replaced

**Done when:**

- same fixture input produces identical regime and confidence across runs
- all-axes-agree fixture scores higher than half-divergent fixture
- old regime-memory transition behavior is preserved unless deliberately changed

---

### Phase 4 — Macro policy pack schema and compatibility layer

Implement WP-4.

**New / changed files:**

- `schemas/macro_policy_pack.schema.json`
- `runtime/build_macro_policy_pack.py`
- `output/macro/latest.json`
- `output/macro/etf_macro_policy_pack_YYYYMMDD_<run_id>.json`

**Rules:**

- pack validates against schema
- `latest.json` and dated pack are byte-identical for the same run, if that remains the chosen contract
- lane discovery remains compatible
- `lane_adjustments` remains available
- central-bank stance is computed, not static prose

**Done when:**

- macro pack builds from macro audit
- old lane discovery still runs
- new fields are available but not yet allowed to cause production decision drift

---

### Phase 5 — Compliance and methodology

Implement WP-6 and WP-7 before any client-facing macro/thesis expansion.

**New / changed files:**

- `MACRO_METHODOLOGY.md`
- `tools/validate_macro_compliance.py`
- Dutch language validator extensions if macro/thesis wording reaches Dutch report

**Rules:**

- no predictive language about market levels or central-bank actions
- overlay entries must be cited and paraphrased
- candidate-stage content must not appear in client reports
- every client-surfaced macro figure must resolve to provenance
- methodology must say the model is descriptive, not predictive

**Done when:**

- planted forecast sentences fail validation
- planted uncited overlay entry fails validation
- planted macro figure without provenance fails validation
- Dutch report validator catches macro/thesis wording leaks where applicable

---

### Phase 6 — WP-9 thesis layer in shadow mode

Implement WP-9.1 and WP-9.2, but keep output internal.

**New files:**

- `config/driver_catalog.yml`
- `config/driver_beneficiary_map.yml`
- `runtime/build_thesis_candidates.py`
- `output/macro/thesis_candidates_YYYY-MM-DD_<run_id>.json`

**Rules:**

- driver IDs are closed and versioned
- driver activation is derived from macro axes
- driver-to-beneficiary links are hand-curated and versioned
- every candidate names its contributing drivers and rationale
- no LLM in the production build path
- breadth guard warns if candidates merely rationalize current holdings

**Done when:**

- same fixture produces same candidate list
- flipping a macro axis flips the relevant driver state
- all candidate lanes exist in the ETF discovery universe
- candidates remain internal and do not affect report actions

---

### Phase 7 — Stage-2 confirmation and fundable integration

Implement WP-9.3.

**New / changed files:**

- `runtime/valuation_sanity.py`
- `runtime/score_etf_lanes.py`
- `runtime/discover_etf_lanes.py`
- challenger/fundability validators
- possibly `runtime/portfolio_rotation_engine.py` if rotation logic needs new fields

**Rules:**

A lane can become fundable only if it has:

```text
active thesis driver
+ documented driver→beneficiary rationale
+ relative-strength / duel confirmation
+ valuation-grade pricing
+ portfolio discipline clearance
+ valuation/crowding caution if applicable
```

**Important distinction:**

- no RS confirmation → remains `candidate`
- momentum-confirmed but valuation-stretched → may become `fundable`, but with caution flag
- valuation-grade pricing missing → cannot become fundable

**Done when:**

- candidate with no RS confirmation never reaches fundable
- valuation-stretched candidate carries caution flag
- every fundable item exposes full chain from driver to confirmation
- prior-week replay shows no unintended drift

---

### Phase 8 — Client-surface integration

Only after shadow validation.

**Changed files likely include:**

- `runtime/render_etf_report_from_state.py`
- `runtime/apply_nl_localization.py`
- `runtime/nl_localization.py`
- `runtime/delivery_html_overrides.py`
- `tools/validate_etf_report_content_contract.py`
- `tools/validate_etf_dutch_language_quality.py`
- `tools/validate_etf_delivery_html_contract.py`

**Rules:**

- Stage-1 candidates remain hidden
- report surfaces only post-confirmation decisions
- wording stays descriptive, not predictive
- no internal driver IDs or config labels leak to client
- Dutch output gets native terminology, not literal translation

**Done when:**

- English and Dutch reports pass validators
- no candidate-stage content appears in rendered reports
- every selection statement traces to driver link and confirmation result
- report remains premium and readable

---

## 8. Exact file impact estimate

### New files

```text
macro_sources/fred_client.py
macro_sources/ecb_client.py
macro_sources/treasury_client.py
macro_sources/vol_client.py
macro_sources/cb_calendar.py
macro_regime/classify.py
macro_regime/confidence.py
macro_regime/overlay.py
schemas/macro_policy_pack.schema.json
schemas/macro_data_audit.schema.json
config/regime_thresholds.yml
config/macro_consensus.yml
config/cb_calendar.yml
config/driver_catalog.yml
config/driver_beneficiary_map.yml
runtime/build_thesis_candidates.py
runtime/valuation_sanity.py
tools/validate_macro_compliance.py
tools/review_thesis_hit_rate.py
fixtures/macro/
MACRO_METHODOLOGY.md
```

### Existing files likely to edit

```text
runtime/build_macro_policy_pack.py
runtime/regime_memory.py
runtime/discover_etf_lanes.py
runtime/score_etf_lanes.py
runtime/render_etf_report_from_state.py
runtime/apply_nl_localization.py
runtime/nl_localization.py
.github/workflows/send-weekly-report.yml
tools/validate_etf_report_content_contract.py
tools/validate_etf_dutch_language_quality.py
tools/validate_etf_delivery_html_contract.py
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
```

---

## 9. Authority rules

### Decision framework

The macro engine describes the current regime and active drivers. It does not independently decide portfolio changes.

### Input/state contract

Authoritative macro values come from the macro audit. Authoritative pricing values come from the pricing audit. The final runtime state must link to both.

### Output contract

The client report must remain concise, premium, bilingual, and descriptive. Internal artifacts may be detailed; client output should not become a data dump.

### Operational runbook

CI must enforce:

- schema validation
- fixture replay
- macro compliance
- no candidate-stage leakage
- pricing-lineage consistency
- bilingual parity and language quality
- delivery render validation before email send

---

## 10. Proposed go/no-go conditions

Approve the roadmap only if the team accepts these conditions:

1. No production decision impact until pricing-lineage validation is stable.
2. WP-1 to WP-4 run in fixture/shadow mode first.
3. WP-7 compliance gate exists before any new macro/thesis content reaches the client report.
4. WP-9 Stage-1 candidates stay internal.
5. Fundable requires thesis + market confirmation + valuation-grade pricing + discipline gates.
6. Institutional overlay may cap confidence, never set regime or portfolio action.
7. Schema must be corrected before WP-9 implementation.
8. Dutch output must be protected by native terminology and validator coverage.
9. The model remains descriptive, not predictive.
10. Every change must be traceable through control files, schemas, fixtures, and CI.

---

## 11. Recommended next action

Create a control-layer proposal PR with no runtime code changes yet.

**First PR should update only:**

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
```

**Purpose of first PR:**

- record team approval of the roadmap
- lock the sequencing
- state that macro work starts in shadow mode
- prevent future confusion between “candidate”, “fundable”, and “client-facing recommendation”

After that, start Phase 2 with the macro audit foundation.

---

## 12. Bottom line

The work packages are valid and implementable. They should be accepted as the next major model-quality roadmap for `weekly-etf`, but only under a strict phased rollout.

The correct sequence is:

```text
1. Complete pricing-lineage proof
2. Build macro audit foundation
3. Replace hardcoded regime/confidence logic
4. Validate macro policy pack schema
5. Add compliance and methodology
6. Add thesis candidates in shadow mode
7. Add Stage-2 confirmation and valuation flags
8. Only then surface confirmed outputs in the client report
```

This keeps the report deterministic, auditable, premium, and compliant while meaningfully improving portfolio decision quality.
