# Handover — Rotation State Authority and Alternative Candidates

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-current-run-rotation-authority`
PR: #58

## Current issue

The 2026-07-14 report correctly refreshed prices and relative strength but produced no mutation because rotation still consumed stale scorecard P/L and recommendation memory. Alternatives were not independently selectable, and several accumulated holdings lacked persisted average entry.

## Root cause

- current valuation and rotation authority were separated;
- P/L could remain inherited from May despite current July prices;
- acquisition prices existed in model-execution artifacts but were not reconstructed;
- alternative ETFs remained descriptive metadata;
- capped candidate scores could be resolved alphabetically.

## Implemented resolution

- `runtime/rotation_state_authority.py` builds current-run valuation authority and refreshes the scorecard;
- missing average entry is reconstructed from `output/etf_trade_ledger.csv` and referenced `output/runtime/etf_model_execution_*.json` artifacts;
- unresolved average-entry authority blocks rotation;
- `runtime/portfolio_rotation_engine_v2.py` scores primary and alternative ETFs independently;
- replacement-only alternatives require a direct 3-month edge of at least 10%;
- general destinations require a failed or sufficiently aged impaired source;
- tied candidate scores use direct evidence, live-radar status, primary implementation, structural score, relative strength and liquidity;
- `runtime/portfolio_rotation_engine.py` remains the stable production entrypoint.

## Validation evidence

```text
PR: #58
final_clean_head: 68432f65e2c19e039956bc129d3a484d46ce9b78
workflow_run: 29438154551
job: 87429929415
result: success
focused_tests: 10 passed
actual_artifact_replay: passed
```

The replay of the 2026-07-14 artifacts produced:

```text
URNM -> XBI
source_delta: -5.00% NAV
destination_delta: +5.00% NAV
estimated_notional: EUR 5511.24
validated_holdings: 9
```

## Exact files changed

```text
runtime/rotation_state_authority.py
runtime/portfolio_rotation_engine_v2.py
runtime/portfolio_rotation_engine.py
tools/validate_etf_rotation_state_authority.py
tests/test_etf_rotation_state_authority.py
.github/workflows/validate-etf-rotation-state-authority.yml
control/work_packages/WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES_20260715.md
control/ETF_ROTATION_STATE_AUTHORITY_CHANGELOG.md
control/ROTATION_STATE_AUTHORITY_STATUS_20260715.md
control/handovers/HANDOVER_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES_20260715.md
control/ETF_PORTFOLIO_ROTATION_CHANGELOG.md
control/ETF_SESSION_CHANGELOG.md
```

## Next action

1. Confirm the latest PR-head validation after the documentation commits.
2. Mark PR #58 ready and merge using squash.
3. Create a fresh standard U.S. Weekly ETF report request in `control/run_queue/`.
4. Verify the production run performs the guarded model mutation and persists it to state and trade ledger.
5. Verify the final English and Dutch reports reflect executed post-mutation holdings.
6. Verify run manifest, delivery manifest and Gmail inbox receipts.
7. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` with the new production baseline.

## Guardrails

- Do not describe the replay as production execution.
- Do not claim report delivery until the delivery manifest and inbox receipt exist.
- Do not bypass the one-major-rotation limit.
- Do not use prior report P/L as current authority.
- Do not allow a missing average-entry basis to default to zero P/L.
- Do not allow alphabetical ordering to decide between capped destination scores.