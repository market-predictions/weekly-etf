# ETF Rotation State Authority — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES`

## 2026-07-15 — Current-run authority defect identified

The 2026-07-14 report used fresh pricing and relative-strength data, but generated no rotation because the decision layer still consumed stale recommendation-scorecard values. The clearest defect was URNM: current-close arithmetic implied approximately -23.57% since entry, while the inherited machine-readable P/L remained -0.55%.

Additional defect:

- primary ETFs were selectable candidates;
- alternative ETFs such as BUG, SOXX, GRID and IBB remained metadata only;
- therefore a strong alternative could not become a direct replacement destination.

## 2026-07-15 — Implementation

Added `runtime/rotation_state_authority.py` to:

- revalue every holding from the current pricing audit;
- recompute EUR market value, NAV and position weight;
- recompute P/L from current close versus average entry;
- refresh the canonical scorecard before rotation;
- carry action-clock history forward without carrying stale valuation fields;
- fail when scorecard date, current price or P/L conflicts with current-run authority.

Added `runtime/portfolio_rotation_engine_v2.py` to:

- consume the current-run valuation state;
- persist the refreshed scorecard before release scoring;
- apply the forced re-underwriting trigger for a position below score 4.00 and down more than 10%;
- independently score lane primary and alternative ETFs;
- permit replacement-only alternatives only with valuation-grade pricing and at least a 10% direct 3-month edge;
- preserve the one-major-rotation, minimum-trade and maximum-source-reduction controls.

Replaced `runtime/portfolio_rotation_engine.py` with a compatibility entrypoint so existing workflow and import paths remain stable.

## Validation

Focused local validation before publication:

```text
python -m py_compile runtime/rotation_state_authority.py
python -m py_compile runtime/portfolio_rotation_engine_v2.py
pytest -q features/tests/test_etf_rotation_state_authority.py
```

Result at implementation time:

```text
5 passed
```

Pull-request validation remains required before merge and production execution.