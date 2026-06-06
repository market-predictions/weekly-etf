# ETF Review OS — Current State

## Snapshot date
2026-06-06

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**ETF has a latest fully recorded runtime-driven bilingual baseline with pricing-lineage proof and delivery-manifest evidence for workflow run #216 / run `20260605_081216`, a completed report-surface cleanup cycle verified by the same run, WP1 deterministic macro narrative shadow comparison implemented, WP2 macro narrative compliance/bilingual parity implemented, WP3 macro promotion decision contract merged, WP4 Dutch/bilingual alias consolidation completed and validated, WP5 direct challenger-vs-current-holding scoring implemented as diagnostic-only evidence, WP7 deterministic macro regime client-surface pilot implemented as non-authoritative preview evidence, WP8 macro old-vs-new review evidence completed with `review_status=ready_for_narrative_promotion_review`, and WP9 controlled deterministic macro narrative promotion artifact completed with `status=not_promoted`. Deterministic macro regime remains shadow-only and not promoted into production report narrative authority, lane scoring, fundability, portfolio action, funding authority, portfolio mutation, delivery authority, execution authority, or production report mutation.**

## What this repository currently is

`market-predictions/weekly-etf` is a runtime-driven production-style weekly ETF review system with:

- explicit pricing audits in `output/pricing/`
- explicit run manifests in `output/run_manifests/`
- redaction-safe delivery manifests in `output/delivery/`
- runtime report-state artifacts in `output/runtime/`
- persisted portfolio state, valuation history, and trade ledger
- guarded model execution with trade-ledger idempotency checks
- English canonical and Dutch native companion report generation
- delivery HTML overrides for strict branded sections
- hard pricing-lineage validation before send
- delivery-manifest evidence linked from the final run manifest
- shadow-first macro/thesis roadmap controls
- WP1, WP2, WP3, WP7, WP8, and WP9 deterministic macro regime promotion-preparation / review / decision gates implemented, while production authority remains blocked
- WP4 Dutch terminology consolidation completed with a shared terminology contract and focused validation
- WP5 replacement-edge scoring implemented as a diagnostic-only decision-framework/input-state artifact path

## Latest production and report-surface evidence

### Latest fully recorded pricing-lineage + delivery-manifest baseline

```text
workflow: Send weekly ETF Pro report
run_number: 216
trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
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

This proves workflow success, pricing-lineage success, final run-manifest linkage to the redaction-safe delivery manifest, and repo-visible SMTP-send evidence for that baseline. It is **not** an end-recipient inbox receipt.

### Report-surface cleanup evidence in run #216

```text
workflow: Send weekly ETF Pro report
run_number: 216
trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
workflow_conclusion: success
english_pdf: weekly_analysis_pro_260604_10.pdf
dutch_pdf: weekly_analysis_pro_nl_260604_10.pdf
```

Closed issues:

```text
Current Position Review score completeness: fixed
English/Dutch active-position score completeness: fixed
stale GLD current-surface wording: fixed
Dutch delivery enum leakage `No / under review`: fixed
unwanted `Nee / onder herbeoordeling` surface wording: removed from final report view
```

This cleanup evidence is reconciled with matching delivery and final run manifests, so run #216 is evidence type B: full pricing-lineage + delivery-manifest baseline. It remains **not** inbox-receipt evidence.

## Macro roadmap implementation status

### WP1 — Deterministic macro narrative shadow candidate

```text
status: completed as shadow-only comparison path
files:
  runtime/render_macro_regime_shadow_narrative.py
  tools/validate_macro_regime_shadow_narrative.py
  tests/test_macro_regime_shadow_narrative.py
  output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json
reported focused test: python -m pytest tests/test_macro_regime_shadow_narrative.py -q = 4 passed
reported artifact validation: MACRO_REGIME_SHADOW_NARRATIVE_OK
```

Authority boundaries:

```text
client_facing=false
production_report=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
no production report mutation
```

### WP2 — Macro narrative compliance and bilingual parity gate

```text
status: completed on main as output-contract validator/test/fixture package
files:
  tools/validate_macro_narrative_client_surface.py
  fixtures/macro_narrative/safe_shadow_candidate_en_nl.json
  fixtures/macro_narrative/bad_predictive_language.json
  fixtures/macro_narrative/bad_shadow_label_leakage.json
  fixtures/macro_narrative/bad_dutch_parity.json
  tests/test_macro_narrative_client_surface.py
