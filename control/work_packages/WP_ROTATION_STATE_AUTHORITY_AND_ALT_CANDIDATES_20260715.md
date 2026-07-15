# WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-current-run-rotation-authority`
Layer: decision framework + input/state contract + operational runbook
Status: implemented and PR-validated / production execution pending merge

## Current issue

The 2026-07-14 production run used fresh market pricing for valuation and relative-strength discovery, but the rotation decision still consumed stale recommendation-memory fields, including May-dated P/L, fresh-cash decisions and replacement timers. Alternative ETFs were descriptive metadata rather than independently selectable destinations.

## Root cause

1. The rotation engine loaded the persisted portfolio state and canonical scorecard before deriving a current-run valuation state.
2. Stored P/L could override the arithmetic implied by current close and average entry.
3. Several accumulated holdings had no persisted average entry even though their model execution artifacts retained lot prices.
4. The scorecard was checked only after report generation and was not refreshed before capital-release scoring.
5. `candidate_reviews()` emitted only each lane's primary ETF.
6. Capped destination scores could fall through to alphabetical order instead of quality evidence.
7. No blocking authority check required scorecard dates, current prices, average-entry basis and P/L to match the current run.

## Implemented change

1. Derive current-run positions, market values, NAV, weights and P/L from the current pricing audit before rotation.
2. Reconstruct missing average entry deterministically from the trade ledger and referenced model-execution artifacts; fail if reconstruction is incomplete.
3. Refresh and persist the canonical recommendation scorecard before capital-release scoring.
4. Block rotation-plan creation when scorecard dates, current prices, average-entry authority or P/L conflict with current-run state.
5. Emit primary and alternative ETFs as independently scored candidate records.
6. Require a direct 3-month edge of at least 10% before a replacement-only candidate can displace its mapped holding.
7. Rank tied destinations using direct-duel priority, live-radar status, primary implementation, structural score, relative strength and liquidity.
8. Preserve one major rotation per run, minimum trade size and maximum source-reduction limits.

## Files

```text
runtime/rotation_state_authority.py
runtime/portfolio_rotation_engine_v2.py
runtime/portfolio_rotation_engine.py
tests/test_etf_rotation_state_authority.py
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
- Missing average entry must be reconstructed from official model-execution history or block rotation.
- Prior scorecard is continuity memory only; it may carry qualitative fields and action-clock history, but not stale price, weight or P/L.
- Alternative ETFs may become replacement-only destinations when valuation-grade priced and when the direct 3-month edge clears 10%.
- Cross-sleeve destinations require general fundability and a failed or sufficiently aged impaired source.
- Destination selection must use quality evidence, not alphabetical ordering after score caps.
- The engine remains ticker-agnostic and does not hard-code a production mutation.

## Validation evidence

```text
PR: #58
head_sha: 68432f65e2c19e039956bc129d3a484d46ce9b78
workflow_run_id: 29438154551
job_id: 87429929415
workflow_conclusion: success
focused_tests: 10 passed
validated_holding_count: 9
scorecard_date_aligned: true
pnl_consistent_with_current_close_and_avg_entry: true
average_entry_authority_complete: true
current_price_consistent: true
replay_report_date: 2026-07-14
replay_nav_eur: 110224.85
replay_trade_intent: URNM -> XBI, -5.00% NAV, EUR 5511.24
```

Validation commands:

```text
python -m py_compile runtime/rotation_state_authority.py runtime/portfolio_rotation_engine_v2.py runtime/portfolio_rotation_engine.py tools/validate_etf_rotation_state_authority.py
python -m pytest -q tests/test_etf_rotation_state_authority.py
python tools/validate_etf_rotation_state_authority.py --plan <generated-plan>
```

## Completion boundary

The implementation package is PR-validated. It is not yet production-proven. Completion requires merge, one fresh production report run, persisted model-execution evidence, run and delivery manifests, and end-recipient receipt confirmation.