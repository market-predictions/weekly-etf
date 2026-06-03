# ETF Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 0 — control-layer operating discipline

### 0. Keep using the control-layer start sequence

- Owner: `[JOINT]`
- Status: active standing rule
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, localization, macro/thesis, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution files

---

## Phase 1 — production baseline and pricing-lineage protection

### 1. Treat runtime + post-execution official state as production baseline

- Owner: `[JOINT]`
- Status: active baseline
- Latest evidence:
  ```text
  workflow: Send weekly ETF Pro report
  run_number: 195
  trigger_commit: e0a6f075127f1a079ca880accd26923928349f9c
  run_id: 20260601_213417
  requested_close_date: 2026-06-01
  workflow_status: workflow_success
  workflow_conclusion: success
  pricing_lineage_status: passed
  report_authority_source: portfolio_state_post_execution
  english_report_path: output/weekly_analysis_pro_260601_04.md
  dutch_report_path: output/weekly_analysis_pro_nl_260601_04.md
  total_portfolio_value_eur: 110290.91
  ```
- Current baseline:
  ```text
  pricing audit
  → historical relative strength
  → macro policy pack, with macro audit shadow-only
  → first-pass lane discovery
  → targeted challenger pricing
  → final lane discovery
  → challenger fundability validation
  → portfolio rotation plan
  → runtime state
  → EN/NL native markdown render
  → pricing-basis disclosure
  → polish/linkify/localization
  → run manifest
  → persisted valuation state
  → guarded model execution
  → post-execution official portfolio state
  → delivery HTML/PDF validation
  → pricing-lineage pre-send gate
  → PDF/email delivery workflow step
  ```
- Action:
  - preserve the split between runtime provenance and post-execution official portfolio state
  - do not repair strict branded sections through markdown post-processing
  - do not let new macro/thesis content bypass runtime-state, bilingual parity, delivery HTML, or compliance validation
  - do not claim email delivery without a delivery receipt/manifest or explicit user confirmation

### 2. ETF pricing-lineage contract

- Owner: `[ASSISTANT]`
- Status: completed / active regression guard
- Current files:
  - `tools/validate_etf_pricing_lineage_contract.py`
  - `tools/validate_etf_client_surface_clean.py`
  - `tools/write_weekly_etf_run_manifest.py`
  - `.github/workflows/send-weekly-report.yml`
- Current rule:
  ```text
  runtime state = pre-execution pricing/report-state provenance
  official portfolio state = post-execution active holdings after guarded execution
  client report Section 7 / Section 15 = post-execution official portfolio state when execution occurred in the same run
  ```
- Action going forward:
  - keep the hard pricing-lineage validator before send
  - keep manifest status `passed` separate from workflow lifecycle status
  - keep current active-holdings pricing rows dynamic, not stale hardcoded ticker sets
  - keep valuation-grade challenger pricing requirements
  - do not describe delivery as successful without delivery evidence

### 3. Add delivery receipt/manifest evidence

- Owner: `[ASSISTANT]`
- Status: next operational hardening
- Problem:
  - `workflow_conclusion: success` proves the workflow passed.
  - `pricing_lineage_status: passed` proves the report/state/pricing chain passed.
  - But latest manifest still has `delivery_manifest_path: null`, so email delivery is not independently proven from repo evidence.
- Action:
  - add or repair a delivery receipt/manifest writer after the actual send step
  - record sent timestamp, report paths, PDF attachment paths, and redaction-safe recipient/transport metadata if available
  - keep delivery success separate from workflow success
- Done when:
  - run manifest points to a real `delivery_manifest_path`
  - the delivery manifest is committed or uploaded as an artifact in a durable place

### 4. Direct visual PDF inspection

- Owner: `[JOINT]`
- Status: pending only because binary artifacts are not sandbox-renderable through the current GitHub connector
- Boundary:
  - repo evidence confirms latest PDFs and chart assets exist and validations passed
  - the GitHub connector exposes binary files as base64 text resources, not sandbox-renderable files
- Action:
  - upload the latest English and Dutch PDFs here for visual inspection; or
  - expose/download the Actions artifact ZIP so the PDFs can be rendered with the PDF skill
- Done when:
  - latest English and Dutch PDFs are visually inspected for layout, chart labels, table rendering, and Dutch client-clean wording

### 5. Remaining pricing-related enhancement: independent verification

- Owner: `[ASSISTANT]`
- Status: optional future enhancement, not a blocker
- Action:
  - add cross-provider verification where feasible
  - upgrade rows from `fresh_exact_unverified` to `fresh_exact_close` only when independent providers agree on requested-date close
- Done when:
  - pricing audit records independent verification source/status
  - exact verified rows can be distinguished from exact unverified rows

---

## Phase 2 — Dutch quality and alias cleanup

### 6. Preserve native Dutch guard-only architecture

- Owner: `[JOINT]`
- Status: active baseline
- Rule:
  ```text
  runtime state / key figures
  → English native render
  → Dutch native render from same runtime state
  → guard-only native Dutch validation
  → delivery HTML/PDF validation
  ```
- Not allowed:
  ```text
  English markdown
  → broad translation / scrub
  → Dutch report
  ```
- Action:
  - keep native Dutch reports protected from broad translation-style mutation
  - only use narrow structured runtime-state display-label normalization where needed
  - keep Dutch chart labels localized in runtime delivery

### 7. Consolidate bilingual alias handling

