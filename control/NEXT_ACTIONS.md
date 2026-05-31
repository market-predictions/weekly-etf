# ETF Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 0 — approved macro/thesis roadmap control lock

### 0. Record roadmap approval and sequencing

- Owner: `[ASSISTANT]`
- Status: completed on 2026-05-31
- Source files:
  - `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md`
  - `control/CURRENT_STATE.md`
  - `control/NEXT_ACTIONS.md`
  - `control/DECISION_LOG.md`
- Decision:
  - The team approved the Macro & Thesis Engine roadmap as the next major model-quality track for `weekly-etf`.
  - The roadmap is approved under strict phased sequencing and shadow-first implementation.
- Locked sequence:
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
- Authority rule:
  > Macro/regime modernization is approved as a post-pricing-lineage enhancement. Until validated in fixtures and shadow runs, the new macro engine may produce internal artifacts but must not change client-facing fundable decisions.

---

## Phase 1 — pricing-lineage closure and runtime baseline protection

### 1. Keep using the control-layer start sequence

- Owner: `[JOINT]`
- Status: active standing rule
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, localization, macro/thesis, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution files

### 2. Treat runtime + delivery HTML as the production baseline

- Owner: `[JOINT]`
- Status: active baseline
- Current baseline:
  ```text
  pricing audit
  → historical relative strength
  → macro policy pack
  → first-pass lane discovery
  → targeted challenger pricing
  → final lane discovery
  → challenger fundability validation
  → portfolio rotation plan
  → runtime state
  → EN/NL markdown render
  → pricing-basis disclosure
  → polish/linkify/localization
  → persisted valuation state
  → equity-curve validation
  → Dutch quality validation
  → delivery HTML overrides
  → bilingual delivery HTML validation
  → pricing-lineage pre-send gate
  → PDF/email delivery workflow step
  ```
- Action:
  - do not repair strict branded sections through markdown post-processing
  - do not let new macro/thesis content bypass runtime-state, bilingual parity, delivery HTML, or compliance validation
  - do not claim email delivery without a delivery receipt/manifest or explicit user confirmation

### 3. ETF pricing-lineage contract

- Owner: `[ASSISTANT]`
- Status: completed / active regression guard
- Evidence:
  - confirmation run id: `20260531_200843`
  - requested close date: `2026-05-29`
  - manifest: `output/run_manifests/weekly_etf_run_manifest_2026-05-29_20260531_200843.json`
  - `pricing_lineage_status: passed`
  - `workflow_conclusion: success`
  - English report: `output/weekly_analysis_pro_260529_22.md`
  - Dutch report: `output/weekly_analysis_pro_nl_260529_22.md`
  - runtime state: `output/runtime/etf_report_state_20260529_20260531_200843.json`
  - pricing audit: `output/pricing/price_audit_2026-05-29_20260531_200843.json`
  - NAV validated: `109964.97`
- Implemented files:
  - `tools/validate_etf_pricing_lineage_contract.py`
  - `tools/validate_etf_client_surface_clean.py`
  - `tools/write_weekly_etf_run_manifest.py`
  - `.github/workflows/send-weekly-report.yml`
- Action going forward:
  - keep the hard pricing-lineage validator before send
  - keep manifest status `passed` separate from workflow lifecycle status
  - do not weaken valuation-grade challenger pricing requirements
  - do not describe delivery as successful without delivery evidence

### 4. Remaining pricing-related enhancement: independent verification

- Owner: `[ASSISTANT]`
- Status: optional future enhancement, not a blocker
- Action:
  - add cross-provider verification where feasible
  - upgrade rows from `fresh_exact_unverified` to `fresh_exact_close` only when independent providers agree on requested-date close
- Done when:
  - pricing audit records independent verification source/status
  - exact verified rows can be distinguished from exact unverified rows

---

## Phase 2 — macro audit foundation, shadow-only

### 5. Preserve Phase 2 macro audit as non-authoritative until promoted

- Owner: `[ASSISTANT]`
- Status: started / shadow-only
- Current files:
  - `config/macro_data_sources.yml`
  - `config/cb_calendar.yml`
  - `macro_sources/build_macro_data_audit.py`
  - `tools/validate_macro_data_audit.py`
  - `schemas/macro_data_audit.schema.json`
  - `runtime/build_macro_policy_pack.py`
- Current rule:
  - macro audit may build internal provenance artifacts
  - macro audit values must not change regime, confidence, lane scoring, fundability, portfolio actions, or client-facing wording yet
  - macro audit unavailability is non-blocking while the layer remains shadow-only
- Next action:
  - add fixture replay examples for no-network validation
  - document which official/market sources are authoritative enough for Phase 3

### 6. Define macro policy pack schema before changing decisions

- Owner: `[ASSISTANT]`
- Status: next architecture task
- Target files:
  - `schemas/macro_policy_pack.schema.json`
  - `runtime/build_macro_policy_pack.py`
  - `config/regime_thresholds.yml`
