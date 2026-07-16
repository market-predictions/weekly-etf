# Decision — WP08 evidence-based cockpit review

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Status: accepted for cockpit preview lane

## Decision

The current cockpit is not ready for a promotion decision yet.

```text
review_conclusion: iteration_required
promotion_status: not_promoted
```

The evidence-based WP08 review passes eight dimensions and identifies three blocking dimensions:

```text
decision_clarity
bilingual_semantic_parity
premium_look_and_feel
```

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

## Required next change

Create a narrow preview-only refinement package that:

1. removes the activity contradiction from the summary when actions were executed;
2. adds a concise next-action trigger derived from current authority;
3. fixes the Dutch punctuation defect;
4. replaces hybrid Dutch provenance labels with natural client-facing Dutch;
5. preserves the current design and authority boundaries;
6. reruns the unchanged WP08 v2 review contract.

## Next package

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

WP09 may improve the preview surface but may not promote, attach, send or replace the production report.

## Evidence

```text
PR: #76
validated_head: abe689064455dbd7206564037220e727c52b929b
WP08_validation_run: 29533073516
current_runtime_validation_run: 29533073585
artifact: cockpit-wp08-evidence-review-29533073516
artifact_digest: sha256:a52ec091725dae17d992d940454cb11daa8dad1c6b7f585beec90f0473a473f0
```
