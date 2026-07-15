# WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-current-run-rotation-authority`
Layer: decision framework + input/state contract + operational runbook
Status: implemented / validation pending

## Current issue

The 2026-07-14 production run used fresh market pricing for valuation and relative-strength discovery, but the rotation decision still consumed stale recommendation-memory fields, including May-dated P/L, fresh-cash decisions and replacement timers. Alternative ETFs were descriptive metadata rather than independently selectable destinations.

## Root cause

1. The rotation engine loaded the persisted portfolio state and canonical scorecard before deriving a current-run valuation state.
2. Stored P/L could override the arithmetic implied by current close and average entry.
3. The scorecard was checked only after report generation and was not refreshed before capital-release scoring.
4. `candidate_reviews()` emitted only each lane's primary ETF.
5. No blocking authority check required scorecard dates and P/L to match the current run.

## Required change

1. Derive current-run positions, market values, NAV, weights and P/L from the current pricing audit before rotation.
2. Refresh and persist the canonical recommendation scorecard before capital-release scoring.
3. Block rotation-plan creation when scorecard dates, current prices or P/L conflict with the current-run valuation state.
4. Emit primary and alternative ETFs as independently scored candidate records.
5. Require a direct 3-month edge of at least 10% before a replacement-only candidate can displace its mapped holding.
6. Preserve one major rotation per run, minimum trade size and maximum source-reduction limits.

## Files

```text
runtime/rotation_state_authority.py
runtime/portfolio_rotation_engine_v2.py
runtime/portfolio_rotation_engine.py
features/tests/test_etf_rotation_state_authority.py
.github/workflows/validate-etf-rotation-state-authority.yml
tools/validate_etf_rotation_state_authority.py
control/work_packages/WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES_20260715.md
control/ETF_ROTATION_STATE_AUTHORITY_CHANGELOG.md
control/ROTATION_STATE_AUTHORITY_STATUS_20260715.md
control/handovers/HANDOVER_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES_20260715.md
```

## Authority rules

- Current pricing audit is authoritative for current close, market value, NAV and position weight.
- Average entry plus current close is authoritative for current P/L.
- Prior scorecard is continuity memory only; it may carry qualitative fields and action-clock history, but not stale price, weight or P/L.
- Alternative ETFs may become replacement-only destinations when valuation-grade priced and when the direct 3-month edge clears 10%.
- Cross-sleeve destinations still require general fundability and a failed or sufficiently aged impaired source.
- The engine remains ticker-agnostic and does not hard-code a specific recommended mutation.

## Validation plan

```text
python -m py_compile runtime/rotation_state_authority.py runtime/portfolio_rotation_engine_v2.py runtime/portfolio_rotation_engine.py tools/validate_etf_rotation_state_authority.py
pytest -q features/tests/test_etf_rotation_state_authority.py
python tools/validate_etf_rotation_state_authority.py --plan <generated-plan>
```

The pull-request workflow must run the compile and focused test gates. A production report run is authorized only after those gates pass and the PR is merged.