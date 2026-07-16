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

## WP08 evidence-based review

```text
package: WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
status: closed
PR: #76
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
validation_run: 29533435789
initial_review_conclusion: iteration_required
promotion_status: not_promoted
```

WP08 replaced the static June review with a content-derived v2 review contract and structured bilingual HTML.

## WP09 current-runtime client-surface refinement

```text
package: WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
status: validated_ready_for_governance_closeout
PR: #79
validated_head: d4e6fa7aae9dab98000716b0ecf24f45d9a7b04a
WP08_validation_run: 29535872134
current_runtime_validation_run: 29535872250
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
```

All eleven evidence-review dimensions pass after the narrow summary, next-trigger, Dutch punctuation and provenance-label refinements.

## Next package

```text
WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
status: next_after_WP09_merge
promotion_status: not_promoted
```

This package must select the cockpit's production relationship but may not itself change production rendering or delivery behavior.
