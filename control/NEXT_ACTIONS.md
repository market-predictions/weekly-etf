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
- Latest fully recorded production evidence:
  ```text
  workflow: Send weekly ETF Pro report
  run_number: 205
  trigger_commit: 3bd07f7ff31af77adbd23359d66a8c5ab7ab3343
  run_id: 20260604_190001
  requested_close_date: 2026-06-03
  workflow_status: workflow_success
  workflow_conclusion: success
  pricing_lineage_status: passed
  delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-03_20260604_190001.json
  report_authority_source: portfolio_state_post_execution
  english_report_path: output/weekly_analysis_pro_260603.md
  dutch_report_path: output/weekly_analysis_pro_nl_260603.md
  total_portfolio_value_eur: 111596.96
  ```
- Latest report-surface cleanup evidence:
  ```text
  workflow: Send weekly ETF Pro report
  run_number: 216
  trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
  workflow_conclusion: success
  user-visible cleanup status: score completeness fixed, stale GLD current wording fixed, Dutch enum leakage fixed
  inspected artifacts: weekly_analysis_pro_260604_10.pdf, weekly_analysis_pro_nl_260604_10.pdf
  ```
- Latest macro shadow-narrative evidence:
  ```text
  Work Package 1 — Deterministic macro narrative shadow candidate
  status: implemented as shadow-only comparison path
  artifact: output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json
  reported focused test: python -m pytest tests/test_macro_regime_shadow_narrative.py -q = 4 passed
  reported artifact validation: MACRO_REGIME_SHADOW_NARRATIVE_OK
  authority: client_facing=false, production_report=false, portfolio_action_authority=false, lane_scoring_authority=false, fundability_authority=false
  ```
- Action:
  - preserve the split between runtime provenance and post-execution official portfolio state
  - do not repair strict branded sections through markdown post-processing
  - keep delivery-runtime localization for strict PDF/HTML panels
  - do not let new macro/thesis content bypass runtime-state, bilingual parity, delivery HTML, or compliance validation
  - keep WP1 macro shadow narrative as comparison/review evidence only
  - keep workflow success, pricing-lineage success, SMTP-send evidence, report-surface evidence, macro shadow-narrative evidence, and inbox receipt distinct

### 2. ETF pricing-lineage and delivery-evidence contract

- Owner: `[ASSISTANT]`
- Status: completed / active regression guard
- Current files:
  - `tools/validate_etf_pricing_lineage_contract.py`
  - `tools/validate_etf_client_surface_clean.py`
  - `tools/write_weekly_etf_run_manifest.py`
  - `tools/write_etf_delivery_manifest_summary.py`
  - `.github/workflows/send-weekly-report.yml`
  - `control/DELIVERY_MANIFEST_STATUS_20260604.md`
- Current rules:
  ```text
  runtime state = pre-execution pricing/report-state provenance
  official portfolio state = post-execution active holdings after guarded execution
  client report Section 7 / Section 15 = post-execution official portfolio state when execution occurred in the same run
  delivery manifest = redaction-safe SMTP-send evidence, not inbox receipt
  ```
- Action going forward:
  - keep the hard pricing-lineage validator before send
  - keep manifest status `passed` separate from workflow lifecycle status
  - keep current active-holdings pricing rows dynamic, not stale hardcoded ticker sets
  - keep valuation-grade challenger pricing requirements
  - keep delivery summary redaction-safe
  - do not describe delivery as end-recipient receipt unless user confirms receipt or a true receipt artifact exists

### 3. Delivery receipt/manifest evidence

- Owner: `[ASSISTANT]`
- Status: closed for this stage / SMTP-send evidence green
- Remaining boundary:
  - delivery evidence is SMTP-send evidence only, not inbox placement / end-recipient receipt
  - report-generation or visual PDF evidence does not equal inbox receipt

### 4. Direct visual PDF inspection / report-surface cleanup

- Owner: `[JOINT]`
- Status: closed for the current `_10` surface-cleanup loop
- Completed evidence:
  ```text
  uploaded English PDF: weekly_analysis_pro_260604_10.pdf
  uploaded Dutch PDF: weekly_analysis_pro_nl_260604_10.pdf
  workflow run observed: Send weekly ETF Pro report #216 success
  trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
  ```
