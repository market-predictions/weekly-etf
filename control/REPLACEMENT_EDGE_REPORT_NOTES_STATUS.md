# Replacement-edge report notes status

## Workpackage

```text
WP11A-FIX — Wire replacement-edge diagnostic notes into report render path
```

## Repository

```text
market-predictions/weekly-etf
```

## Status

```text
status: completed / render-path-wired / validator-added / awaiting CI confirmation
```

## Purpose

WP5 added direct challenger-vs-current-holding replacement-edge diagnostics. WP11A created the safe helper and tests. WP11A-FIX wires those diagnostics into the report-output path as clearly non-authoritative notes.

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

## Files changed

```text
runtime/replacement_edge_report_notes.py
runtime/polish_runtime_reports.py
tests/test_replacement_edge_report_notes.py
tools/validate_etf_report_content_contract.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
```

## Implementation summary

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

now requires the English rendered report to contain:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

and the English diagnostic-only authority disclaimer.

## Test coverage updated

```text
tests/test_replacement_edge_report_notes.py
```

The tests assert:

- English output includes the diagnostic-only marker and full authority disclaimer
- Dutch output includes the diagnostic-only marker and full authority disclaimer
- empty diagnostics render a safe fallback rather than implying a signal
- English polish output inserts the notes below the replacement-duel section
- Dutch polish output inserts the notes below the vervangingsanalyse section
- diagnostic payload fields remain non-authoritative

## Commits

```text
11c9a00a57204fb226f077b52c18377d6f7fa04a — Clarify replacement-edge diagnostic authority boundary
4ee42122aca1ceaccf7ba9a5eda3506ef637f3c4 — Wire replacement-edge diagnostic notes into runtime polish
3ca18c9adee77c148291a2b1cfbaa6513c0735c1 — Test replacement-edge notes render integration
d6b8cee7a5b4eb99d536a0bae199bd639edd3459 — Validate replacement-edge diagnostic report notes
```

## Validation still required

The required focused tests should be run by CI or a local worker:

```bash
python -m pytest tests/test_replacement_edge_report_notes.py -q
```

A fresh workflow/report run should also confirm that the updated content validator passes against the newly polished English report.

## Remaining work

No further WP11A-FIX implementation work is currently known.

The remaining open item is validation evidence:

```text
run focused pytest
run fresh report/content validator
record resulting workflow/test status in CURRENT_STATE and ETF_SESSION_CHANGELOG
```
