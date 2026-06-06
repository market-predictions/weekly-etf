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
- Latest macro roadmap gate evidence:
  ```text
  WP1 — Deterministic macro narrative shadow candidate: completed / not promoted
  WP2 — Macro narrative compliance and bilingual parity gate: completed / not promoted
  WP3 — Macro promotion decision contract: completed / merged via PR #51
  WP3 merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
  WP4 — Dutch / bilingual alias consolidation: partial / regression guard added
  WP4 commit: 25dbd2c12167b20c771e3a98188f4f0125470421
  ```
- Action:
  - preserve the split between runtime provenance and post-execution official portfolio state
  - do not repair strict branded sections through markdown post-processing
  - keep delivery-runtime localization for strict PDF/HTML panels
  - keep WP1 macro shadow narrative as comparison/review evidence only
  - keep WP2 macro client-surface/parity validation as a safety gate only, not promotion authority
  - keep WP3 as narrative-promotion decision contract only, not portfolio/lane/fundability authority
  - keep WP4 as output-contract regression hardening only until full alias consolidation is complete
  - keep workflow success, pricing-lineage success, SMTP-send evidence, report-surface evidence, macro shadow-narrative evidence, macro client-surface validation evidence, macro-promotion decision evidence, Dutch terminology validation evidence, and inbox receipt distinct

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

---

## Phase 2 — Dutch quality and alias cleanup

### 3. WP4 — Complete Dutch / bilingual alias consolidation

- Owner: `[ASSISTANT]`
- Status: partial / regression guard added / full consolidation still open
- Evidence:
  ```text
  tests/test_dutch_terminology_contract.py
  commit: 25dbd2c12167b20c771e3a98188f4f0125470421
  ```
- Current guard covers:
  ```text
  No / under review → Nee / onder herbeoordeling
  Smaller / under review → Kleiner / onder herbeoordeling
  Hold but replaceable → Aanhouden, maar vervangbaar
  runtime.nl_terminology as shared marker/forbidden-label source
  native Dutch scrub as guard-only / narrow-alias based
  sitecustomize.py must not own client-facing Dutch enum/status aliases
  ```
- Remaining work:
  - move remaining repeated/migration Dutch aliases into one shared source where safe
  - make native render, markdown validation, Dutch quality validation, delivery HTML validation, and delivery runtime use that same source
  - review remaining alias surfaces in:
    ```text
    runtime/nl_localization.py
    runtime/apply_nl_localization.py
    runtime/scrub_nl_client_language.py
    runtime/delivery_html_overrides.py
    runtime/client_facing_sanitizer.py
    ```
  - reduce scattered one-off mappings without reintroducing broad English-to-Dutch translation passes
- Expected validation:
  ```bash
  python tools/validate_etf_dutch_language_quality.py
  python tools/validate_etf_delivery_html_contract.py
  python -m pytest tests/test_dutch_terminology_contract.py -q
  ```
- Boundary:
  - no pricing change
  - no portfolio-state change
  - no lane-scoring change
  - no fundability change
  - no deterministic macro promotion
  - no production delivery authority change
  - no inbox receipt claim

---

## Phase 3 — macro roadmap gates

### 4. WP1 — Deterministic macro narrative shadow candidate

- Owner: `[ASSISTANT]`
- Status: completed as shadow-only comparison path / not promoted
- Remaining action:
  - keep artifact as review/comparison evidence only
  - do not insert candidate wording into the report without WP2/WP3 and explicit promotion
  - do not feed it into portfolio actions, lane scoring, fundability, or delivery logic

### 5. WP2 — Macro narrative compliance and bilingual parity gate

- Owner: `[ASSISTANT]`
- Status: completed as output-contract safety gate / not promoted
- Remaining action:
  - keep as an active regression gate for any future macro narrative candidate
  - do not interpret a WP2 pass as promotion authority

### 6. WP3 — Macro promotion decision contract

- Owner: `[ASSISTANT]`
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
  - do not grant portfolio-action, lane-scoring, fundability, funding, mutation or delivery authority through WP3

### 7. WP7 — Future macro client-surface pilot

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

### 8. WP5 — Add direct replacement-edge scoring

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

### 9. Use safe report request queue for ChatGPT-initiated fresh reports

- Owner: `[ASSISTANT]`
- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Then verify the workflow outcome and repo artifacts directly where possible instead of asking the user to inspect Actions manually.