- Completed findings:
  - all active positions have numeric scores in Current Position Review / Review huidige posities
  - stale GLD current-surface wording is removed from the Dutch conclusion
  - `No / under review` no longer leaks into the final Dutch report view after the delivery enum patch
  - unwanted `Nee / onder herbeoordeling` surface wording is gone from the report where it should not appear
- Future action:
  - repeat visual inspection only when a new PDF/layout/localization defect is reported or after major delivery HTML changes
  - when inspecting, use user-uploaded PDFs or a renderable Actions artifact because GitHub binary files may only expose base64 text through the connector

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
  - keep strict branded report sections localized at delivery HTML/runtime layer when those panels are regenerated after markdown

### 7. Consolidate bilingual alias handling

- Owner: `[ASSISTANT]`
- Status: useful cleanup; not a blocker for the current production surface
- Current reason:
  - the latest Dutch enum leak proved that markdown scrub and native Dutch validation are not enough for strict branded PDF/HTML panels rebuilt from runtime state
  - delivery-runtime alias maps must share the same terminology source as native render and validators
- Target files:
  - `runtime/nl_terminology.py`
  - `runtime/nl_localization.py`
  - `runtime/apply_nl_localization.py`
  - `runtime/scrub_nl_client_language.py`
  - `runtime/delivery_html_overrides.py`
  - `runtime/client_facing_sanitizer.py`
  - `sitecustomize.py`
  - `send_report_runtime_html.py`
  - `tools/validate_etf_delivery_html_contract.py`
  - `tools/validate_etf_dutch_language_quality.py`
- Action:
  - keep Dutch terminology and aliases in one source of truth
  - reuse that source from native render, markdown validation, send-time parity checks, Dutch quality validation, delivery HTML validation, and startup/delivery patches
  - avoid one-off text fixes spread across validators

---

## Phase 3 — macro audit foundation, shadow-only

### 8. Preserve Phase 2 macro audit as non-authoritative until promoted

- Owner: `[ASSISTANT]`
- Status: fixture replay wired / shadow-only baseline green
- Current rule:
  - macro audit may build internal provenance artifacts
  - macro audit values must not change regime, confidence, lane scoring, fundability, portfolio actions, or client-facing wording yet
  - macro audit unavailability is non-blocking while the layer remains shadow-only
  - macro-audit-derived axes may be validated as shadow evidence only
- Remaining action:
  - document which official/market sources are authoritative enough for later Phase 3 promotion
  - keep all macro-audit-derived axes out of client reports and portfolio authority until methodology/compliance/promotion gates pass

### 9. Macro policy pack schema / promotion contract

- Owner: `[ASSISTANT]`
- Status: closed for this stage / active promotion firewall
- Current rule:
  - current macro policy pack remains a legacy compatibility pack
  - `lane_adjustments` remain legacy-compatible only
  - `deterministic_regime_shadow`, `macro_axes`, `macro_axis_scores`, confidence decomposition, and active drivers remain shadow/internal unless explicitly promoted
  - promotion gates remain `not_promoted`
- Remaining action:
  - keep this contract active as a firewall for later deterministic regime/thesis work
  - do not expand authority without explicit control-layer promotion

---

## Phase 4 — deterministic regime and confidence engine

### 10. Replace hardcoded regime/confidence logic in shadow mode first

- Owner: `[ASSISTANT]`
- Status: shadow implementation/calibration closed for this stage; not promoted
- Current rule:
  - shadow confidence measures descriptive cross-axis agreement, not forecast probability
  - risk-on shadow confidence can be capped when audited macro axes materially disagree
  - non-risk-on macro disagreements are diagnostic only at this stage
- Remaining action:
  - review old-versus-new pack differences before any promotion discussion
  - keep output descriptive, not predictive
  - preserve current production decisions during shadow comparison

### 10A. Work Package 1 — Deterministic macro narrative shadow candidate

- Owner: `[ASSISTANT]`
- Status: completed as shadow-only comparison path / not promoted
- Files:
  - `runtime/render_macro_regime_shadow_narrative.py`
  - `tools/validate_macro_regime_shadow_narrative.py`
  - `tests/test_macro_regime_shadow_narrative.py`
  - `output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json`
