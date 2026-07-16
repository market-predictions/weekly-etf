# Handover — WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp08-evidence-side-by-side-review`
PR: #76
Status: implementation validated / governance closeout pending

## Claim status

No open WP08 or overlapping cockpit-review PR and no active cockpit branch existed at claim time.

## Current issue

The historical side-by-side builder was a static June template. It selected every report variant, did not inspect contents, repeated a provenance gap closed by WP07 and rendered escaped Markdown inside `<pre>`.

## Root cause

WP04 established a safe review lane but not a current-runtime evaluation contract. Later execution, provenance and report-freshness work made its static conclusions stale.

## Files changed

```text
runtime/build_cockpit_side_by_side_review.py
tests/test_cockpit_side_by_side_review.py
tests/test_cockpit_wp08_evidence_review.py
.github/workflows/validate-cockpit-wp08-evidence-review.yml
control/work_packages/WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260716.md
control/handovers/HANDOVER_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260716.md
```

## Implemented

```text
schema_version: cockpit_side_by_side_review_v2
review_type: evidence_based_side_by_side_preview_only
```

The review now:

- selects only the latest report sequence per language;
- selects the latest cockpit preview per language;
- reads runtime state and artifact contents;
- evaluates eleven dimensions;
- records evidence, required fixes and blocking status;
- hashes ten selected inputs;
- produces structured bilingual review HTML;
- emits a deterministic review conclusion and next package.

## Exact-current selected artifacts

```text
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html
output/runtime/etf_report_state_20260714_20260715_175910_executed.json
```

## Exact-current result

Passed:

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

Partial and blocking:

```text
decision_clarity
bilingual_semantic_parity
premium_look_and_feel
```

Evidence:

- executed URNM reduction and XBI addition are correct in both languages;
- pre/post weights and current NAV/return reconcile;
- WP07 provenance is present and therefore no longer a gap;
- the summary contradicts the completed activity;
- no dedicated next-action trigger is shown;
- the Dutch discipline sentence ends with a comma;
- Dutch provenance labels retain hybrid terminology.

## Review conclusion

```text
iteration_required
promotion_status: not_promoted
next_recommended_package: WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

## Validation evidence

```text
validated_head: abe689064455dbd7206564037220e727c52b929b
WP08_validation_run: 29533073516
WP08_validation_conclusion: success
current_runtime_validation_run: 29533073585
current_runtime_validation_conclusion: success
```

Workflow artifact:

```text
cockpit-wp08-evidence-review-29533073516
digest: sha256:a52ec091725dae17d992d940454cb11daa8dad1c6b7f585beec90f0473a473f0
```

The before/after protected SHA-256 lists are identical.

## What was not changed

```text
production report
portfolio state
trade ledger
valuation history
pricing authority
model execution
email delivery
promotion status
```

## Generated evidence paths

```text
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.json
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.md
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.html
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260714.md
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260714.html
```

These are workflow artifacts, not production delivery files.

## Next recommended package

```text
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT
```

WP09 should make only the narrow preview-copy and bilingual refinements identified by WP08, then rerun WP08 unchanged.

## Final closeout fields

```text
final_head_validation: pending after governance updates
merge_commit: pending
```
