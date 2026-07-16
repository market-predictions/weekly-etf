# Handover — WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp08-evidence-side-by-side-review`
Status: claimed / implementation in progress

## Claim status

No open WP08 or overlapping cockpit-review pull request was found. No active cockpit branch was found at claim time.

## Current issue

The current side-by-side builder is a static June review template. It does not compare the selected artifacts, selects every report variant for the token and repeats a provenance gap that WP07 already closed.

## Baseline evidence

Workflow artifact from current-runtime validation run `29525968480` showed:

```text
classic_report_sources: 16 mixed historical/current variants
cockpit_preview_sources: 2 current bilingual previews
schema_version: cockpit_side_by_side_review_v1
review_conclusion: absent
content-derived findings: absent
```

The current cockpit surface also shows:

```text
EN summary: We keep discipline ahead of activity this week ... URNM reduced · XBI added.
NL discipline sentence: ends with a comma
next-action trigger: not presented as a dedicated review item
```

## Safety boundary

```text
promotion_status: not_promoted
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
review_output_only: output/cockpit_review/
```

## Implementation target

Replace the static review with an evidence-derived v2 contract, deterministic current artifact selection, structured findings and client-grade HTML. Record the resulting blocking findings and recommend the next narrow package.

## Completion evidence

Pending code, tests, current-artifact workflow validation, PR and merge evidence.