- Evidence:
  ```text
  reported focused test: python -m pytest tests/test_macro_regime_shadow_narrative.py -q = 4 passed
  reported artifact validation: MACRO_REGIME_SHADOW_NARRATIVE_OK
  ```
- Authority boundaries:
  ```text
  client_facing=false
  production_report=false
  portfolio_action_authority=false
  lane_scoring_authority=false
  fundability_authority=false
  ```
- Remaining action:
  - keep the artifact as review/comparison evidence only
  - do not insert candidate wording into the report without WP2 compliance/parity and WP3 promotion-contract gates
  - do not feed it into portfolio actions, lane scoring, fundability, or delivery logic

---

## Phase 5 — compliance and methodology gates

### 11. Macro/thesis methodology and compliance validator

- Owner: `[ASSISTANT]`
- Status: closed for current shadow-compliance stage / active regression guard
- Current coverage:
  - predictive macro/market/central-bank phrasing blocks
  - uncited overlay claims block
  - orphan macro figures block
  - Stage-1 candidate leakage blocks
  - shadow/internal label leakage blocks
  - macro-conflict cap methodology validation
  - macro pack report surface validation when `output/macro/latest.json` exists
  - latest committed English/Dutch report macro sections validation
- Remaining action:
  - keep this as an active regression guard
  - add further planted-failure fixtures only if a new macro/thesis surface risk appears
  - do not interpret green compliance as promotion authority

### 11A. Work Package 2 — Macro narrative compliance and bilingual parity gate

- Owner: `[ASSISTANT]`
- Status: next recommended macro roadmap package
- Goal:
  - validate that deterministic macro narrative candidates are safe for English/Dutch client wording before any client-surface pilot
- Required boundaries:
  - block predictive wording
  - block uncited macro claims
  - block shadow/internal labels
  - block `macro_axes` leakage
  - block `confidence_decomposition` leakage
  - block English leakage in Dutch report
  - block Dutch/English meaning drift
- Done when:
  ```bash
  python -m pytest tests/test_macro_narrative_client_surface.py -q
  ```
  passes with safe fixtures passing and bad fixtures failing

### 11B. Work Package 3 — Macro promotion decision contract

- Owner: `[ASSISTANT]`
- Status: next recommended macro roadmap package
- Goal:
  - define exactly what must be true before deterministic macro regime can move from shadow to report narrative authority
- Required contract:
  - methodology approved
  - bilingual parity approved
  - compliance validator passed
  - old-vs-new comparison reviewed
  - no portfolio-action authority
  - no lane-scoring authority
  - explicit control-layer promotion decision
- Done when:
  ```bash
  python -m pytest tests/test_macro_regime_promotion_contract.py -q
  ```
  passes

---

## Phase 6 — WP-9 thesis candidates in shadow mode

### 12. Build thesis candidate layer as internal artifact only

- Owner: `[ASSISTANT]`
- Status: closed for this stage / shadow-only evidence green
- Current rule:
  - Stage-1 thesis candidates are internal only
  - candidates are not fundable without Stage-2 confirmation, valuation-grade pricing, and portfolio discipline gates
  - candidates must not appear in English or Dutch reports
  - candidates must not feed lane scoring, fundability, portfolio actions, or recommendations until explicitly promoted
- Remaining action:
  - keep as an active shadow evidence guard
  - do not consume `output/macro/latest_thesis_candidates.json` in production runtime paths without explicit promotion

---

## Phase 7 — Stage-2 confirmation and fundable integration

### 13. Add thesis → fundable promotion discipline

- Owner: `[ASSISTANT]`
- Status: contract baseline green / not promoted
- Current rule:
  - `ready_for_promotion_review_not_promoted` is the maximum allowed status before explicit promotion
  - `fundable`, `recommended`, `portfolio_action_ready`, and `client_facing` are blocked by contract validation
  - authority flags for client surface, lane scoring, fundability, portfolio actions, report surface, and production report path must remain false
- Remaining action:
  - do not integrate Stage-2 output into `runtime/score_etf_lanes.py`, `runtime/discover_etf_lanes.py`, reports, or execution until a later explicit promotion review
  - if promotion is later requested, first design non-authoritative Stage-2 chain artifacts and compare them against lane discovery without changing fundability

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
