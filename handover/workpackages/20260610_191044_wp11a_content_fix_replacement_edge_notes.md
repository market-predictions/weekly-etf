# WP11A-CONTENT-FIX — Preserve replacement-edge notes through output contract fix

## Context

The WP11A policy-cap retry reached the content-contract validation step. Model execution was no longer blocked by `source_reduction_exceeds_policy`.

The new failure was:

```text
ETF content contract failed for weekly_analysis_pro_260609_04.md: replacement-edge diagnostic notes missing/incomplete: ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED, Diagnostic-only: these notes grant no allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority or portfolio mutation authority., allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority, portfolio mutation authority
```

## Root Cause

`runtime.polish_runtime_reports` inserted replacement-edge diagnostic notes before `runtime.fix_report_output_contract`.

`runtime.fix_report_output_contract` then rebuilt the English replacement/action surface and omitted the diagnostic notes from the replacement pricing/duel block. The Dutch native report was skipped by this fixer and retained the marker.

## Files Changed

```text
runtime/fix_report_output_contract.py
tests/test_replacement_edge_report_notes.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
handover/workpackages/20260610_191044_wp11a_content_fix_replacement_edge_notes.md
control/run_queue/weekly_etf_report_request_20260610_191044_wp11a_content_fix_retry.md
```

## Code/Test Commits

```text
eb312232d86e2f9ffac5133695b2cf69f71ea64f — Preserve replacement-edge notes in output contract fix
0229ede09541aa9b61b6ff8136d7610a426853b1 — Test output contract replacement-edge notes
```

## Implementation

- Added replacement-edge diagnostic-note construction to `runtime.fix_report_output_contract`.
- Appended the notes to the English replacement pricing/duel block produced by `action_snapshot_section`.
- Added a regression test proving the output-contract fixer emits:
  - `ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED`
  - the English diagnostic-only authority disclaimer

## Local Validation

Focused smoke test:

```text
SMOKE_OK replacement edge notes survive output-contract fix
```

Validation against the failed fresh output after applying the fixer:

```text
ETF_OUTPUT_CONTRACT_FIX_PATCHED | report=weekly_analysis_pro_260609_04.md | rotation_plan=True
ETF_OUTPUT_CONTRACT_FIX_SKIPPED | report=weekly_analysis_pro_nl_260609_04.md | reason=native_dutch_renderer
ETF_OUTPUT_CONTRACT_FIX_OK
ETF_REPORT_CONTENT_CONTRACT_OK | report=weekly_analysis_pro_260609_04.md
```

Note: the local container lacked optional render/test packages (`pytest`, `matplotlib`, PyYAML), so the focused validator run used temporary import stubs for unused PDF/render imports. The GitHub Actions workflow installs its normal dependencies.

## Authority Boundary Confirmation

No policy, scoring, fundability, ranking, recommendation, target-weight, execution or portfolio-mutation logic was changed.

The replacement-edge report notes remain diagnostic-only and non-authoritative.

## Retry

Run queue request prepared:

```text
control/run_queue/weekly_etf_report_request_20260610_191044_wp11a_content_fix_retry.md
```

Expected validation:

```text
English report contains ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
English report contains Diagnostic-only authority disclaimer
Dutch report retains ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
python tools/validate_etf_report_content_contract.py --output-dir output passes in CI
```
