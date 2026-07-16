# Work Package — WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp09-current-runtime-client-surface-refinement`
PR: #79

## Layer

```text
output contract
operational runbook
```

## Status

```text
implementation_status: closed
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
merge_commit: 9b679df825fdc4c7ce37cbdc2474acae6d25d67f
next_package: WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
```

## Purpose

Correct only the three client-surface dimensions blocked by the WP08 evidence review and rerun the unchanged WP08 v2 review model.

## Authority inputs

```text
output/runtime/latest_etf_report_state_path.txt
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/macro/latest.json
```

## Implemented changes

1. The short summary is action-aware:
   - executed actions produce controlled-rotation wording;
   - no-action runs retain disciplined inactivity wording.
2. A dedicated bilingual next-action trigger is derived from current concentration and review state.
3. Dutch discipline punctuation uses localized percentage formatting and a valid final period.
4. Dutch provenance labels use natural client-facing language.
5. Existing layout, cards, metrics, evidence strip, preview filenames and authority precedence remain intact.

## Operational gate correction

The WP08 workflow now enforces the state relationship rather than one fixed lifecycle conclusion:

```text
blocking findings present -> iteration_required
no blocking findings -> ready_for_promotion_decision
promotion_status -> not_promoted in both cases
```

The WP08 v2 dimensions, evidence model and review builder remain unchanged.

## Explicit non-goals

```text
no production promotion
no production report replacement
no email send
no model execution
no portfolio decision change
no pricing change
no state or ledger mutation
no report _04 rewrite
```

## Exact-current acceptance result

```text
schema_version: cockpit_side_by_side_review_v2
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
next_recommended_package: WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
```

All eleven dimensions pass:

```text
readability
density
visual_hierarchy
decision_clarity
executed_action_clarity
current_weight_accuracy
performance_risk_accuracy
trust_provenance_clarity
bilingual_semantic_parity
premium_look_and_feel
audit_evidence_preservation
```

## Validation and merge evidence

```text
final_validated_head: 739f80854456edc852baa167fcd849b98a56a4ff
WP08_validation_run: 29536333738
current_runtime_validation_run: 29536333731
validation_conclusion: success
PR: #79
merge_commit: 9b679df825fdc4c7ce37cbdc2474acae6d25d67f
artifact: cockpit-wp08-evidence-review-29535872134
artifact_digest: sha256:0a86df7071453783315c28bb60e9dd620c4eea4fbdf6f2f9fab9812a83fdb628
```

The artifact confirms ten hashed inputs, zero blockers and all eleven findings at `pass`.

## Safety result

```text
preview_output_only: output/cockpit_preview/
review_output_only: output/cockpit_review/
authority_file_mutation: false
delivery_change: false
email_send: false
portfolio_model_execution: false
promotion_status: not_promoted
```

## Next package

```text
WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
```

The next package must decide whether the cockpit remains an experiment, becomes an additive front page/attachment, or enters another iteration. WP09 itself did not promote the cockpit.
