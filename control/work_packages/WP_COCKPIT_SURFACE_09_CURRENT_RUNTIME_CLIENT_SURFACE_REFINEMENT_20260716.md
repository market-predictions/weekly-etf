# Work Package — WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp09-current-runtime-client-surface-refinement`

## Layer

```text
output contract
operational runbook
```

## Status

```text
claimed
promotion_status: not_promoted
```

## Purpose

Correct only the three client-surface dimensions blocked by the WP08 evidence review and rerun the unchanged WP08 v2 contract.

## Authority inputs

```text
output/runtime/latest_etf_report_state_path.txt
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/macro/latest.json
```

## Required changes

1. Make the short summary action-aware.
2. Add a concise bilingual next-action trigger derived from current authority and existing discipline rules.
3. Fix the Dutch discipline punctuation defect.
4. Replace hybrid Dutch provenance labels with natural Dutch client-facing wording.
5. Preserve the existing cockpit layout, metrics, evidence strip, preview filenames and authority precedence.

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

## Acceptance

Run the unchanged WP08 v2 review against exact July 14 artifacts. Required result:

```text
review_conclusion: ready_for_promotion_decision
blocking_findings: []
promotion_status: not_promoted
```

This result means the preview is ready for a separate promotion decision. It does not promote the cockpit.

## Safety boundary

```text
preview_output_only: output/cockpit_preview/
review_output_only: output/cockpit_review/
authority_file_mutation: false
delivery_change: false
```
