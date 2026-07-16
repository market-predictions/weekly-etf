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

## Stable boundary

```text
promotion_status: not_promoted
classic_report_evidence_layer: preserved
production_delivery_contract: unchanged
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

WP08 introduced the evidence-based v2 review contract.

## WP09 current-runtime client-surface refinement

```text
package: WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
status: closed
PR: #79
merge_commit: 9b679df825fdc4c7ce37cbdc2474acae6d25d67f
closeout_PR: #80
closeout_merge_commit: 009e0f1a910c44b43de0d6c5babf3b1e0eae5cfd
final_validation_run: 29536333738
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
```

All eleven evidence-review dimensions pass.

## Cockpit production-relationship decision

```text
package: WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
status: decision_recorded_validation_pending
selected_option: additive_delivery_front_page
production_change_in_decision_package: false
promotion_status: not_promoted
```

Selected route:

```text
one additive cockpit front page inside the existing EN/NL HTML and PDF
complete classic report body preserved
one email body and one PDF per language preserved
attachment and manifest contracts unchanged
feature-gated implementation
default disabled
fail closed to classic output
```

Rejected at this stage:

```text
separate attachment
full report replacement
another refinement cycle
remaining preview-only as the primary route
```

## Next package

```text
WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
status: next_after_decision_merge
promotion_status: not_promoted
```

WP10 may implement the feature-gated integration but may not enable it by default or send email. A separate implementation-promotion closeout is required before actual production enablement.
