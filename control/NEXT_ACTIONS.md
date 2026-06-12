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
- For replacement-edge report-note work, also read:
  ```text
  control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
  ```
- For deterministic macro promotion review/integration work, also read:
  ```text
  control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
  control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
  control/MACRO_REPORT_SURFACE_STATUS.md
  ```

---

## Phase 1 — production baseline and pricing-lineage protection

### 1. Treat runtime + manifest-linked delivery evidence as latest production baseline

- Owner: `[JOINT]`
- Status: active baseline
- Latest fully recorded production evidence:
  ```text
  workflow: Send weekly ETF Pro report
  github_actions_run: 27306857013
  workflow_title: Retry ETF delivery after hiding replacement-edge marker
  workflow_status: completed
  workflow_conclusion: success
  artifact_commit: e2891ca
  requested_close_date: 2026-06-10
  run_id: 20260610_211606
  report_token: 260610
  english_report_path: output/weekly_analysis_pro_260610_02.md
  dutch_report_path: output/weekly_analysis_pro_nl_260610_02.md
  english_pdf_path: output/weekly_analysis_pro_260610_02.pdf
  dutch_pdf_path: output/weekly_analysis_pro_nl_260610_02.pdf
  english_delivery_html: output/weekly_analysis_pro_260610_02_delivery.html
  dutch_delivery_html: output/weekly_analysis_pro_nl_260610_02_delivery.html
  runtime_state_path: output/runtime/etf_report_state_20260610_20260610_211606.json
  executed_runtime_state_path: output/runtime/etf_report_state_20260610_20260610_211606_already_executed.json
  pricing_audit_path: output/pricing/price_audit_2026-06-10_20260610_211606.json
  run_manifest_path: output/run_manifests/weekly_etf_run_manifest_2026-06-10_20260610_211606.json
  delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-10_20260610_211606.json
  pricing_lineage_status: passed
  pricing_coverage_count_pct: 100.0
  fresh_holdings_count: 9
  carried_forward_holdings_count: 0
  total_portfolio_value_eur: 103994.26
  cash_eur: 1936.52
  delivery_status: smtp_sendmail_returned_no_exception
  inbox_receipt: not_proven
  ```
- Delivery wording:
  - Delivery manifest recorded `smtp_sendmail_returned_no_exception` after `send_report.py` returned from `smtplib.sendmail` without raising.
  - This is delivery-layer evidence, not an end-recipient inbox receipt.
- Current holdings:
  ```text
  CIBR
  DFEN
  GSG
  IEFA
  PAVE
  SMH
  SPY
  URNM
  XLU
  ```
- Historical note:
  - Workflow run #216 / run `20260605_081216` remains historical evidence only.
  - Do not describe run #216 as the latest production baseline.
- Action:
  - keep workflow success, pricing-lineage success, SMTP-send evidence, report-surface evidence, macro client-surface validation evidence, macro-promotion decision evidence, replacement-edge evidence, delivery evidence, and inbox receipt distinct
  - do not weaken pricing-lineage, runtime-state, run-manifest, or delivery-manifest requirements

---

## Phase 2 — macro roadmap gates

### 2. Current macro surface status

- Status: client-safe macro report surface integrated
- Current production flow:
  ```text
  runtime.build_macro_policy_pack
    -> output/macro/latest.json
    -> runtime.macro_report_surface
    -> runtime.polish_runtime_reports / native report rendering
    -> English/Dutch report sections
  ```
- Validated after marker cleanup:
  ```text
  ETF_MACRO_REPORT_SURFACE_OK
  ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
  ```
- Boundary:
  - client-safe macro report surface is integrated
  - raw deterministic macro read is not client-facing
  - deterministic macro read is not promoted as official production regime source
  - do not infer promotion from green validators, review readiness, macro policy pack existence, client-safe macro surface presence, prior pilot output, or prior review artifact

### 3. Completed deterministic macro packages

- Status: completed / not promoted where applicable
- Evidence summary:
  ```text
  WP1 — Deterministic macro narrative shadow candidate: completed / not promoted
  WP2 — Macro narrative compliance and bilingual parity gate: completed / not promoted
  WP3 — Macro promotion decision contract: completed / merged
  WP7 — Deterministic macro regime client-surface pilot: completed / non-authoritative / not promoted
  WP8 — Macro old-vs-new review evidence package: completed / ready_for_narrative_promotion_review / not promoted
  WP9 — Controlled deterministic macro narrative promotion artifact: completed / status=not_promoted
  WP10 — Explicit deterministic macro narrative authority promotion decision: completed / status=not_promoted
  WP13 — Deterministic macro read promotion review: completed / review-only / not promoted
  ```
- WP13 review artifact:
  ```text
  control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
  ```
- Standing authority boundary:
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
  - future deterministic macro work must be framed as one of:
    1. shadow-quality improvement only
    2. promotion-decision preparation only
    3. explicit control-layer promotion decision
    4. separate production report integration after promotion
  - do not collapse these into one implicit change

### 4. WP13 — Deterministic macro read promotion review, not implementation

