# Replacement-edge report notes status

## Workpackage

```text
WP11A-VERIFY — Validate replacement-edge diagnostic notes in CI/fresh report output
```

## Repository

```text
market-predictions/weekly-etf
```

## Status

```text
status: validation-requested / fresh-report-run-queued / awaiting-workflow-evidence
```

## Purpose

WP5 added direct challenger-vs-current-holding replacement-edge diagnostics. WP11A created the safe helper and tests. WP11A-FIX wired those diagnostics into the report-output path as clearly non-authoritative notes. WP11A-VERIFY requests and tracks validation evidence for that report-output contract.

## Authority boundary

Replacement-edge report notes remain diagnostic-only.

They do not grant:

```text
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
portfolio_mutation=false
production_recommendation_authority=false
execution_authority=false
```

The notes must not influence ranking, fundability, recommendation, target weights, trade intents, execution, or portfolio mutation.

## Files changed by WP11A-FIX

```text
runtime/replacement_edge_report_notes.py
runtime/polish_runtime_reports.py
tests/test_replacement_edge_report_notes.py
tools/validate_etf_report_content_contract.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
```

## WP11A-FIX implementation summary

The helper:

```text
runtime/replacement_edge_report_notes.py
```

- builds a notes payload from the existing WP5 replacement-edge artifact builder
- renders English and Dutch markdown tables
- embeds a stable marker:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

- explicitly states that the notes do not create allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority, or portfolio mutation authority
- preserves the existing WP5 diagnostic-only boundary

The runtime polish layer:

```text
runtime/polish_runtime_reports.py
```

- injects the replacement-edge notes after the final Replacement Duel / Vervangingsanalyse section
- applies the insertion to both English and Dutch report text
- uses a safe empty-state fallback when a lane-assessment source cannot be resolved
- does not alter pricing, lane scoring, rotation, trade-intent, execution, or portfolio-state logic

The content validator:

```text
tools/validate_etf_report_content_contract.py
```

requires the English rendered report to contain:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

and the English diagnostic-only authority disclaimer.

## WP11A-VERIFY action taken

Created validation run-queue request:

```text
control/run_queue/weekly_etf_report_request_20260610_0015_wp11a_verify.md
```

Commit:

```text
31328c2e5d2a2c16c642914f1538808fe56f77ac — Request WP11A-VERIFY fresh report validation run
```

## Validation evidence status

At the time this file was updated, the GitHub connector returned no workflow-run metadata for commit:

```text
31328c2e5d2a2c16c642914f1538808fe56f77ac
```

So WP11A-VERIFY is not yet closed.

## Required validation evidence still needed

Focused test:

```bash
python -m pytest tests/test_replacement_edge_report_notes.py -q
```

Fresh report/content validation should prove:

```text
English report contains ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
Dutch report contains ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
python tools/validate_etf_report_content_contract.py --output-dir output passes
```

## Remaining work

```text
wait for / inspect GitHub Actions workflow result
confirm latest fresh English report path
confirm latest fresh Dutch report path
confirm marker in both reports
confirm content validator result
record completed verification status in CURRENT_STATE, NEXT_ACTIONS, ETF_SESSION_CHANGELOG and a follow-up handover
```
