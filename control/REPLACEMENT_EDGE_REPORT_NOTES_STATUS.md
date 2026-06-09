# Replacement-edge report notes status

## Workpackage

```text
WP11A — Integrate WP5 replacement-edge diagnostics into report notes, non-authoritative
```

## Repository

```text
market-predictions/weekly-etf
```

## Status

```text
status: started / helper-and-tests-added / not-yet-wired-into-production-render
```

## Purpose

WP5 added direct challenger-vs-current-holding replacement-edge diagnostics. WP11A starts the safe client-surface integration path by rendering those diagnostics as clearly non-authoritative report notes.

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

## Files added

```text
runtime/replacement_edge_report_notes.py
tests/test_replacement_edge_report_notes.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
```

## Implementation summary

The new helper:

```text
runtime/replacement_edge_report_notes.py
```

- builds a notes payload from the existing WP5 replacement-edge artifact builder
- renders English and Dutch markdown tables
- embeds a stable marker:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

- explicitly states that the notes do not create allocation, fundability, scoring, recommendation or execution authority
- preserves the existing WP5 diagnostic-only boundary

## Test coverage added

```text
tests/test_replacement_edge_report_notes.py
```

The tests assert:

- English output includes the diagnostic-only marker and authority disclaimer
- Dutch output includes the diagnostic-only marker and authority disclaimer
- empty diagnostics render a safe fallback rather than implying a signal

## Not done yet

The helper is not yet wired into:

```text
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/delivery_html_overrides.py
.github/workflows/send-weekly-report.yml
```

Reason: an attempted large overwrite of the existing render module was blocked by the connector/safety layer. To avoid risking production output, WP11A was narrowed to a safe helper/test/status increment first.

## Next safe step

A follow-up worker should integrate the helper in a small patch:

1. import `replacement_edge_notes_markdown`
2. insert the note block immediately below the existing Replacement Duel Table / Vervangingsanalyse section
3. optionally add an output-contract validator that checks the marker and diagnostic-only disclaimer
4. only then wire it into the workflow if needed

## Validation evidence available in repo

```text
helper added: runtime/replacement_edge_report_notes.py
tests added: tests/test_replacement_edge_report_notes.py
```

Local or CI execution still needs to confirm:

```text
python -m pytest tests/test_replacement_edge_report_notes.py -q
```
