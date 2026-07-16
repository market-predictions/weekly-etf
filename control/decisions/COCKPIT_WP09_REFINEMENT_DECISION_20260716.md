# Decision — WP09 current-runtime client-surface refinement

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Status: accepted for preview lane

## Decision

The refined cockpit has passed the full WP08 v2 evidence review and is ready for a separate promotion decision.

```text
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
```

This is not a production promotion decision.

## Accepted refinements

1. Action-aware summary wording.
2. Dedicated bilingual next-action trigger.
3. Correct Dutch discipline punctuation.
4. Natural Dutch provenance labels.
5. Preserved current-runtime authority, design and preview-only output boundary.

## Evidence

```text
PR: #79
validated_head: d4e6fa7aae9dab98000716b0ecf24f45d9a7b04a
WP08_validation_run: 29535872134
current_runtime_validation_run: 29535872250
artifact: cockpit-wp08-evidence-review-29535872134
artifact_digest: sha256:0a86df7071453783315c28bb60e9dd620c4eea4fbdf6f2f9fab9812a83fdb628
```

All eleven review dimensions passed and protected authority hashes were unchanged.

## Next package

```text
WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW
```

That package must choose explicitly among:

```text
remain preview-only experiment
additive front page or attachment
another iteration
production replacement path
```

No option is authorized by this decision. Any production or delivery change requires its own explicit contract and evidence.
