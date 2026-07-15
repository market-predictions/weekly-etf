# ETF Rotation State Authority — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES`

## 2026-07-15 — Current-run authority defect identified

The 2026-07-14 report used fresh pricing and relative-strength data, but generated no rotation because the decision layer still consumed stale recommendation-scorecard values. The clearest defect was URNM: current-close arithmetic implied approximately -23.57% since entry, while the inherited machine-readable P/L remained -0.55%.

Additional defects:

- primary ETFs were selectable candidates, while alternatives such as BUG, SOXX, GRID and IBB remained metadata only;
- several accumulated positions had no persisted average entry even though official model-execution artifacts retained their acquisition prices;
- capped destination scores could fall through to alphabetical ordering, initially selecting IAI instead of the better-supported live-radar XBI candidate.

## 2026-07-15 — Implementation

Added `runtime/rotation_state_authority.py` to:

- revalue every holding from the current pricing audit;
- recompute EUR market value, NAV and position weight;
- recompute P/L from current close versus average entry;
- reconstruct missing average entry from official trade-ledger references and model-execution artifacts;
- refresh the canonical scorecard before rotation;
- carry action-clock history forward without carrying stale valuation fields;
- fail when scorecard date, current price, average-entry basis or P/L conflicts with current-run authority.

Added `runtime/portfolio_rotation_engine_v2.py` to:

- consume the current-run valuation state;
- persist the refreshed scorecard before release scoring;
- apply the forced re-underwriting trigger for a position below score 4.00 and down more than 10%;
- independently score lane primary and alternative ETFs;
- permit replacement-only alternatives only with valuation-grade pricing and at least a 10% direct 3-month edge;
- rank tied destinations using direct-duel evidence, live-radar status, primary implementation, structural score, relative strength and liquidity;
- preserve the one-major-rotation, minimum-trade and maximum-source-reduction controls.

Replaced `runtime/portfolio_rotation_engine.py` with a compatibility entrypoint so existing workflow and import paths remain stable.

## 2026-07-15 — Validation and replay

Focused validation:

```text
python -m py_compile runtime/rotation_state_authority.py runtime/portfolio_rotation_engine_v2.py runtime/portfolio_rotation_engine.py tools/validate_etf_rotation_state_authority.py
python -m pytest -q tests/test_etf_rotation_state_authority.py
```

Result:

```text
10 passed
```

Final clean PR gate:

```text
PR: #58
head_sha: 68432f65e2c19e039956bc129d3a484d46ce9b78
workflow_run_id: 29438154551
job_id: 87429929415
conclusion: success
```

The actual committed 2026-07-14 production artifacts were replayed. Evidence:

```text
validated_holding_count: 9
scorecard_date_aligned: true
pnl_consistent_with_current_close_and_avg_entry: true
average_entry_authority_complete: true
current_price_consistent: true
NAV: EUR 110224.85
trade_intent_count: 1
trade_intent: reduce URNM by 5.00% NAV and allocate EUR 5511.24 to XBI
```

The retained plan artifact is stored by workflow run `29438154551` as `corrected-july-rotation-plan`.

## Remaining production proof

The PR is validated but not yet production-proven. Required next sequence:

1. merge PR #58;
2. request one fresh U.S. Weekly ETF production report;
3. confirm current-run scorecard persistence, model execution, state and trade-ledger mutation;
4. confirm report/run/delivery manifests;
5. confirm English and Dutch inbox receipts;
6. update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` with the production baseline.