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
final_validated_head: 523bb038db9ccc10c009b88e6c8f6dd489bc7dc5
validation_run: 29525968480
merge_commit: d80984b7336f343344719a80a29712506926bd26
```

The cockpit now uses current post-execution weights and market values before previous or inherited values and derives specific bilingual action wording from runtime state.

## Next package

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
status: next
promotion_status: not_promoted
```

WP08 is review-only. It must compare the current July 14 classic report with the corrected current-runtime cockpit and may not promote or attach the cockpit without a subsequent explicit decision.
