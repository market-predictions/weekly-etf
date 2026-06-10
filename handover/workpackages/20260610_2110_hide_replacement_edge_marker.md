# WP11A-MARKER-HIDE — Hide replacement-edge marker from client reports

## Status

```text
implemented / retry requested
```

## Files changed

```text
tools/validate_etf_report_content_contract.py
tests/test_replacement_edge_report_notes.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
control/run_queue/weekly_etf_report_request_20260610_2110_hide_replacement_edge_marker.md
handover/workpackages/20260610_2110_hide_replacement_edge_marker.md
```

## What changed

- The report content contract now treats `ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED`, its Markdown comment form, and its HTML-escaped form as forbidden client-surface text.
- Replacement-edge diagnostic notes are still required through the English diagnostic-only authority disclaimer and authority-boundary terms.
- Tests now assert that the marker is absent from direct note rendering, English/Dutch polish insertion, and the output-contract action snapshot.
- Documentation now records that the marker must not appear in client-facing Markdown, HTML, or PDF output.

## Validation

```text
PYTHONPATH=/tmp/stub-yaml-marker:$PWD direct replacement-edge report note tests: OK
replacement-edge no-marker smoke test: OK
```

`pytest` was not available in the local runtime, so the test functions were executed directly.

## Authority confirmation

No policy, scoring, fundability, recommendation, target-weight, execution, trade-ledger, or portfolio-mutation behavior was changed.

The replacement-edge notes remain diagnostic-only.

## Retry

Created run-queue request:

```text
control/run_queue/weekly_etf_report_request_20260610_2110_hide_replacement_edge_marker.md
```

Expected output validation:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED absent from Markdown/HTML/PDF
diagnostic-only authority disclaimer still present
```
