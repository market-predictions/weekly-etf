# Stage-2 Promotion Review Decision Artifact Design

## Status

Design-only.

No live decision artifact is created.

No Stage-2 promotion decision is made.

No production report authority is granted.

No scoring authority is granted.

No fundability authority is granted.

No portfolio-action authority is granted.

No delivery or execution authority is granted.

No historical-output mutation authority is granted.

This document is a design contract for a future explicit control-layer decision artifact. It does not create a decision artifact, does not promote Stage-2 output, and does not change production report output, lane scoring, fundability, portfolio actions, delivery behavior, execution behavior, or historical output files.

## Purpose

Define how a future Stage-2 promotion review decision artifact may be structured, reviewed, validated, and bounded.

The decision path remains:

```text
Stage-2 shadow confirmation
→ promotion-review artifact schema
→ promotion-review checklist validation
→ fixture replay
→ future decision artifact design
→ explicit future control-layer decision
→ separate future implementation package
```

WP34 only defines the future decision artifact rules. It does not write a live review artifact and does not write a live decision artifact under `output/`.

## Four-layer design

### 1. Decision framework

A later control-layer decision artifact may record whether a reviewed Stage-2 evidence chain remains blocked, remains not promoted, or is ready for a separate explicit decision package.

Allowed future non-promotional decision statuses are:

```text
not_promoted
rejected_not_promoted
blocked_missing_evidence
blocked_by_authority_boundary
ready_for_explicit_promotion_decision_not_promoted
```

The design keeps promotion behavior out of WP34. Any production-impacting status is outside this work package and requires a separate future control-layer decision package plus a separate future implementation package before any production use.

The future decision artifact may not create a trade, recommendation, portfolio action, fundability decision, delivery action, execution action, report wording change, or historical-output mutation.

### 2. Input/state contract

A future decision artifact must cite exact source evidence from the completed design and validation chain:

```text
control/STAGE2_PROMOTION_BRIDGE_DESIGN.md
schemas/stage2_promotion_review.schema.json
tools/validate_stage2_promotion_review_checklist.py
fixtures/stage2_promotion_review/manifest.json
tools/validate_stage2_promotion_review_fixtures.py
control/MACRO_STAGE2_CONFIRMATION_STATUS.md
output/macro/validation/latest_stage2_confirmation_validation.json
tools/validate_etf_macro_thesis_surface_leakage.py
config/macro_thesis_bilingual_aliases.yml
tools/validate_macro_report_surface.py
control/CURRENT_STATE.md
```

The latest verified production baseline reference must remain traceable through `control/CURRENT_STATE.md` and the run-scoped manifest-linked production baseline.

No prompt memory, chat summary, prior report prose, or raw internal reasoning may substitute for the explicit evidence chain.

### 3. Output contract

The future decision artifact is a control-layer artifact only. It must use a closed, review-safe structure and must preserve no-authority defaults.

Illustrative future artifact shape:

```json
{
  "schema_version": "1.0",
  "artifact_type": "stage2_promotion_review_decision",
  "decision_status": "not_promoted",
  "decision_scope": "review_decision_only",
  "generated_at_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "authority": {
    "client_facing_authority": false,
    "production_report_narrative_authority": false,
    "lane_scoring_authority": false,
    "fundability_authority": false,
    "portfolio_action_authority": false,
    "portfolio_mutation": false,
    "historical_output_mutation": false,
    "delivery_authority": false,
    "execution_authority": false,
    "report_surface_allowed": false,
    "production_report_path_changed": false,
    "decision_artifact_only": true,
    "implementation_required_before_production_use": true,
    "explicit_control_layer_decision_required": true
  },
  "source_evidence": {
    "promotion_bridge_design": "control/STAGE2_PROMOTION_BRIDGE_DESIGN.md",
    "review_schema": "schemas/stage2_promotion_review.schema.json",
    "review_checklist_validator": "tools/validate_stage2_promotion_review_checklist.py",
    "fixture_manifest": "fixtures/stage2_promotion_review/manifest.json",
    "fixture_validator": "tools/validate_stage2_promotion_review_fixtures.py",
    "stage2_shadow_status": "control/MACRO_STAGE2_CONFIRMATION_STATUS.md",
    "stage2_shadow_validation": "output/macro/validation/latest_stage2_confirmation_validation.json",
    "leakage_validator": "tools/validate_etf_macro_thesis_surface_leakage.py",
    "bilingual_aliases": "config/macro_thesis_bilingual_aliases.yml",
    "macro_report_surface_validator": "tools/validate_macro_report_surface.py",
    "latest_verified_production_baseline": "control/CURRENT_STATE.md"
  },
  "decision_rationale": [],
  "blocking_conditions": [],
  "required_future_work": []
}
```

This JSON is illustrative only. It is not a live artifact and must not be committed under `output/` by WP34.

Required false/no-authority fields are:

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
```

Required control booleans are:

```text
decision_artifact_only: true
implementation_required_before_production_use: true
explicit_control_layer_decision_required: true
```

Forbidden direct decision-surface values are blocklisted below and may appear only in this blocklist, validator tests, or planted failure examples:

```text
stage_1_candidate
stage_2_confirmed_not_fundable
stage_2_fundable_ready_shadow
stage2_status
confirmation_status
driver_id
driver_ids
active_drivers
driver_catalog
driver_beneficiary_map
shadow_only
internal_only
```

These raw fields must not be used as approved decision-facing labels, client-facing wording, scoring inputs, fundability signals, portfolio-action triggers, delivery triggers, or execution triggers.

### 4. Operational runbook

WP34 adds only:

```text
control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md
tools/validate_stage2_promotion_review_decision_artifact_design.py
tests/test_stage2_promotion_review_decision_artifact_design.py
.github/workflows/validate-stage2-promotion-review-decision-artifact-design.yml
```

The validator must prove that the design:

```text
states design-only status
states no live decision artifact is created
states no Stage-2 promotion decision is made
requires all false/no-authority fields
requires source evidence from WP30, WP31, WP32, and WP33
references leakage validation, bilingual aliases, and macro report surface validation
defines only non-promotional current decision behavior
blocks forbidden current-status claims
blocks raw internal fields from approved decision-surface labels
preserves the separate future implementation package requirement
```

Before any later production implementation, a separate future package must exist and must pass the relevant schema, checklist, fixture, leakage, bilingual alias, macro surface, Dutch language, report-content, delivery, pricing-lineage, and runtime-state validators.

## Explicit non-goals

WP34 does not:

```text
create a live decision artifact
write a decision artifact under output
promote Stage-2 output
change production report wording
change Dutch report generation
change lane scoring
change fundability
change portfolio actions
change delivery behavior
change execution behavior
mutate historical outputs
```

## Future gate

A future implementation package may be considered only after:

```text
this design validates
Stage-2 promotion review decision artifact schema exists
Stage-2 promotion review decision artifact validator exists
all Stage-2 review schema/checklist/fixture validators pass
all leakage/bilingual/macro-surface validators pass
an explicit control-layer decision package is separately approved
```

Until then, Stage-2 output remains shadow evidence and review material only.
