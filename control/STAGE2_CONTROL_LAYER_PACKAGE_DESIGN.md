# Stage-2 Explicit Control-Layer Decision Package Design

## Status

design-only.

No live decision artifact is created.

No Stage-2 promotion is made.

No production report authority is granted.

No scoring authority is granted.

No fundability authority is granted.

No portfolio-action authority is granted.

No delivery authority is granted.

No execution authority is granted.

No historical-output mutation authority is granted.

A future explicit control-layer decision package is required.

A separate future implementation package is required.

The future explicit decision package must not rely on chat memory as source evidence.

## 1. Decision framework design

WP42 designs the authority rules for a future explicit decision package. It does not make that future decision.

Authority rule:

```text
A future explicit control-layer decision package may record only a control-layer decision artifact.
It may not mutate reports, scoring, fundability, portfolio state, delivery, execution, runtime state, or historical outputs.
Any production use requires a separate future implementation package after the explicit decision.
```

The chain remains:

```text
Stage-2 shadow confirmation
→ promotion-review artifact schema
→ promotion-review checklist validation
→ fixture replay
→ decision artifact design
→ decision artifact schema
→ decision artifact validator fixtures
→ validator hardening
→ sample generation gate
→ dry-run artifact builder
→ explicit decision artifact design review
→ non-production fixture gate
→ explicit control-layer decision package design
→ future explicit control-layer decision package
→ separate future implementation package
```

## 2. Input/state contract design

Required future evidence references:

```text
control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md
control/STAGE2_PROMOTION_REVIEW_EXPLICIT_DECISION_ARTIFACT_DESIGN_REVIEW.md
control/decision_records/stage2_promotion_review_decision_artifact_design_20260617.md
control/decision_records/stage2_promotion_review_decision_schema_20260617.md
control/decision_records/stage2_promotion_review_decision_fixtures_20260617.md
control/decision_records/stage2_promotion_review_decision_hardening_20260617.md
control/decision_records/stage2_promotion_review_decision_sample_gate_20260617.md
control/decision_records/stage2_promotion_review_decision_dry_run_20260617.md
control/decision_records/stage2_promotion_review_explicit_decision_design_review_20260617.md
control/decision_records/stage2_decision_non_production_fixture_gate_20260617.md
schemas/stage2_promotion_review_decision.schema.json
fixtures/stage2_promotion_review_decision/manifest.json
tools/validate_stage2_promotion_review_decision_schema.py
tools/validate_stage2_promotion_review_decision_fixtures.py
tools/validate_stage2_promotion_review_decision_hardening.py
tools/validate_stage2_promotion_review_decision_sample_gate.py
tools/validate_stage2_promotion_review_decision_dry_run.py
tools/validate_stage2_promotion_review_explicit_decision_design_review.py
tools/wp41_validator.py
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

The future explicit decision package must also verify the latest production baseline and must preserve delivery evidence as delivery-layer evidence only, not inbox receipt evidence.

## 3. Output contract design

Allowed future decision package statuses:

```text
not_promoted
rejected_not_promoted
blocked_missing_evidence
blocked_by_authority_boundary
ready_for_future_implementation_package_not_promoted
```

Forbidden future decision package statuses:

```text
promoted_to_production
promoted_to_report
production_ready
client_facing_ready
fundable_ready
portfolio_action_ready
delivery_ready
execution_ready
trade_ready
```

Required future authority defaults:

```text
client_facing_authority: false
production_report_narrative_authority: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
portfolio_mutation: false
historical_output_mutation: false
delivery_authority: false
execution_authority: false
report_surface_allowed: false
production_report_path_changed: false
decision_artifact_only: true
implementation_required_before_production_use: true
explicit_control_layer_decision_required: true
```

WP42 creates no live output. The future control-layer decision package must not reference output as a write target.

## 4. Operational runbook design

WP42 adds this design document, a validator, and tests only.

A future explicit control-layer decision package must:

```text
verify every required evidence reference
validate the closed decision schema
validate fixture evidence
validate hardening
validate sample gate behavior
validate dry-run behavior
validate non-production fixture gate behavior
record only a control-layer decision artifact if separately approved
leave production use to a separate implementation package
```

No delivery or inbox receipt is claimed by this design.
