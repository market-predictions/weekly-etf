# Work Package — WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: active / claimed

## Current issue

The official portfolio contains nine active whole-share positions while the maximum is eight. The position-count contract correctly classifies the state as `close_first`, but it deliberately does not decide which holding, if any, should be closed.

This package performs a fresh, no-mutation review of all plausible count-reducing paths. It must not assume that the 14-share XLU residual is automatically the correct source merely because it is the smallest position.

## Decision framework

The review must compare every active holding as a potential closure source using current evidence across:

1. portfolio role and diversification value;
2. current recommendation and thesis quality;
3. relative strength and trend condition;
4. contribution and opportunity cost;
5. liquidity and implementation practicality;
6. concentration and factor-overlap effects;
7. whether proceeds should remain in cash or be reallocated only to an already-held ticker.

Allowed review conclusions:

- `close_to_cash_supported`;
- `close_and_reallocate_existing_supported`;
- `no_trade_insufficient_evidence`.

A review conclusion is not execution authority. Any official portfolio mutation requires separate explicit user authorization after this package.

## Input/state contract

Authoritative state inputs:

```text
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
runtime/position_count_contract.py
```

Fresh evidence requirements:

- use the latest completed U.S. market close available when the package runs;
- build a read-only price and relative-strength snapshot for every active ticker;
- record source, timestamp, requested close date, observed price date and missing-data status;
- do not overwrite official pricing audits, portfolio state, trade ledger, valuation history, runtime pointers or delivered reports;
- treat prior report scores and thesis fields as continuity evidence, not automatic current-price truth;
- fail closed to `no_trade_insufficient_evidence` when essential current evidence is unavailable or internally inconsistent.

Every proposed transition must use whole shares and pass the existing position-count transition contract before it may be described as feasible.

## Output contract

Produce machine-readable evidence and a concise bilingual review surface stating:

- current count and maximum;
- evidence date and freshness status;
- ranked closure-source comparison for all nine holdings;
- selected conclusion and rationale;
- rejected alternatives and why;
- projected whole-share quantities, cash and active count for any supported transition;
- explicit statement that official state was not changed;
- client-safe English and Dutch wording without raw workflow, override or internal-engine terminology.

The package must not modify or resend historical client reports.

## Operational runbook

Implement and validate:

1. a read-only fresh-evidence builder for active holdings;
2. a deterministic close-first review engine;
3. projected transition checks through `runtime/position_count_contract.py`;
4. fixtures covering close-to-cash, reallocate-to-existing and insufficient-evidence outcomes;
5. a no-mutation GitHub Actions validation workflow;
6. persistent decision/review evidence;
7. governance closeout with claim release and handover.

## Authority boundary

This package must not:

- execute a trade;
- change `output/etf_portfolio_state.json`;
- append `output/etf_trade_ledger.csv`;
- change `output/etf_valuation_history.csv`;
- change official pricing pointers or run manifests;
- generate or deliver a production report;
- send email;
- select or open a new ticker while the portfolio is above the maximum.

## Acceptance criteria

- work package and claim are recorded before implementation;
- latest available completed-market-close evidence is used or the review fails closed;
- all nine holdings are compared under one deterministic rubric;
- no source is selected solely because it is the smallest position;
- any proposed transition passes whole-share and position-count preflight;
- official authority hashes remain unchanged;
- review evidence, decision record and bilingual surface are persisted;
- focused tests and workflow validation pass;
- PR is merged;
- claim is released;
- handover, `CURRENT_STATE.md`, `NEXT_ACTIONS.md`, `DECISION_LOG.md` and `ETF_SESSION_CHANGELOG.md` are updated;
- no portfolio mutation, report delivery or email occurs.
