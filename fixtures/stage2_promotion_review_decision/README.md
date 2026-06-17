# Stage-2 promotion review decision fixtures

These fixtures validate the Stage-2 promotion review decision schema and validator behavior.

## Scope

Validator-fixture / sample-fixture validation only.

The fixtures do not create live decision artifacts and do not grant client-facing authority, production report authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

## Fixture groups

Pass fixtures:

- `pass_not_promoted.json`
- `pass_blocked_missing_evidence.json`
- `pass_ready_for_explicit_promotion_decision_not_promoted.json`

Planted-failure fixtures:

- `fail_promoted_status.json`
- `fail_authority_true.json`
- `fail_missing_decision_artifact_design_source.json`
- `fail_missing_decision_artifact_only.json`
- `fail_raw_driver_id_text.json`
- `fail_fundable_claim_text.json`
- `fail_additional_property.json`

The manifest at `fixtures/stage2_promotion_review_decision/manifest.json` is the authority for expected fixture outcomes.
