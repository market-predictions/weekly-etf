# Deterministic Macro Regime Promotion Contract

## Purpose

This contract defines what must be true before deterministic macro regime output may move from shadow-only evidence to report narrative authority.

The contract prevents accidental promotion merely because the deterministic macro shadow engine works.

## Layer

```text
decision framework + input/state contract
```

## Scope

This contract applies to deterministic macro regime artifacts and any English/Dutch macro narrative candidate derived from them.

It does not grant authority to:

```text
portfolio actions
lane scoring
fundability
funding
portfolio mutation
execution
```

## Status model

Allowed promotion statuses:

```text
not_promoted
promoted_to_report_narrative_authority
```

The default and safe status is:

```text
not_promoted
```

A `not_promoted` artifact is valid when all client-facing and production narrative authority fields remain false.

## Required promotion gates

Promotion to report narrative authority requires all of the following approvals:

```text
methodology_approved=true
bilingual_parity_approved=true
compliance_validator_passed=true
old_vs_new_comparison_reviewed=true
explicit_control_layer_promotion_decision=true
```

Promotion also requires:

```text
control_layer_decision=promote_to_report_narrative_authority
client_facing_narrative_authority=true
production_report_narrative_authority=true
blockers=[]
```

## Permanent authority boundaries

Even after report narrative promotion, the deterministic macro regime must not automatically receive these authorities:

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
```

Those authorities require separate explicit promotion contracts.

## Required artifact fields

A promotion decision artifact must include:

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

Required schema values:

```text
schema_version=macro_regime_promotion_decision_v1
artifact_type=deterministic_macro_regime_promotion_decision
```

Required approval keys:

```text
methodology_approved
bilingual_parity_approved
compliance_validator_passed
old_vs_new_comparison_reviewed
```

Required promotion decision keys:

```text
control_layer_decision
explicit_control_layer_promotion_decision
decision_record_path
reviewed_by_or_process
```

Required authority keys:

```text
portfolio_action_authority
lane_scoring_authority
fundability_authority
funding_authority
portfolio_mutation
```

## Valid not-promoted state

A valid not-promoted artifact must keep:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

It may contain blockers explaining why promotion is not yet approved.

## Valid promoted state

A valid promoted artifact must keep:

```text
status=promoted_to_report_narrative_authority
client_facing_narrative_authority=true
production_report_narrative_authority=true
methodology_approved=true
bilingual_parity_approved=true
compliance_validator_passed=true
old_vs_new_comparison_reviewed=true
control_layer_decision=promote_to_report_narrative_authority
explicit_control_layer_promotion_decision=true
blockers=[]
```

The permanent authority boundaries must still remain false.

## Operational rule

A passing validator proves only that the promotion decision artifact is internally consistent with this contract.

It does not by itself prove that the production report has been updated, that delivery succeeded, or that portfolio-action authority exists.

## Validator

```bash
python tools/validate_macro_regime_promotion_contract.py <artifact.json>
```

Focused tests:

```bash
python -m pytest tests/test_macro_regime_promotion_contract.py -q
```
