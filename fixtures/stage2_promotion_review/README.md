# Stage-2 promotion review fixtures

These fixtures validate the Stage-2 promotion review schema and checklist layers.

## Scope

Fixture-set design and validation only.

The fixtures do not create live production promotion artifacts and do not grant client-facing authority, production report authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

## Fixture groups

Pass fixtures:

- `pass_ready_for_review_not_promoted.json`
- `pass_not_ready_missing_evidence.json`

Planted-failure fixtures:

- `fail_authority_true.json`
- `fail_promoted_status.json`
- `fail_missing_bilingual_aliases.json`
- `fail_raw_driver_id_text.json`
- `fail_fundable_claim_text.json`

The manifest at `fixtures/stage2_promotion_review/manifest.json` is the authority for expected fixture outcomes.
