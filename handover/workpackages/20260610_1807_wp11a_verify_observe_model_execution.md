# Handover — WP11A-VERIFY-OBSERVE model execution failure visibility

## Repository worked on

```text
market-predictions/weekly-etf
```

## Workpackage title

```text
WP11A-VERIFY-OBSERVE — Make model-execution policy failures visible in CI logs
```

## Status

```text
observability-fix-committed / retry-request-prepared / awaiting-workflow-evidence
```

## Context

The WP11A-VERIFY retry passed the previously failing Dutch GLD/client-language surface and reached further into the report-build step.

Observed successful markers from the failing run:

```text
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_NL_DATE_LOCALIZATION_OK
ETF_LINKIFY_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

The next failure likely occurred inside:

```bash
python -m runtime.model_execution_engine \
  --runtime-state "$runtime_state_path" \
  --portfolio-state output/etf_portfolio_state.json \
  --trade-ledger output/etf_trade_ledger.csv \
  --mode shadow \
  --output-dir output/runtime
```

Because the workflow captures stdout in `execution_log="$(...)"`, the exact blocked policy/input error was not visible before the step exited.

## Files changed

```text
runtime/model_execution_engine.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
handover/workpackages/20260610_1807_wp11a_verify_observe_model_execution.md
```

The final trigger commit in this sequence is expected to add:

```text
control/run_queue/weekly_etf_report_request_20260610_180729_wp11a_verify_observe.md
```

## Implementation

Updated `runtime/model_execution_engine.py` so blocked model-execution policy failures still print to stdout and also print the same message to stderr before exiting.

Implemented behavior:

```python
message = "ETF_MODEL_EXECUTION_BLOCKED | artifact=" + artifact["artifact_path"] + " | errors=" + ";".join(artifact["policy_checks"]["errors"])
print(message)
print(message, file=sys.stderr)
raise SystemExit(1)
```

This preserves the existing failure behavior and makes the hidden policy/input error visible in GitHub Actions logs.

## Commits

```text
887722cc638778ee44809b6556aa54c7ca72f569 — Expose model execution policy failures on stderr
3b9e1556cea12d1a72a142152491f828b0ac778c — Record WP11A observe status before retry
```

The run-queue retry is intentionally created as the final commit after this handover to avoid advancing `main` while the workflow is running.

## Whether rerun was triggered

Prepared here; the run is triggered by the final run-queue file commit:

```text
control/run_queue/weekly_etf_report_request_20260610_180729_wp11a_verify_observe.md
```

## Workflow result

Not available at handover creation time.

## Visible model-execution error if still failing

Not available yet. The expected log line is:

```text
ETF_MODEL_EXECUTION_BLOCKED | artifact=... | errors=...
```

## Authority boundaries preserved

No policy/scoring/trading authority was changed.

Preserved boundaries:

```text
replacement-edge notes remain diagnostic_only=true
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
production_recommendation_authority=false
execution_authority=false
portfolio_mutation=false
```

No pricing, lane scoring, fundability, recommendation, target-weight, trade-intent, execution, or portfolio-state mutation logic was changed.

## Remaining work

```text
inspect the observe retry workflow result
if failing, capture the visible ETF_MODEL_EXECUTION_BLOCKED errors line
if passing, confirm fresh English/Dutch reports contain ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
confirm report content validator result
close WP11A-VERIFY with final evidence
```
