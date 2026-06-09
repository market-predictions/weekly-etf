# ETF Review OS — Current State

## Snapshot date
2026-06-10

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**ETF has a latest fully recorded runtime-driven bilingual baseline with pricing-lineage proof and delivery-manifest evidence for workflow run #216 / run `20260605_081216`, completed macro promotion-preparation packages WP1, WP2, WP3, WP7, WP8, WP9, and WP10, completed supporting Dutch terminology and replacement-edge diagnostic packages, and completed WP11A-FIX render-path wiring for replacement-edge diagnostic notes. WP10 created an explicit deterministic macro narrative authority promotion decision artifact with `status=not_promoted`. Deterministic macro regime remains outside production report narrative authority, lane scoring, fundability, portfolio action, funding authority, portfolio mutation, delivery authority, execution authority, and production report mutation. Replacement-edge notes are now wired into the polished report surface as diagnostic-only evidence and do not grant lane-scoring, fundability, recommendation, execution, or portfolio mutation authority.**

## Latest production and report-surface evidence

```text
workflow: Send weekly ETF Pro report
run_number: 216
run_id: 20260605_081216
requested_close_date: 2026-06-04
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
report_authority_source: runtime_state
english_report_path: output/weekly_analysis_pro_260604_10.md
dutch_report_path: output/weekly_analysis_pro_nl_260604_10.md
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_081216.json
final_run_manifest_path: output/run_manifests/weekly_etf_run_manifest_2026-06-04_20260605_081216.json
total_portfolio_value_eur: 111105.47
```

This is full pricing-lineage + delivery-manifest baseline evidence. It is not an end-recipient inbox receipt.

## Macro roadmap implementation status

### WP1 — Deterministic macro narrative shadow candidate

```text
status: completed as shadow-only comparison path
artifact: output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json
production_report=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
```

### WP2 — Macro narrative compliance and bilingual parity gate

```text
status: completed as output-contract safety gate
production_report_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
delivery_authority=false
```

WP2 validates wording/parity safety only. It is not promotion authority.

### WP3 — Macro promotion decision contract

```text
status: completed / merged
contract: control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
validator: tools/validate_macro_regime_promotion_contract.py
```

WP3 defines the decision contract for narrative authority only. It does not grant portfolio-action, lane-scoring, fundability, funding, mutation, execution, delivery, or report-integration authority.

### WP7 — Deterministic macro regime client-surface pilot

```text
status: completed as controlled non-authoritative pilot / not_promoted
artifact: output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json
wp2_validation_status=passed
wp3_promotion_status=not_promoted
client_surface_pilot=true
client_facing=false
production_report=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
production_report_mutation=false
```

The WP7 artifact is preview/review evidence only.

### WP8 — Macro old-vs-new review evidence package

```text
status: completed / validated / ready_for_narrative_promotion_review / not_promoted
artifact: output/macro/review/macro_old_vs_new_review_20260605_000000.json
review_status: ready_for_narrative_promotion_review
```

WP8 is review evidence only. It is not promotion and does not mutate the production report, delivery workflow, portfolio state, lane scoring, fundability, funding, or portfolio actions.

### WP9 — Controlled deterministic macro narrative promotion artifact

```text
status: completed / validated / not_promoted
artifact: output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

WP9 does not integrate deterministic macro wording into the live production report.

### WP10 — Explicit deterministic macro narrative authority promotion decision

```text
status: completed / validated / not_promoted
artifact: output/macro/promotion/macro_regime_promotion_decision_20260606_000000.json
test: tests/test_macro_regime_promotion_decision_artifact.py
local artifact validation: python tools/validate_macro_regime_promotion_contract.py output/macro/promotion/macro_regime_promotion_decision_20260606_000000.json = MACRO_REGIME_PROMOTION_CONTRACT_OK
local focused test: python -m pytest tests/test_macro_regime_promotion_decision_artifact.py -q = 4 passed
```

WP10 records the explicit promotion decision as:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

Authority boundaries preserved:

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
delivery_authority=false
execution_authority=false
production_report_mutation=false
```

Reason: the current control files did not contain an explicit control-layer instruction to promote narrative authority. WP8 readiness remains eligibility for promotion review, not automatic promotion.

### WP11A-FIX — Replacement-edge diagnostic notes render integration

```text
status: completed / render-path-wired / validator-added / awaiting CI confirmation
helper: runtime/replacement_edge_report_notes.py
render path: runtime/polish_runtime_reports.py
validator: tools/validate_etf_report_content_contract.py
test: tests/test_replacement_edge_report_notes.py
marker: ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

WP11A-FIX wires replacement-edge diagnostic notes into the polished English and Dutch report surfaces below the replacement-duel / vervangingsanalyse section.

Authority boundaries preserved:

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

Validation still required by CI/local worker:

```bash
python -m pytest tests/test_replacement_edge_report_notes.py -q
```

A fresh report run should confirm the updated content validator passes against a newly polished English report.

## Four-layer operating status

### 1. Decision framework

- Deterministic macro remains review/control evidence only.
- WP10 explicitly records `status=not_promoted`.
- Green compliance or review status does not equal production promotion or trade authority.
- WP5 replacement-edge scoring remains diagnostic-only.
- WP11A-FIX exposes replacement-edge diagnostics as report notes only, not as allocation, scoring, fundability, recommendation, execution, or mutation authority.

### 2. Input/state contract

Authoritative production inputs remain runtime/pricing/manifest/state artifacts. Macro promotion-preparation, review, and decision artifacts remain control/review artifacts only:

```text
output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
output/macro/pilot/macro_regime_client_surface_pilot_<run_id>.json
output/macro/review/macro_old_vs_new_review_<run_id>.json
output/macro/promotion/macro_regime_promotion_decision_<run_id>.json
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
```

Replacement-edge notes are rendered from diagnostic artifacts/helper logic and remain non-authoritative.

### 3. Output contract

- WP7 pilot output is preview/review evidence only.
- WP8 old-vs-new review is not promotion.
- WP9 and WP10 both record `status=not_promoted`.
- Deterministic macro wording remains outside the production report path.
- No production report output was changed by WP10.
- WP11A-FIX adds replacement-edge diagnostic notes to the polished English/Dutch report surface with explicit diagnostic-only wording.

### 4. Operational runbook

WP10 operation is separate from production report integration:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
+ output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json
+ output/macro/review/macro_old_vs_new_review_20260605_000000.json
+ output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json
→ output/macro/promotion/macro_regime_promotion_decision_20260606_000000.json
→ tools/validate_macro_regime_promotion_contract.py
```

This path records a decision artifact only. The current WP10 artifact is `not_promoted` and must not mutate the production report or delivery workflow.

WP11A-FIX operation is report-surface only. It does not change pricing, lane scoring, rotation, execution, trade intent, or portfolio-state mutation logic.

## Immediate priorities

### Priority A — preserve pricing-lineage and delivery-evidence discipline

Do not weaken pricing lineage, manifest, official portfolio-state, or delivery-evidence boundaries. Delivery evidence remains SMTP-send/report-generation evidence unless a real receipt exists.

### Priority B — preserve WP10 `not_promoted` boundary

WP10 has created a WP3-compatible explicit promotion decision artifact with `status=not_promoted`. Deterministic macro wording remains outside production report narrative authority. Any future production report integration requires a future explicit promotion decision and a separate report-integration work package.

### Priority C — validate WP11A-FIX in CI/fresh report run

WP11A-FIX has wired replacement-edge diagnostic notes into the polished report surface and content validator. The next validation step is to run focused tests and a fresh report/content-validation pass, then record the resulting evidence.
