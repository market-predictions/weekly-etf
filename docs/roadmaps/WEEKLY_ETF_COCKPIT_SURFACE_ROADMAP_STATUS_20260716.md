# Weekly ETF Cockpit Surface Roadmap — Current Status

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`

## Historical completion

```text
WP01: merged in PR #52
WP02: merged in PR #52
WP03: merged in PR #53
WP04: merged in PR #54
WP05: merged in PR #55
WP06: merged in PR #56
WP07: merged in PR #57
```

## Stable decisions

```text
promotion_status: not_promoted
WP05 decision: not_promoted_needs_iteration
WP06 selected_path: iteration_path
production_report_change: none
delivery_change: none
```

## Current-runtime revalidation

```text
package: WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION
status: closed
PR: #74
validation_run: 29525968480
merge_commit: d80984b7336f343344719a80a29712506926bd26
```

The cockpit now uses current post-execution weights and market values and derives specific bilingual action wording from runtime state.

## WP08 evidence-based review

```text
package: WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
status: validated_ready_for_governance_closeout
PR: #76
validated_head: abe689064455dbd7206564037220e727c52b929b
validation_run: 29533073516
review_conclusion: iteration_required
promotion_status: not_promoted
```

WP08 replaced the static June review with a content-derived v2 review contract and structured bilingual HTML.

Passed dimensions:

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

Blocking dimensions:

```text
decision_clarity
bilingual_semantic_parity
premium_look_and_feel
```

## Next package

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
status: next_after_WP08_merge
promotion_status: not_promoted
```

WP09 must correct only the WP08 blockers and rerun the unchanged v2 review. It may not promote, attach, send or replace the cockpit in production.