- Owner: `[ASSISTANT]`
- Status: completed / review-only / not promoted
- Artifact:
  ```text
  control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
  ```
- Six checklist questions answered:
  ```text
  What exact deterministic fields would become production narrative source?
  What bilingual surface would be allowed?
  What would remain forbidden?
  What validators must pass?
  What explicit control-layer phrase/flag authorizes promotion?
  What rollback path exists if client output regresses?
  ```
- Boundary:
  - deterministic macro was not promoted
  - production report behavior did not change
  - no scoring, fundability, execution, delivery, or portfolio state changed
  - no runtime/output/pricing/workflow files were changed

---

## Phase 3 — replacement-edge scoring and report notes

### 5. Replacement-edge diagnostic notes status

- Status: marker cleanup verified successful in current `260610_02` baseline
- Required current wording:
  ```text
  The visible marker ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED is absent from the current 260610_02 Markdown / clean Markdown / HTML / PDF surfaces.
  ```
- Boundary:
  ```text
  diagnostic_only=true
  portfolio_action_authority=false
  fundability_authority=false
  lane_scoring_authority=false
  funding_authority=false
  production_recommendation_authority=false
  execution_authority=false
  portfolio_mutation=false
  ```
- The notes must not influence:
  ```text
  ranking
  lane scoring
  fundability
  recommendation
  target weights
  trade intents
  execution
  portfolio mutation
  ```
- Historical note:
  - Older historical artifacts such as `260609_06`, `260609_07`, and early `260610` outputs may still contain the old marker.
  - Current delivery output is the fresh `260610_02` set.
  - Do not bulk-edit old historical outputs unless explicitly requested.

---

## Phase 4 — Dutch quality and output-contract guardrails

### 6. Keep output-contract validators active

- Status: active standing requirement
- Protect:
  ```text
  pricing lineage
  runtime-state authority
  bilingual English/Dutch output
  Dutch terminology contract
  ticker linkification
  client-surface scrub
  macro/thesis leakage guard
  replacement-edge diagnostic-only boundary
  delivery HTML contract
  delivery manifest summary
  run manifest summary
  ```
- Key validators:
  ```text
  tools/validate_etf_report_content_contract.py
  tools/validate_etf_macro_thesis_surface_leakage.py
  tools/validate_macro_report_surface.py
  tools/validate_macro_compliance.py
  tools/validate_etf_delivery_html_contract.py
  tools/validate_etf_client_surface_clean.py
  tools/validate_etf_model_execution.py
  tools/validate_etf_trade_ledger_idempotency.py
  ```

---

## Phase 5 — next roadmap packages

### 7. WP14 — Deterministic macro read shadow replay evidence

- Owner: `[ASSISTANT]`
- Status: next recommended package / not started
- Goal:
  ```text
  Run or prepare fixture replay evidence for deterministic macro read versus legacy macro pack over recent reports.
  ```
- Required output:
  - review artifact only
  - not client-facing report content
- Suggested artifact path:
  ```text
  output/macro/replay/deterministic_macro_shadow_replay_<run_id>.json
  ```
- Boundary:
  - no production report mutation
  - no recommendation, fundability, execution, or portfolio-state mutation
  - no deterministic macro promotion by implication

### 8. WP15 — Historical artifact cleanup policy

- Owner: `[ASSISTANT]`
- Status: recommended after WP14 or when historical-output grep noise becomes operationally blocking / not started
- Goal:
  ```text
  Decide whether old generated outputs should remain immutable historical artifacts or whether the repo wants a controlled cleanup/archive policy.
  ```
- Rationale:
  ```text
  Old reports may still contain prior client-surface issues, including the old replacement-edge marker.
  Current generated outputs are clean, but repo-wide grep can still find old artifacts.
  ```
- Boundary:
  - do not bulk-delete or rewrite historical output files without explicit user approval
  - policy first, cleanup second

---

## Do-not-do list

Do not:

```text
reintroduce ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED into report output
treat old historical artifacts as current delivery output
promote deterministic macro read by inference
let macro/thesis shadow fields leak into client output
use replacement-edge diagnostics for scoring/fundability/trades
rewrite historical output files without explicit approval
commit while a delivery workflow is running unless the commit is intentionally the trigger/fix
collapse state authority back into Markdown reports
```

---

## Useful verification commands

Check latest Actions run:

```bash
python - <<'PY'
import json, urllib.request
url='https://api.github.com/repos/market-predictions/weekly-etf/actions/runs?per_page=5'
with urllib.request.urlopen(url, timeout=20) as r:
    data=json.load(r)
for run in data.get('workflow_runs', []):
    print(run.get('id'), run.get('display_title'), run.get('status'), run.get('conclusion'), run.get('head_sha')[:12])
PY
```

Check current report marker absence:

```bash
git grep -n "ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED" origin/main -- \
  output/weekly_analysis_pro_260610_02* \
  output/weekly_analysis_pro_nl_260610_02* || true
```

Check macro surface:

```bash
python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
```

Check latest manifests:

```bash
cat output/run_manifests/latest_weekly_etf_run_manifest_path.txt
cat output/delivery/latest_weekly_etf_delivery_manifest_path.txt
```
