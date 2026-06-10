# Handover — WP11A-POLICY-CAP model execution source-reduction cap

## Repository worked on

```text
market-predictions/weekly-etf
```

## Workpackage title

```text
WP11A-POLICY-CAP — Cap model execution source reductions to existing policy limit
```

## Status

```text
policy-cap-fix-committed / retry-request-prepared / awaiting-workflow-evidence
```

## Context

The WP11A-VERIFY-OBSERVE retry made the hidden model-execution error visible.

The actual blocker was:

```text
ETF_MODEL_EXECUTION_BLOCKED | artifact=output/runtime/etf_model_execution_20260609_20260610_181023.json | errors=source_reduction_exceeds_policy:SPY:5.23>5.00
```

Interpretation:

```text
The rotation intent requested a 5.23% SPY source reduction while the existing max_single_source_reduction_pct_nav policy cap is 5.00%.
```

The user explicitly approved changing execution behavior so the model execution engine enforces the existing cap instead of blocking above it.

## Files changed

```text
runtime/model_execution_engine.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
handover/workpackages/20260610_1901_wp11a_policy_cap_model_execution.md
```

The final trigger commit in this sequence is expected to add:

```text
control/run_queue/weekly_etf_report_request_20260610_190101_wp11a_policy_cap_retry.md
```

## Implementation

Updated `runtime/model_execution_engine.py`:

- `_execution_notional` now reads `max_single_source_reduction_pct_nav` from the existing runtime rotation policy.
- Executable notional is capped to the minimum of:
  - requested notional
  - available source value
  - existing source-reduction policy cap
- Policy cap events are recorded as warnings with cap reason `policy`.
- Proposed ledger rows include:
  - `notional_capped`
  - `notional_capped_to_source_value`
  - `notional_cap_reason`

Expected warning shape:

```text
source_notional_capped_to_policy:SPY:5555.27->5312.32
```

## Commits

```text
951a72c4492cfc72ab46289def755606d35a309c — Cap model execution source reductions to policy
222e089403597de571531ce512b50fa9812e5cc0 — Record WP11A policy-cap fix before retry
```

The run-queue retry is intentionally created as the final commit after this handover to avoid advancing `main` while the workflow is running.

## Local validation

Syntax check:

```text
python -m py_compile runtime/model_execution_engine.py
```

Result:

```text
passed
```

Local reproduction against the failing runtime state:

```bash
python -m runtime.model_execution_engine \
  --runtime-state output/runtime/etf_report_state_20260609_20260610_181023.json \
  --portfolio-state output/etf_portfolio_state.json \
  --trade-ledger output/etf_trade_ledger.csv \
  --mode shadow \
  --output-dir /tmp/weekly-etf-model-exec-test-2
```

Result:

```text
ETF_MODEL_EXECUTION_OK | artifact=/tmp/weekly-etf-model-exec-test-2/etf_model_execution_20260609_20260610_181023.json | mode=shadow | trades=1 | status=shadow_ready
```

Artifact evidence:

```text
policy_checks.passed=true
policy_checks.errors=[]
policy_checks.warnings=['source_notional_capped_to_policy:SPY:5555.27->5312.32']
source_delta_weight_pct=-5.0
destination_delta_weight_pct=5.0
notional_capped=true
notional_capped_to_source_value=false
notional_cap_reason=policy
```

## Authority boundaries

This is an execution behavior change, explicitly approved by the user, but it is not a policy relaxation.

Preserved boundaries:

```text
max_single_source_reduction_pct_nav remains the controlling policy value
replacement-edge notes remain diagnostic_only=true
portfolio_action_authority=false for replacement-edge notes
fundability_authority=false for replacement-edge notes
lane_scoring_authority=false for replacement-edge notes
funding_authority=false for replacement-edge notes
production_recommendation_authority=false for replacement-edge notes
```

## Whether rerun was triggered

Prepared here; the run is triggered by the final run-queue file commit:

```text
control/run_queue/weekly_etf_report_request_20260610_190101_wp11a_policy_cap_retry.md
```

## Workflow result

Not available at handover creation time.

## Remaining work

```text
inspect the policy-cap retry workflow result
confirm shadow model execution passes or captures the next visible blocker
confirm latest fresh English/Dutch reports contain ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
confirm report content validator result
close WP11A-VERIFY with final evidence
```
