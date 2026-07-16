# Work Package — WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`

## Layer

```text
decision framework
output contract
operational runbook
```

## Status

```text
implementation_status: closed
review_conclusion: iteration_required
promotion_status: not_promoted
PR: #76
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
next_package: WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

## Purpose and result

WP08 converted the historical static June side-by-side review into a deterministic evidence-based current-runtime review.

```text
schema_version: cockpit_side_by_side_review_v2
review_type: evidence_based_side_by_side_preview_only
```

The builder now selects one current classic baseline and one latest cockpit preview per language, evaluates eleven dimensions from runtime state and artifact contents, records input SHA-256 identities and produces structured bilingual HTML.

## Exact-current findings

```text
readability: pass
density: pass
visual_hierarchy: pass
decision_clarity: partial / blocking
executed_action_clarity: pass
current_weight_accuracy: pass
performance_risk_accuracy: pass
trust_provenance_clarity: pass
bilingual_semantic_parity: partial / blocking
premium_look_and_feel: partial / blocking
audit_evidence_preservation: pass
```

Blocking evidence:

1. The summary says discipline is ahead of activity although URNM was reduced and XBI was added.
2. The cockpit lacks a dedicated next-action trigger present in the classic decision cockpit.
3. The Dutch discipline sentence ends with a comma.
4. Dutch provenance labels contain hybrid English terminology.

The current action, weight, performance, provenance and audit surfaces passed.

## Selected sources

```text
Classic EN: output/weekly_analysis_pro_260714_04.md
Classic EN HTML: output/weekly_analysis_pro_260714_04_delivery.html
Classic NL: output/weekly_analysis_pro_nl_260714_04.md
Classic NL HTML: output/weekly_analysis_pro_nl_260714_04_delivery.html
Cockpit EN: output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html
Cockpit NL: output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html
```

## Validation and merge evidence

```text
final_validated_head: 830f79c09cbb170f748f840647ddccfe78d3c68c
WP08_validation_run: 29533435789
current_runtime_validation_run: 29533435716
validation_conclusion: success
PR: #76
merge_commit: 4a8c1a81aa8bca7324969f59f8134cb6db1def8e
artifact: cockpit-wp08-evidence-review-29533073516
artifact_digest: sha256:a52ec091725dae17d992d940454cb11daa8dad1c6b7f585beec90f0473a473f0
```

Compilation, regressions, production validators, exact-current assertions and protected-file hash comparisons passed.

## Boundary

```text
review_output: output/cockpit_review/
promotion_status: not_promoted
email_send: false
portfolio_model_execution: false
authority_file_mutation: false
delivery_change: false
```

## Next package

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

WP09 must correct only the three blocking review dimensions and rerun WP08 v2 unchanged. Passing that review still requires a separate promotion decision.
