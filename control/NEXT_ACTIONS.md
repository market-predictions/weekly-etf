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

### 1. Treat runtime + manifest-linked delivery evidence as latest production baseline

- Owner: `[JOINT]`
- Status: active baseline
- Latest fully recorded production evidence:
  ```text
  workflow: Send weekly ETF Pro report
  run_number: 216
  trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
  run_id: 20260605_081216
  requested_close_date: 2026-06-04
  workflow_status: workflow_success
  workflow_conclusion: success
  pricing_lineage_status: passed
  delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_081216.json
  final_run_manifest_path: output/run_manifests/weekly_etf_run_manifest_2026-06-04_20260605_081216.json
  report_authority_source: runtime_state
  english_report_path: output/weekly_analysis_pro_260604_10.md
  dutch_report_path: output/weekly_analysis_pro_nl_260604_10.md
  total_portfolio_value_eur: 111105.47
  evidence_type: full pricing-lineage + delivery-manifest baseline
  inbox_receipt: not_proven
  ```
- Previous fully recorded production evidence:
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
  manifest reconciliation: completed; not visual-only
  ```
- Latest macro roadmap gate evidence:
  ```text
  WP1 — Deterministic macro narrative shadow candidate: completed / not promoted
  WP2 — Macro narrative compliance and bilingual parity gate: completed / not promoted
  WP3 — Macro promotion decision contract: completed / merged via PR #51
  WP3 merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
  ```
- Action:
  - preserve the split between runtime provenance and post-execution official portfolio state
  - do not repair strict branded sections through markdown post-processing
  - keep delivery-runtime localization for strict PDF/HTML panels
  - keep WP1 macro shadow narrative as comparison/review evidence only
  - keep WP2 macro client-surface/parity validation as a safety gate only, not promotion authority
  - keep WP3 as narrative-promotion decision contract only, not portfolio/lane/fundability authority
  - keep workflow success, pricing-lineage success, SMTP-send evidence, report-surface evidence, macro shadow-narrative evidence, macro client-surface validation evidence, macro-promotion decision evidence, and inbox receipt distinct

### 2. ETF pricing-lineage and delivery-evidence contract

- Owner: `[ASSISTANT]`
- Status: completed / active regression guard
- Current rules:
  ```text
  runtime state = pricing/report-state provenance for run #216 / run 20260605_081216
  official portfolio state = post-execution active holdings when guarded execution occurs
  client report Section 7 / Section 15 = authoritative report values from the validated run state/official state path
  final run manifest = must link delivery_manifest_path when delivery evidence exists
  delivery manifest = redaction-safe SMTP-send evidence, not inbox receipt
  ```
- Action going forward:
  - keep the hard pricing-lineage validator before send
  - keep manifest status `passed` separate from workflow lifecycle status
  - keep current active-holdings pricing rows dynamic, not stale hardcoded ticker sets
  - keep valuation-grade challenger pricing requirements
  - keep delivery summary redaction-safe
  - do not describe delivery as end-recipient receipt unless user confirms receipt or a true receipt artifact exists

### 3. Direct visual PDF inspection / report-surface cleanup

- Owner: `[JOINT]`
- Status: closed for the current `_10` surface-cleanup loop
- Future action:
  - repeat visual inspection only when a new PDF/layout/localization defect is reported or after major delivery HTML changes
  - when inspecting, use user-uploaded PDFs or a renderable Actions artifact because GitHub binary files may only expose base64 text through the connector

### 4. Remaining pricing-related enhancement: independent verification

- Owner: `[ASSISTANT]`
- Status: optional future enhancement, not a blocker
- Action:
  - add cross-provider verification where feasible
  - upgrade rows from `fresh_exact_unverified` to `fresh_exact_close` only when independent providers agree on requested-date close

---

## Phase 2 — Dutch quality and alias cleanup

### 5. Consolidate bilingual alias handling

- Owner: `[ASSISTANT]`
- Status: next recommended cleanup / not a blocker for current production surface
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

## Phase 3 — macro roadmap gates

### 6. WP1 — Deterministic macro narrative shadow candidate

- Owner: `[ASSISTANT]`
- Status: completed as shadow-only comparison path / not promoted
- Remaining action:
  - keep artifact as review/comparison evidence only
  - do not insert candidate wording into the report without WP2/WP3 and explicit promotion
  - do not feed it into portfolio actions, lane scoring, fundability, or delivery logic

### 7. WP2 — Macro narrative compliance and bilingual parity gate

- Owner: `[ASSISTANT]`
- Status: completed as output-contract safety gate / not promoted
- Remaining action:
  - keep as an active regression gate for any future macro narrative candidate
  - do not interpret a WP2 pass as promotion authority

### 8. WP3 — Macro promotion decision contract

- Owner: `[ASSISTANT]`
- Status: completed / merged / not promoted
- Evidence:
  ```text
  PR #51 — WP3: Add macro promotion decision contract
  merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
  files:
    control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
    tools/validate_macro_regime_promotion_contract.py
    fixtures/macro_promotion/not_promoted_valid.json
    fixtures/macro_promotion/bad_promoted_without_approval.json
    tests/test_macro_regime_promotion_contract.py
  ```
- Authority boundaries:
  ```text
  portfolio_action_authority=false
  lane_scoring_authority=false
  fundability_authority=false
  funding_authority=false
  portfolio_mutation=false
  ```
- Remaining action:
  - keep deterministic macro regime shadow-only unless a future artifact satisfies the promotion contract
  - do not interpret WP3 merge as report narrative promotion
  - do not grant portfolio-action, lane-scoring, fundability, funding, mutation or delivery authority through WP3

### 9. Future macro client-surface pilot

- Owner: `[JOINT]`
- Status: possible next macro package, not started
- Preconditions:
  - WP1 completed
  - WP2 completed
  - WP3 completed
  - explicit decision to run a non-authoritative pilot
- Boundary:
  - pilot may show a controlled report-side preview only if explicitly approved
  - pilot must not affect portfolio actions, lane scoring, fundability, funding, execution, or delivery authority

---

## Phase 4 — direct challenger-vs-current-holding scoring

### 10. Add direct replacement-edge scoring

- Owner: `[ASSISTANT]`
- Status: future model enhancement
- Action:
  - map challenger lanes to the holding they may replace
  - compute direct 1m and 3m relative strength versus that holding
  - include drawdown/volatility edge
  - feed diagnostic result into replacement-duel notes
- Boundary:
  - diagnostic-only at first
  - no automatic trade, funding, or fundability authority

---

## Phase 5 — ChatGPT-triggerable report generation

### 11. Use safe report request queue for ChatGPT-initiated fresh reports

- Owner: `[ASSISTANT]`
- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Then verify the workflow outcome and repo artifacts directly where possible instead of asking the user to inspect Actions manually.
