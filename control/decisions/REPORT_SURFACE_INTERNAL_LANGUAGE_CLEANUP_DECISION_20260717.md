# Decision — Report-surface internal-language cleanup

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP`
Status: accepted

## Decision

Future English and Dutch client report surfaces must pass one shared deterministic internal-language contract before delivery.

Client-facing reports must describe the investment decision and evidence directly. They must not expose implementation-layer terms such as:

```text
shadow engine
runtime macro pack
rotation engine status
guarded model rotation
guarded auto-execution
release score
hold with override / aanhouden met override
override reason text
review-only / alleen ter review
runtime valuation
model/action weights
churn budget / discipline gates
run(s)
```

## Chosen output contract

1. `runtime/report_surface_language_contract.py` is the canonical bilingual phrase-normalization and forbidden-term contract.
2. The existing pre-send cleanup path applies that contract to Markdown and HTML.
3. The existing client-surface clean gate fails when forbidden implementation language remains.
4. The supplementary deterministic regime comparison is written at source as a client-safe cross-check.
5. The deterministic regime payload retains all explicit false-authority fields.
6. Numeric tokens, percentages, ticker links and portfolio decisions may not change during wording cleanup.
7. Historical reports remain immutable; representative historical reports may be replayed only in memory or into separate validation previews.

## Authority consequence

```text
client_language_authority: output_contract_only
portfolio_action_authority_change: false
pricing_authority_change: false
macro_thesis_authority_promotion: false
lane_scoring_change: false
fundability_change: false
portfolio_execution_change: false
historical_output_mutation: false
delivery_authority: false
```

This decision improves how existing authority is expressed. It does not create new analytical, portfolio, pricing, scoring, execution or delivery authority.

## Validation basis

```text
workflow_run: 29590932038
workflow_job: 87919550815
focused_tests: 30 passed
representative_report_token: 260716
EN findings: 18 -> 0
NL findings: 6 -> 0
EN numeric tokens preserved: 635
NL numeric tokens preserved: 588
EN markdown links preserved: 234
NL markdown links preserved: 236
historical report hashes: identical before/after
email_sent: false
```

Persistent evidence:

```text
control/evidence/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_EVIDENCE_20260717.json
```

## Operational consequence

The next fresh production run will use this contract automatically through the existing cleanup and pre-send validation sequence. A fresh report and email still require a separate explicit production request and real delivery evidence.