- Action:
  - define required fields for regime, confidence decomposition, central-bank stance, active drivers, lane adjustments, and provenance
  - ensure backward compatibility for `lane_adjustments`
  - explicitly mark any field that is shadow-only versus decision-authoritative
- Done when:
  - current legacy pack validates or has a compatibility adapter
  - future deterministic regime engine has a stable output contract before implementation

---

## Phase 3 — deterministic regime and confidence engine

### 7. Replace hardcoded regime/confidence logic in shadow mode first

- Owner: `[ASSISTANT]`
- Status: planned
- Target files:
  - `macro_regime/classify.py`
  - `macro_regime/confidence.py`
  - `config/regime_thresholds.yml`
  - `runtime/regime_memory.py` only if extension is needed
- Action:
  - move thresholds out of code into config
  - compute confidence from cross-axis agreement rather than fixed constants
  - keep output descriptive, not predictive
  - preserve current production decisions during shadow comparison
- Done when:
  - fixture inputs produce deterministic regime/confidence outputs
  - old versus new pack differences can be reviewed before promotion

---

## Phase 4 — compliance and methodology gates

### 8. Add macro/thesis methodology and compliance validator

- Owner: `[ASSISTANT]`
- Status: planned before client-surface expansion
- Target files:
  - `MACRO_METHODOLOGY.md`
  - `tools/validate_macro_compliance.py`
  - Dutch language validator extensions if macro/thesis wording reaches Dutch reports
- Action:
  - block predictive phrasing about market levels or central-bank actions
  - require cited/paraphrased overlay entries
  - block Stage-1 candidate leakage
  - ensure every client-surfaced macro claim traces to provenance
- Done when:
  - planted forecast sentences fail validation
  - uncited overlay entries fail validation
  - orphan macro claims fail validation

---

## Phase 5 — WP-9 thesis candidates in shadow mode

### 9. Build thesis candidate layer as internal artifact only

- Owner: `[ASSISTANT]`
- Status: planned
- Target files:
  - `config/driver_catalog.yml`
  - `config/driver_beneficiary_map.yml`
  - `runtime/build_thesis_candidates.py`
  - `output/macro/thesis_candidates_<reference_date>_<run_id>.json`
- Action:
  - define closed driver IDs
  - derive active drivers from macro axes
  - map drivers to beneficiary ETF lanes through curated config
  - keep candidates internal until Stage-2 confirmation gates pass
- Done when:
  - same fixture produces same candidate list
  - candidate lanes exist in the ETF discovery universe
  - no candidate-stage content appears in client reports

---

## Phase 6 — Stage-2 confirmation and fundable integration

### 10. Add thesis → fundable promotion discipline

- Owner: `[ASSISTANT]`
- Status: planned after shadow validation
- Target files:
  - `runtime/valuation_sanity.py`
  - `runtime/score_etf_lanes.py`
  - `runtime/discover_etf_lanes.py`
  - challenger/fundability validators
- Action:
  - require active thesis driver
  - require documented driver → beneficiary rationale
  - require relative-strength / duel confirmation
  - require valuation-grade pricing
  - add valuation/crowding caution flag where needed
- Done when:
  - no RS confirmation means candidate remains candidate
  - no valuation-grade pricing means not fundable
  - every fundable item exposes a complete chain from driver to confirmation

---

## Phase 7 — Dutch quality and alias cleanup

### 11. Consolidate bilingual alias handling

- Owner: `[ASSISTANT]`
- Status: useful cleanup after pricing-lineage closure
- Target files:
  - `runtime/nl_localization.py`
  - `runtime/apply_nl_localization.py`
  - `send_report.py`
  - `tools/validate_etf_delivery_html_contract.py`
  - `tools/validate_etf_dutch_language_quality.py`
- Action:
  - keep Dutch terminology and aliases in one source of truth
  - reuse that source from markdown localization, send-time parity checks, Dutch quality validation, and delivery HTML validation

---

## Phase 8 — ChatGPT-triggerable report generation

### 12. Use safe report request queue for ChatGPT-initiated fresh reports

- Owner: `[ASSISTANT]`
- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Do not create trigger files under `output/`.
- After triggering, inspect the resulting run artifacts/manifests and workflow logs where available.
- Do not ask the user to check the Actions tab unless connector access is insufficient and the run cannot be diagnosed from repo evidence.

---

## Immediate next recommended action

Continue the approved roadmap with **Phase 2/3 macro-regime work**, not more pricing repair:

1. Freeze the latest pricing-lineage evidence as the baseline.
2. Add macro pack schema / compatibility adapter.
3. Add deterministic regime/confidence engine in shadow mode.
4. Add fixture replay tests before any production decision impact.

Do not move WP-9 thesis candidates into production until schema, compliance, fixture replay, and bilingual gates exist.