- Owner: `[ASSISTANT]`
- Status: useful cleanup after the production baseline is green
- Target files:
  - `runtime/nl_terminology.py`
  - `runtime/nl_localization.py`
  - `runtime/apply_nl_localization.py`
  - `runtime/scrub_nl_client_language.py`
  - `send_report_runtime_html.py`
  - `tools/validate_etf_delivery_html_contract.py`
  - `tools/validate_etf_dutch_language_quality.py`
- Action:
  - keep Dutch terminology and aliases in one source of truth
  - reuse that source from native render, markdown validation, send-time parity checks, Dutch quality validation, and delivery HTML validation
  - avoid one-off text fixes spread across validators

---

## Phase 3 — macro audit foundation, shadow-only

### 8. Preserve Phase 2 macro audit as non-authoritative until promoted

- Owner: `[ASSISTANT]`
- Status: fixture replay wired / shadow-only baseline green
- Current files:
  - `config/macro_data_sources.yml`
  - `config/cb_calendar.yml`
  - `macro_sources/build_macro_data_audit.py`
  - `tools/validate_macro_data_audit.py`
  - `schemas/macro_data_audit.schema.json`
  - `runtime/build_macro_policy_pack.py`
  - `fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json`
  - `tools/replay_macro_data_audit_shadow_fixture.py`
  - `.github/workflows/validate-macro-regime-shadow.yml`
  - `output/macro/validation/latest_macro_audit_axis_shadow_validation.json`
- Current rule:
  - macro audit may build internal provenance artifacts
  - macro audit values must not change regime, confidence, lane scoring, fundability, portfolio actions, or client-facing wording yet
  - macro audit unavailability is non-blocking while the layer remains shadow-only
  - macro-audit-derived axes may be validated as shadow evidence only
- Latest evidence:
  ```text
  workflow: Validate ETF macro regime shadow
  run_number: 14
  workflow_run_id: 26877273381
  trigger_commit: 3a7d87323a0a83bdaab5a81bb8a037f3babf9fff
  status: passed
  macro_data_audit_fixture: fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json
  macro_axis_evidence_path: output/macro/validation/latest_macro_audit_axis_shadow_validation.json
  regime_shadow_evidence_path: output/macro/validation/latest_macro_regime_shadow_validation.json
  markers: ETF_MACRO_REGIME_FIXTURE_REPLAY_OK, ETF_MACRO_DATA_AUDIT_VALID_OK, ETF_MACRO_AUDIT_AXIS_SHADOW_OK, ETF_MACRO_REGIME_SHADOW_OK
  ```
- Completed in this stage:
  - no-network macro-data-audit fixture replay is wired into CI
  - fixture validates required groups: `fred`, `ecb`, `treasury_fiscaldata`, `volatility`
  - shadow policy-pack builder consumes the fixture
  - `deterministic_regime_shadow.macro_axes` is populated and validated
  - repo-visible evidence is written under `output/macro/validation/`
- Remaining action:
  - document which official/market sources are authoritative enough for later Phase 3 promotion
  - keep all macro-audit-derived axes out of client reports and portfolio authority until methodology/compliance/promotion gates pass

### 9. Define macro policy pack schema before changing decisions

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

## Phase 4 — deterministic regime and confidence engine

### 10. Replace hardcoded regime/confidence logic in shadow mode first

- Owner: `[ASSISTANT]`
- Status: shadow implementation started; fixture replay green; not promoted
- Target files:
  - `macro_regime/classify.py`
  - `macro_regime/confidence.py`
  - `config/regime_thresholds.yml`
  - `runtime/build_macro_policy_pack_shadow.py`
  - `tools/replay_macro_regime_shadow_fixtures.py`
  - `tools/replay_macro_data_audit_shadow_fixture.py`
  - `runtime/regime_memory.py` only if extension is needed
- Current evidence:
  - deterministic market-proxy regime fixtures replay successfully
  - macro-audit-derived axes replay successfully via no-network fixture
  - output remains under `deterministic_regime_shadow`
  - authority flags remain shadow-only and non-client-facing
- Action:
  - move any remaining thresholds out of code into config where useful
  - review old-versus-new pack differences before promotion
  - keep output descriptive, not predictive
  - preserve current production decisions during shadow comparison
- Done when:
  - fixture inputs produce deterministic regime/confidence outputs across both market-proxy and macro-audit inputs
  - old versus new pack differences can be reviewed before promotion
  - methodology/compliance/bilingual gates are ready for any client-surface test

---

## Phase 5 — compliance and methodology gates

### 11. Add macro/thesis methodology and compliance validator

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

## Phase 6 — WP-9 thesis candidates in shadow mode

### 12. Build thesis candidate layer as internal artifact only

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

## Phase 7 — Stage-2 confirmation and fundable integration

### 13. Add thesis → fundable promotion discipline

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

## Phase 8 — direct challenger-vs-current-holding scoring

### 14. Add direct replacement-edge scoring

- Owner: `[ASSISTANT]`
- Status: future model enhancement
- Action:
  - map challenger lanes to the holding they may replace
  - compute direct 1m and 3m relative strength versus that holding
  - feed direct replacement edge into lane scoring and replacement-duel notes

---

## Phase 9 — ChatGPT-triggerable report generation

### 15. Use safe report request queue for ChatGPT-initiated fresh reports

- Owner: `[ASSISTANT]`
- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Then verify the workflow outcome and repo artifacts directly where possible instead of asking the user to inspect Actions manually.
