# Handover — Shared Strategy State and Exposure Portfolio Target

Date: 2026-07-27
Repository: `market-predictions/weekly-etf`
Branch: `sync/shared-strategy-state`
Draft PR: #113
Status: presentable shadow implementation; not merged

## Delivered

Weekly ETF now exports two read-only donor artifacts for consumption by Weekly ETF EU:

1. `etf_shared_strategy_state_v1`
   - complete assessed lane set;
   - promoted opportunity ranking;
   - regime lineage;
   - methodology, market-evidence, macro and donor-context score decomposition;
   - no funding or execution authority.

2. `etf_shared_portfolio_target_v1`
   - all current donor holdings mapped to stable exposure IDs;
   - current and validated rotation-plan target weights;
   - position actions, release scores and constraint context;
   - no portfolio mutation or execution authority.

## Current donor reference

```text
report_date: 2026-07-24
source_run_id: 20260726_191116
assessed_lanes: 25
promoted_lanes: 6
portfolio_positions: 9
maximum_positions: 8
position_constraint: close_first
trade_intents: 0
nav_eur: 107189.79
cash_eur: 2534.36
cash_weight_pct: 2.364367
```

Promoted exposures:

1. cybersecurity resilience
2. AI compute and semiconductors
3. grid buildout and electrification
4. healthcare quality
5. defense resilience
6. food security and agriculture inputs

Exposure-level donor targets:

```text
ai_compute_infrastructure       27.16%
non_us_developed_equities       24.66%
cyber_security                  18.35%
broad_commodities               10.05%
grid_power                       5.06%
biotech_innovation               4.94%
healthcare_quality               4.93%
uranium_nuclear                  1.95%
power_utilities_capex            0.53%
cash                             2.364367%
```

## Validation

Latest completed donor workflow:

```text
workflow: Validate shared ETF strategy state
run_id: 30281156879
conclusion: success
branch_commit: d0ebe6700555b0d8d50ec37145966cd7a11db495
```

Validated boundaries:

- deterministic output except generation timestamp;
- source run and file lineage present;
- all donor positions mapped to exposure IDs;
- exposure aggregates reconcile to position targets;
- target weights plus cash reconcile to 100%;
- no portfolio mutation, funding authority or execution authority.

## Production boundary

This branch does not alter:

- the official Weekly ETF portfolio;
- the trade ledger;
- the production report renderer;
- report delivery;
- any broker or model execution path.

## Remaining work before production promotion

1. Decide whether the shared artifacts should be generated inside the production workflow or a separate reusable workflow.
2. Replace branch-to-branch consumption with a versioned merged contract only after both PRs are reviewed.
3. Preserve backward compatibility for the existing US report and rotation engine.
4. Add a formal version/promotion policy for consumers.

## Next safe action

Review draft PR #113 together with the EU synchronization shadow. Do not merge solely because CI is green; confirm the consumer contract and versioning boundary first.
