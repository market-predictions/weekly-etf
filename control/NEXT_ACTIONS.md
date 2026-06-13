# ETF Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 0 — control-layer operating discipline

Every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, localization, macro/thesis, or lab-optimization session starts with:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution files

For deterministic macro work, also read:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
control/MACRO_REPORT_SURFACE_STATUS.md
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/MACRO_REGIME_SHADOW_STATUS.md
control/DETERMINISTIC_REGIME_ENGINE_PROMOTION_REVIEW.md
```

For historical-output cleanup/archive questions, also read:

```text
control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md
```

---

## Phase 1 — current baseline rule

Current manifest-linked production baseline is `260612_08`.

Use:

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260613_113054.json
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_113054.json
```

Latest verified production baseline:

```text
requested_close_date: 2026-06-12
run_id: 20260613_113054
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_08.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_08.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

Historical generated outputs remain immutable by default. Do not bulk-edit old reports to remove stale wording or old markers.

---

## Phase 2 — closed repair / foundation packages

WP16 is closed on the latest verified report set.

WP17 is closed on the latest verified report set.

WP18 is closed.

WP19 is closed.

WP20 is closed.

WP20 closeout evidence:

```text
review artifact: output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
status: not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

Do not continue patching WP16/WP17/WP18/WP19/WP20 unless a new defect is found in a later manifest-linked run.

---

## Phase 3 — deterministic macro boundary

Current deterministic macro boundary remains:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
deterministic regime engine: not promoted
```

WP16/WP17/WP18/WP19/WP20 do not promote deterministic macro.

Standing authority boundary:

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

---

## Phase 4 — active package

Active package:

```text
WP21 — Deterministic regime client-safe report surface design
```

Current WP21 status:

```text
not_started / ready_to_start / design-only required
```

Scope:

```text
- output-contract design only
- define a client-safe deterministic regime report surface
- no raw macro axes in report
- no automatic production promotion
- no implementation into production report path
- no scoring/fundability changes
- no portfolio mutation
- no historical output rewrite
```

Likely start files:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
control/DETERMINISTIC_REGIME_ENGINE_PROMOTION_REVIEW.md
control/MACRO_REPORT_SURFACE_STATUS.md
runtime/macro_report_surface.py
tools/validate_macro_report_surface.py
tools/validate_macro_compliance.py
output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

Required boundary:

```text
design_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

---

## Phase 5 — next package after WP21 closes

Do not start this until WP21 is designed and closed.

Likely next package:

```text
WP22 — Deterministic regime client-safe surface validator, if WP21 produces a stable design
```

Tentative scope:

```text
- validator/specification only or narrow helper-only implementation
- no production report integration
- no automatic production promotion
- no scoring/fundability changes
- no portfolio mutation
```

---

## Do-not-do list

```text
Do not claim inbox delivery without receipt evidence.
Do not promote deterministic macro by implication.
Do not rewrite historical generated outputs.
Do not use replacement-edge diagnostics for scoring, fundability, or trades.
Do not weaken pricing-lineage or runtime-state authority.
Do not localize ETF issuer/product names such as iShares, SPDR, VanEck, Sprott, or Global X.
Do not bypass the PDF visual gate after WP17.
Do not start WP22 before WP21 is designed and closed.
```