reported focused test: python -m pytest tests/test_macro_narrative_client_surface.py -q = 4 passed
```

WP2 blocks predictive wording, uncited macro claims, shadow/internal labels, `macro_axes` leakage, `confidence_decomposition` leakage, English leakage in Dutch report text, citation parity mismatch, and Dutch/English meaning drift.

Authority boundaries:

```text
output_contract_gate_only=true
production_report_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
delivery_authority=false
```

### WP3 — Macro promotion decision contract

```text
status: completed / merged
PR: #51 — WP3: Add macro promotion decision contract
merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
files:
  control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
  tools/validate_macro_regime_promotion_contract.py
  fixtures/macro_promotion/not_promoted_valid.json
  fixtures/macro_promotion/bad_promoted_without_approval.json
  tests/test_macro_regime_promotion_contract.py
reported focused test from staged harness: python -m pytest tests/test_macro_regime_promotion_contract.py -q = 5 passed
```

WP3 defines the promotion gate required before deterministic macro regime output may move from shadow-only evidence to report narrative authority. It does not grant portfolio-action, lane-scoring, fundability, funding, mutation, or delivery authority.

### WP7 — Deterministic macro regime client-surface pilot

```text
status: completed as controlled non-authoritative client-surface pilot / not promoted
files:
  runtime/render_macro_regime_client_surface_pilot.py
  tools/validate_macro_regime_client_surface_pilot.py
  tests/test_macro_regime_client_surface_pilot.py
  output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json
reported focused test: python -m pytest tests/test_macro_regime_client_surface_pilot.py -q = 10 passed
reported pilot validation: MACRO_REGIME_CLIENT_SURFACE_PILOT_OK
reported WP2 validation on pilot: MACRO_NARRATIVE_CLIENT_SURFACE_OK
```

WP7 produces a pilot preview with:

```text
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

The WP7 artifact is preview/review evidence only. It does not mutate the production report, does not change delivery workflow, and does not promote deterministic macro regime into production report narrative authority.

### WP8 — Macro old-vs-new review evidence package

```text
status: completed / validated
files:
  runtime/build_macro_old_vs_new_review_package.py
  tools/validate_macro_old_vs_new_review_package.py
  tests/test_macro_old_vs_new_review_package.py
  output/macro/review/macro_old_vs_new_review_20260605_000000.json
review_status: ready_for_narrative_promotion_review
```

Validation evidence from Codespaces on `main` after `git pull` to `e301c26`:

```bash
python -m pytest tests/test_macro_old_vs_new_review_package.py -q
# 5 passed in 0.08s

python tools/validate_macro_old_vs_new_review_package.py output/macro/review/macro_old_vs_new_review_20260605_000000.json
# MACRO_OLD_VS_NEW_REVIEW_OK | artifact=output/macro/review/macro_old_vs_new_review_20260605_000000.json | review_status=ready_for_narrative_promotion_review | production_report_narrative_authority=false | portfolio_action_authority=false | lane_scoring_authority=false | fundability_authority=false | funding_authority=false | portfolio_mutation=false
```

WP8 is review evidence only. It is **not** promotion and does not mutate the production report, delivery workflow, portfolio state, lane scoring, fundability, funding, or portfolio actions.

### WP9 — Controlled deterministic macro narrative promotion artifact

```text
status: completed / validated / not_promoted
files:
  output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json
  tests/test_macro_regime_promotion_decision_artifact.py
local artifact validation: python tools/validate_macro_regime_promotion_contract.py output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json = MACRO_REGIME_PROMOTION_CONTRACT_OK
local focused test: python -m pytest tests/test_macro_regime_promotion_decision_artifact.py -q = 4 passed
```

WP9 records the control-layer promotion decision as:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

Authority boundaries:

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

WP9 does **not** integrate deterministic macro wording into the live production report. A separate explicit promotion decision and separate report-integration work package remain required before production report output changes.

## Dutch / bilingual output-contract status

### WP4 — Dutch / bilingual alias consolidation

```text
status: completed / shared terminology contract validated
final worker commit: 0ac46cfde1b57299e5523b60d92b415c161d5a28
follow-up fix commit: 661764692127f03af21e6fc961dfabddaf6a9ab5
validation environment: GitHub Codespaces on main after git pull to 6617646
```

Coordinator-side validation passed:

