# Replacement-edge report notes status

## Workpackage

```text
WP11A-VERIFY / WP11A-VERIFY-OBSERVE — Validate replacement-edge diagnostic notes and expose model-execution policy failures
```

## Repository

```text
market-predictions/weekly-etf
```

## Status

```text
status: observability-fix-committed / retry-request-prepared / awaiting-workflow-evidence
```

## Purpose

WP5 added direct challenger-vs-current-holding replacement-edge diagnostics. WP11A created the safe helper and tests. WP11A-FIX wired those diagnostics into the report-output path as clearly non-authoritative notes. WP11A-VERIFY requests and tracks validation evidence for that report-output contract.

WP11A-VERIFY reached the report-build step and passed the Dutch client-language scrub, date localization, ticker linkification, and macro-thesis surface leakage validation. The remaining blocker was hidden because `runtime.model_execution_engine` output was captured by the workflow before the failing exit code stopped the step.

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

A later retry after a Dutch GLD surface fix reached further into the report-build step and showed:

```text
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_NL_DATE_LOCALIZATION_OK
ETF_LINKIFY_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

The next failure appeared to be inside model execution, but the precise `ETF_MODEL_EXECUTION_BLOCKED` policy error was hidden by workflow stdout capture.

## WP11A-VERIFY-OBSERVE action taken

Committed observability-only stderr output in:

```text
runtime/model_execution_engine.py
```

Commit:

```text
887722cc638778ee44809b6556aa54c7ca72f569 — Expose model execution policy failures on stderr
```

Change summary:

- added `import sys`
- preserved the existing blocked exit behavior
- preserved the existing stdout message
- additionally prints the same `ETF_MODEL_EXECUTION_BLOCKED` line to stderr before `SystemExit(1)`

No policy rule was relaxed. No pricing, lane scoring, fundability, recommendation, target-weight, trade-intent, execution, or portfolio-state mutation logic was changed.

## Prepared retry request

A new retry request is prepared as the final trigger commit for this sequence:

```text
control/run_queue/weekly_etf_report_request_20260610_180729_wp11a_verify_observe.md
```

Purpose:

```text
Retry WP11A-VERIFY after model-execution observability fix.
```

## Validation evidence status

WP11A-VERIFY is not yet closed.

The next workflow run should now expose the exact model-execution policy/input error if the step still fails, for example:

```text
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=source_not_in_portfolio:...
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=trade_price_invalid:...
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=trade_below_min_size_after_source_cap:...
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=source_has_no_executable_value:...
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=major_rotation_count_exceeds_policy:...
```

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

Model-execution observability should prove:

```text
failed shadow model-execution policy checks are visible in GitHub Actions logs
```

## Remaining work

```text
inspect GitHub Actions workflow result for the observe retry
if failing, capture the visible ETF_MODEL_EXECUTION_BLOCKED errors line
confirm latest fresh English report path
confirm latest fresh Dutch report path
confirm marker in both reports
confirm content validator result
record completed verification status in CURRENT_STATE, NEXT_ACTIONS, ETF_SESSION_CHANGELOG and a follow-up closeout handover
```
