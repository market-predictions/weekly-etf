# Handover — WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
PR: #76
Status: closed

## Merge evidence

```text
final_validated_head: 830f79c09cbb170f748f840647ddccfe78d3c68c
WP08_validation_run: 29533435789
current_runtime_validation_run: 29533435716
validation_conclusion: success
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
```

## What changed

The side-by-side builder is now evidence-based rather than a static June review template.

```text
schema_version: cockpit_side_by_side_review_v2
review_type: evidence_based_side_by_side_preview_only
review_conclusion: iteration_required
promotion_status: not_promoted
```

It selects the current `_04` classic sources and current bilingual cockpit previews, evaluates eleven dimensions, stores SHA-256 input identities and renders structured English/Dutch review HTML.

## Passed dimensions

```text
readability
density
visual_hierarchy
executed_action_clarity
current_weight_accuracy
performance_risk_accuracy
trust_provenance_clarity
audit_evidence_preservation
```

## Blocking dimensions

```text
decision_clarity
bilingual_semantic_parity
premium_look_and_feel
```

## Required fixes carried forward

1. Replace the activity-contradicting summary after an executed rotation.
2. Add a concise next-action trigger derived from current authority.
3. Fix the Dutch sentence terminator.
4. Replace hybrid Dutch provenance labels with natural Dutch wording.

## Safety result

```text
production_report_change: none
promotion_change: none
email_send: false
portfolio_model_execution: false
authority_file_mutation: false
delivery_change: false
```

## Evidence artifact

```text
cockpit-wp08-evidence-review-29533073516
sha256:a52ec091725dae17d992d940454cb11daa8dad1c6b7f585beec90f0473a473f0
```

## Next package

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

WP09 remains preview-only and must rerun WP08 v2 unchanged after the narrow refinements.
