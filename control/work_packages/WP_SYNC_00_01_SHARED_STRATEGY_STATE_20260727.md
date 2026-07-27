# WP-SYNC-00/01 — Shared Strategy Decision State

Date: 2026-07-27
Status: claimed / implementation in progress
Branch: `sync/shared-strategy-state`

## Purpose

Extract a versioned, read-only, exposure-level strategy artifact from the mature Weekly ETF donor architecture so Weekly ETF EU can consume the same regime, opportunity ranking, evidence and desired exposure direction.

## Authority boundaries

- No portfolio mutation.
- No trade-ledger write.
- No report send.
- No change to existing US report wording or ranking.
- The artifact has strategy/research authority only; it has no funding, execution or broker authority.
- Existing production state, pricing, lane discovery and report rendering remain authoritative for the US report.

## Inputs

1. latest `output/lane_reviews/etf_lane_assessment_*.json`;
2. latest `output/runtime/etf_report_state_*.json`;
3. `output/macro/latest.json` when available;
4. current `output/etf_portfolio_state.json`;
5. existing scoring constants from `runtime/score_etf_lanes.py`.

## Outputs

- `schemas/etf_shared_strategy_state.schema.json`
- `runtime/build_shared_strategy_state.py`
- `tools/validate_shared_strategy_state.py`
- `output/shared/etf_shared_strategy_state_<report_date>_<run_id>.json`

## Required contract

The artifact must separate:

- raw methodology fields;
- structural/methodology score;
- market evidence adjustment;
- macro adjustment;
- donor portfolio/implementation context adjustment;
- final donor ranking score.

It must retain every assessed lane, not only promoted lanes, so EU can distinguish genuine strategic rejection from missing product implementation.

## Acceptance criteria

- deterministic output for identical inputs;
- all promoted lanes appear in `promoted_exposures`;
- exposure IDs are stable and ticker-independent;
- report date and source run lineage are explicit;
- current US holdings are context only, not embedded as EU instructions;
- validator fails on missing lineage, duplicate exposure IDs, inconsistent ranks or execution authority;
- existing US production output remains unchanged.

## Next package

After this contract is green, Weekly ETF EU may add a shadow-only importer and UCITS mapping layer under its own branch and authority boundaries.
