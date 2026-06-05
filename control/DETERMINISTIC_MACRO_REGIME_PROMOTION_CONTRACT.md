# Deterministic Macro Regime Promotion Contract

## Purpose

This contract defines exactly what must be true before deterministic macro regime output may move from shadow-only evidence to report narrative authority.

The contract exists to prevent accidental promotion merely because the shadow engine works.

## Current default status

```text
deterministic_macro_regime_shadow_only=true
client_facing_narrative_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
```

## Four-layer separation

### 1. Decision framework

The deterministic macro regime may support a future report narrative only after a separate control-layer promotion decision.

Promotion to report narrative authority must never imply portfolio-action authority, lane-scoring authority, fundability authority, funding authority, or portfolio mutation authority.

### 2. Input/state contract

A promotion decision artifact must be machine-readable JSON and must explicitly record whether all required promotion prerequisites have passed.

Required top-level fields:

```text
schema_version
artifact_type
run_id
created_at_utc
report_date
status
client_facing_narrative_authority
production_report_narrative_authority
required_approvals
promotion_decision
authority
blockers
```

Allowed `schema_version`:

```text
macro_regime_promotion_decision_v1
```

Allowed `artifact_type`:

```text
deterministic_macro_regime_promotion_decision
```

Allowed `status` values:

```text
not_promoted
promoted_to_report_narrative_authority
```

### 3. Output contract

The promotion decision artifact may be stored under:

```text
output/macro/promotion/macro_regime_promotion_decision_<run_id>.json
```

A `not_promoted` artifact is valid when it keeps narrative authority disabled and records blockers or pending approvals.

A `promoted_to_report_narrative_authority` artifact is valid only when every required approval and the explicit control-layer decision are present.

### 4. Operational runbook

Before promotion, all of the following must be true:

```text
methodology_approved=true
bilingual_parity_approved=true
compliance_validator_passed=true
old_vs_new_comparison_reviewed=true
explicit_control_layer_promotion_decision=true
```

The explicit control-layer decision must state:

```text
control_layer_decision=promote_to_report_narrative_authority
```

The artifact must also preserve:

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
```

## Required approval object

The `required_approvals` object must contain:

```text
methodology_approved
bilingual_parity_approved
compliance_validator_passed
old_vs_new_comparison_reviewed
```

For promoted artifacts, every value must be `true`.

For not-promoted artifacts, values may remain `false`, but narrative authority must remain disabled.

## Required promotion decision object

The `promotion_decision` object must contain:

```text
control_layer_decision
explicit_control_layer_promotion_decision
decision_record_path
reviewed_by_or_process
```

For promoted artifacts:

```text
control_layer_decision=promote_to_report_narrative_authority
explicit_control_layer_promotion_decision=true
```

For not-promoted artifacts:

```text
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

## Required authority object

The `authority` object must contain and preserve:

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
```

## Blocking rule

If `status=not_promoted`, `blockers` must be a non-empty list and must include:

```text
macro regime remains shadow-only
```

If any required approval is missing or false, the artifact must not use:

```text
status=promoted_to_report_narrative_authority
client_facing_narrative_authority=true
production_report_narrative_authority=true
```

## Current rule

This work package may add only:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
tools/validate_macro_regime_promotion_contract.py
fixtures/macro_promotion/not_promoted_valid.json
fixtures/macro_promotion/bad_promoted_without_approval.json
tests/test_macro_regime_promotion_contract.py
```

It must not edit the production report renderer, workflow, portfolio state, pricing authority, fundability gate, lane scoring, PDF rendering, email delivery, or delivery manifest behavior.
