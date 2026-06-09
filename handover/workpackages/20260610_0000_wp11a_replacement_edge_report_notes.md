# Handover — WP11A replacement-edge report notes

## Repository

```text
market-predictions/weekly-etf
```

## Workpackage

```text
WP11A — Integrate WP5 replacement-edge diagnostics into report notes, non-authoritative
```

## Status

```text
started / helper-and-tests-added / production-render-not-yet-wired
```

## What was done

Added a safe helper layer for rendering WP5 direct challenger-vs-current-holding replacement-edge diagnostics as report notes.

Added:

```text
runtime/replacement_edge_report_notes.py
tests/test_replacement_edge_report_notes.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
handover/workpackages/20260610_0000_wp11a_replacement_edge_report_notes.md
```

## Commits

```text
9f43a5cdc619d0ca6f3d8c081a71bdded8b7b49c — Add replacement-edge report notes helper
f8cae7ec9d7d8944ab15b4b209fedc4f91821917 — Test replacement-edge report notes helper
defbd114bb83cea7678d01f1fc82130f2a2b30ad — Record replacement-edge report notes status
```

## Authority boundary preserved

The helper and tests keep the WP5 boundary explicit:

```text
diagnostic_only=true
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
portfolio_mutation=false
production_recommendation_authority=false
execution_authority=false
```

## Helper behavior

`runtime/replacement_edge_report_notes.py`:

- builds a notes payload from the existing WP5 `build_replacement_edge_artifact` path
- renders English and Dutch markdown
- includes marker:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

- includes a clear diagnostic-only disclaimer
- has a safe empty-state fallback

## Test behavior

`tests/test_replacement_edge_report_notes.py` asserts:

- English output includes the marker and non-authority language
- Dutch output includes the marker and non-authority language
- empty diagnostics render a safe fallback

## Not completed

The helper is not yet wired into:

```text
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/delivery_html_overrides.py
.github/workflows/send-weekly-report.yml
```

Reason: an attempted large overwrite of the existing replacement-duel render module was blocked by the connector/safety layer. To avoid risky production-output mutation, the package was narrowed to a safe helper/test/status increment.

## Next recommended step

Create a small follow-up patch that:

1. imports `replacement_edge_notes_markdown`
2. inserts it below the existing Replacement Duel Table / Vervangingsanalyse block
3. adds or extends a validator to require the marker and diagnostic-only disclaimer
4. only then wires the render/report path if the validator passes

## Validation still required

Run:

```bash
python -m pytest tests/test_replacement_edge_report_notes.py -q
```

No test run has been confirmed yet in this chat.