```bash
python -m pytest tests/test_dutch_terminology_contract.py -q
# 5 passed in 0.04s

python tools/validate_etf_dutch_language_quality.py
# ETF_DUTCH_LANGUAGE_QUALITY_OK | report=weekly_analysis_pro_nl_260604_11.md | terminology=central

python tools/validate_etf_delivery_html_contract.py
# ETF_DELIVERY_HTML_CONTRACT_OK | report=weekly_analysis_pro_260604_11.md | dynamic_holdings=CIBR,DFEN,GSG,IEFA,PAVE,SMH,SPY,URNM,XLU | post_execution=True
# ETF_DELIVERY_HTML_CONTRACT_OK | report=weekly_analysis_pro_nl_260604_11.md | dynamic_holdings=CIBR,DFEN,GSG,IEFA,PAVE,SMH,SPY,URNM,XLU | post_execution=True
```

WP4 is output-contract/runtime cleanup only and does not grant macro, delivery, portfolio, lane-scoring, fundability, funding, mutation, or receipt authority.

## Replacement-edge / challenger-vs-current status

### WP5 — Direct challenger-vs-current-holding scoring

```text
status: implemented as diagnostic-only scoring package
files:
  runtime/map_challenger_to_current_holding.py
  runtime/score_replacement_edge.py
  tools/validate_replacement_edge_scoring.py
  tests/test_replacement_edge_scoring.py
  output/replacement_edges/replacement_edge_20260606_000000.json
reported focused test: python -m pytest tests/test_replacement_edge_scoring.py -q = 4 passed
reported artifact validation: REPLACEMENT_EDGE_SCORING_OK
```

Top-level authority boundaries:

```text
diagnostic_only=true
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
portfolio_mutation=false
production_recommendation_authority=false
```

The sample artifact is review evidence only. It does not create automatic trades, mutate portfolio state, grant funding authority, grant fundability authority, grant lane-scoring authority, grant production recommendation authority, promote deterministic macro logic, or feed into live trade decisions.

## Four-layer operating status

### 1. Decision framework

- Capital re-underwriting discipline remains active.
- Broad lane discovery remains active.
- Valuation-grade challenger discipline remains active.
- Guarded model execution with trade-ledger idempotency remains active.
- Deterministic macro regime, macro axes, WP1 candidate narrative, WP2-passing surfaces, WP3 contract, WP7 pilot preview, WP8 old-vs-new review evidence, and WP9 promotion decision artifact remain non-client-facing and non-authoritative unless explicit future promotion gates pass.
- WP8 says the pilot is `ready_for_narrative_promotion_review`, not promoted.
- WP9 explicitly records `status=not_promoted`.
- WP5 replacement-edge scoring is diagnostic-only and does not create portfolio-action, lane-scoring, fundability, funding, mutation, or production-recommendation authority.
- Green compliance/validator status never equals production promotion or trade authority by itself.

### 2. Input/state contract

Authoritative production inputs remain:

```text
output/pricing/price_audit_<requested_close_date>_<run_id>.json
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/runtime/etf_report_state_<report_token>_<run_id>.json
output/runtime/etf_model_execution_<date>_<run_id>.json
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/lane_reviews/etf_lane_assessment_<report_token>.json
output/market_history/etf_relative_strength.json
output/macro/latest.json
```

Macro promotion-preparation / review / decision artifacts are review/audit/control artifacts only:

```text
output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
output/macro/pilot/macro_regime_client_surface_pilot_<run_id>.json
output/macro/review/macro_old_vs_new_review_<run_id>.json
output/macro/promotion/macro_regime_promotion_decision_<run_id>.json
fixtures/macro_narrative/*.json
fixtures/macro_promotion/*.json
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
```

Replacement-edge artifacts are diagnostic-only input/state artifacts:

```text
output/replacement_edges/replacement_edge_<run_id>.json
```

### 3. Output contract

