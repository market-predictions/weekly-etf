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
- Latest roadmap evidence:
  ```text
  WP1 — Deterministic macro narrative shadow candidate: completed / not promoted
  WP2 — Macro narrative compliance and bilingual parity gate: completed / not promoted
  WP3 — Macro promotion decision contract: completed / merged via PR #51
  WP4 — Dutch / bilingual alias consolidation: completed / validated
  WP5 — Direct challenger-vs-current-holding scoring: completed / diagnostic-only
  WP6 — Latest-run manifest / delivery evidence reconciliation: completed
  WP7 — Deterministic macro regime client-surface pilot: completed / non-authoritative / not promoted
  WP8 — Macro old-vs-new review evidence package: completed / ready_for_narrative_promotion_review / not promoted
  WP9 — Controlled deterministic macro narrative promotion artifact: completed / status=not_promoted
  ```
- Action:
  - preserve the split between runtime provenance and post-execution official portfolio state
  - keep WP1 macro shadow narrative as comparison/review evidence only
  - keep WP2 macro client-surface/parity validation as a safety gate only, not promotion authority
  - keep WP3 as narrative-promotion decision contract only, not portfolio/lane/fundability authority
  - keep WP7 macro client-surface pilot preview-only until an explicit future WP3-compliant promotion decision changes that
  - keep WP8 old-vs-new review as evidence only; it is not promotion and does not mutate production reports
  - keep WP9 promotion decision artifact as `not_promoted`; it records no production report narrative authority and no production report mutation
  - keep WP5 replacement-edge scoring diagnostic-only until an explicit future authority/integration decision changes that
  - keep workflow success, pricing-lineage success, SMTP-send evidence, report-surface evidence, macro shadow-narrative evidence, macro client-surface validation evidence, macro-promotion decision evidence, Dutch terminology validation evidence, replacement-edge evidence, pilot-preview evidence, old-vs-new review evidence, and inbox receipt distinct

---

## Phase 2 — macro roadmap gates

### 2. WP1 — Deterministic macro narrative shadow candidate

- Status: completed as shadow-only comparison path / not promoted
- Remaining action:
  - keep artifact as review/comparison evidence only
  - do not insert candidate wording into the report without WP2/WP3 and explicit promotion
  - do not feed it into portfolio actions, lane scoring, fundability, or delivery logic

### 3. WP2 — Macro narrative compliance and bilingual parity gate

- Status: completed as output-contract safety gate / not promoted
- Remaining action:
  - keep as an active regression gate for any future macro narrative candidate
  - do not interpret a WP2 pass as promotion authority

### 4. WP3 — Macro promotion decision contract

- Status: completed / merged / not promoted
- Evidence:
  ```text
  PR #51 — WP3: Add macro promotion decision contract
  merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
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

### 5. WP7 — Deterministic macro regime client-surface pilot

- Status: completed as controlled non-authoritative pilot / not promoted
- Evidence:
  ```text
  runtime/render_macro_regime_client_surface_pilot.py
  tools/validate_macro_regime_client_surface_pilot.py
  tests/test_macro_regime_client_surface_pilot.py
  output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json
  reported focused test: python -m pytest tests/test_macro_regime_client_surface_pilot.py -q = 10 passed
  reported pilot validation: MACRO_REGIME_CLIENT_SURFACE_PILOT_OK
  reported WP2 validation on pilot: MACRO_NARRATIVE_CLIENT_SURFACE_OK
  ```
- Authority boundaries:
  ```text
  wp3_promotion_status=not_promoted
  production_report_narrative_authority=false
  portfolio_action_authority=false
  lane_scoring_authority=false
  fundability_authority=false
  funding_authority=false
  portfolio_mutation=false
  production_report_mutation=false
  ```

### 6. WP8 — Macro old-vs-new review evidence package

- Status: completed / validated / not promoted
- Evidence:
  ```text
  runtime/build_macro_old_vs_new_review_package.py
  tools/validate_macro_old_vs_new_review_package.py
  tests/test_macro_old_vs_new_review_package.py
  output/macro/review/macro_old_vs_new_review_20260605_000000.json
  review_status: ready_for_narrative_promotion_review
  ```
- Boundary:
  - review evidence only
  - not promotion
  - no production report mutation
  - production_report_narrative_authority=false
  - portfolio_action_authority=false
  - lane_scoring_authority=false
  - fundability_authority=false
  - funding_authority=false
  - portfolio_mutation=false
  - delivery_authority=false

### 7. WP9 — Controlled deterministic macro narrative promotion artifact

- Owner: `[ASSISTANT]`
- Status: completed / validated / `status=not_promoted`
- Evidence:
  ```text
  output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json
  tests/test_macro_regime_promotion_decision_artifact.py
  local validation: python tools/validate_macro_regime_promotion_contract.py output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json = MACRO_REGIME_PROMOTION_CONTRACT_OK
  local focused test: python -m pytest tests/test_macro_regime_promotion_decision_artifact.py -q = 4 passed
  ```
- Decision:
  - WP9 records `not_promoted` because no explicit control-layer instruction to promote was present.
  - WP8 `ready_for_narrative_promotion_review` remains review eligibility only, not promotion.
- Authority boundaries:
  ```text
  client_facing_narrative_authority=false
  production_report_narrative_authority=false
  portfolio_action_authority=false
  lane_scoring_authority=false
  fundability_authority=false
  funding_authority=false
  portfolio_mutation=false
  delivery_authority=false
  execution_authority=false
  production_report_mutation=false
  ```
- Remaining action:
  - do not integrate deterministic macro wording into production reports unless a future explicit control-layer decision promotes narrative authority and a separate report-integration work package changes the production report path

---

## Phase 3 — Dutch quality and alias cleanup

### 8. WP4 — Dutch / bilingual alias consolidation

- Status: completed / validated
- Remaining action:
  - keep shared Dutch terminology contract active as a regression surface

---

## Phase 4 — replacement-edge scoring

### 9. WP5 — Direct challenger-vs-current-holding scoring

- Status: completed as diagnostic-only scoring package
- Authority boundaries:
  ```text
  diagnostic_only=true
  portfolio_action_authority=false
  fundability_authority=false
  lane_scoring_authority=false
  funding_authority=false
  portfolio_mutation=false
  production_recommendation_authority=false
  ```
- Remaining action:
  - decide in a future package whether and how to consume replacement-edge diagnostics in replacement-duel notes or current-position review
  - keep diagnostic-only unless a separate authority decision grants lane-scoring, fundability, recommendation, or portfolio-action use

---

## Phase 5 — possible follow-up packages

### 10. Integrate replacement-edge diagnostics into notes, non-authoritative

- Status: possible follow-up, not started
- Boundary:
  - no lane-scoring authority
  - no fundability authority
  - no trade authority
  - no production recommendation authority unless separately approved

### 11. Use safe report request queue for ChatGPT-initiated fresh reports

- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Then verify the workflow outcome and repo artifacts directly where possible instead of asking the user to inspect Actions manually.

### 12. Future deterministic macro report integration, only after explicit promotion

- Status: not started / blocked
- Boundary:
  - WP9 did not promote narrative authority
  - no production report mutation has occurred
  - a future package must explicitly promote narrative authority first, then separately integrate report output