- English is the canonical analytical report.
- Dutch is a native companion render from the same runtime state/key figures.
- Strict branded sections are rendered from runtime state at delivery HTML level.
- Current Position Review / Review huidige posities must show numeric scores for every active ETF position.
- Dutch delivery-surface enum localization must be enforced at delivery runtime, not only markdown scrub time.
- Exited-holding wording, especially stale GLD current-surface wording when GLD is not active, must be blocked.
- WP4 introduced and validated a shared Dutch terminology contract.
- WP1 deterministic macro narrative candidates must not appear in client-facing reports until WP2 and WP3 gates plus explicit future promotion pass.
- WP7 deterministic macro client-surface pilot output is preview/review evidence only and must not be treated as production report narrative integration.
- WP8 old-vs-new review evidence may support a future WP9-style promotion artifact, but it is not promotion itself.
- WP9 records `status=not_promoted`; deterministic macro wording remains out of the production report path.
- WP2 validates wording/parity safety only.
- WP3 defines the decision contract for narrative authority only; it does not grant portfolio, lane, fundability, funding, mutation, or delivery authority.
- WP5 diagnostic replacement-edge output must not appear as a production recommendation unless a later explicit integration and authority decision permits it.

### 4. Operational runbook

The production path remains:

```text
run-queue request or manual dispatch
→ resolve run identity
→ persistent ETF pricing pass
→ historical relative-strength fetch
→ macro policy pack build, with macro audit shadow-only / non-blocking
→ first-pass lane discovery
→ challenger pricing augmentation
→ final lane discovery
→ challenger fundability validation
→ portfolio rotation plan
→ runtime report state
→ EN/NL native markdown reports
→ pricing-basis disclosure
→ report polish / localization / ticker links
→ run manifest
→ persisted valuation state
→ guarded ETF model execution
→ post-execution official portfolio state
→ delivery HTML/PDF validation
→ Dutch quality validation
→ hard pricing-lineage pre-send gate
→ PDF/email delivery workflow step
→ redaction-safe delivery manifest summary
→ final manifest update with delivery_manifest_path
```

Strict branded/PDF-visible defects must be fixed in the generating layer:

```text
runtime state defect → fix runtime state builder
markdown-only defect → fix native renderer / polish / linkifier
strict branded panel defect → fix delivery HTML overrides
send-time enum/localization defect → fix delivery runtime / shared localization map
validator gap → add or tighten relevant pre-send gate
```

WP7 operation is separate from production report integration:

```text
output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
→ runtime/render_macro_regime_client_surface_pilot.py
→ output/macro/pilot/macro_regime_client_surface_pilot_<run_id>.json
→ tools/validate_macro_regime_client_surface_pilot.py
→ tools/validate_macro_narrative_client_surface.py
```

WP8 operation is separate from promotion:

```text
output/macro/pilot/macro_regime_client_surface_pilot_<run_id>.json
→ runtime/build_macro_old_vs_new_review_package.py
→ output/macro/review/macro_old_vs_new_review_<run_id>.json
→ tools/validate_macro_old_vs_new_review_package.py
```

This path is review-only and must not mutate the production report or delivery workflow.

WP9 operation is separate from production report integration:

```text
output/macro/pilot/macro_regime_client_surface_pilot_<run_id>.json
+ output/macro/review/macro_old_vs_new_review_<run_id>.json
+ control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
→ output/macro/promotion/macro_regime_promotion_decision_<run_id>.json
→ tools/validate_macro_regime_promotion_contract.py
```

This path records a decision artifact only. The current WP9 artifact is `not_promoted` and must not mutate the production report or delivery workflow.

WP5 operation is separate from production execution:

```text
output/lane_reviews/etf_lane_assessment_<date>.json
+ output/market_history/etf_relative_strength.json
+ output/etf_portfolio_state.json
→ runtime/map_challenger_to_current_holding.py
→ runtime/score_replacement_edge.py
→ output/replacement_edges/replacement_edge_<run_id>.json
→ tools/validate_replacement_edge_scoring.py
```

This path is diagnostic/review-only and must not mutate the production report or portfolio.

## Immediate priorities

### Priority A — preserve pricing-lineage and delivery-evidence discipline

Do not weaken pricing lineage, manifest, official portfolio-state, or delivery-evidence boundaries. Delivery evidence remains SMTP-send/report-generation evidence unless a real receipt exists.

### Priority B — preserve WP9 `not_promoted` boundary

WP9 has created a WP3-compatible promotion decision artifact with `status=not_promoted`. Deterministic macro wording remains outside production report narrative authority. Any future production report integration requires a new explicit promotion decision and a separate report-integration work package.

### Priority C — decide how to consume WP5 diagnostics

WP5 diagnostic replacement-edge scoring is implemented. A future package may integrate it into replacement-duel notes or the current-position review surface, but only as diagnostic evidence unless a separate authority decision grants lane-scoring, fundability, or recommendation use.
