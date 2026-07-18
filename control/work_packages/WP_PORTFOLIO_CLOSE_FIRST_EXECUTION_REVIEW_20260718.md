# Work Package — WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: implementation_complete / validation_green / merge_pending

## Current issue

The official portfolio contains nine active whole-share positions while the maximum is eight. The position-count contract correctly classifies the state as `close_first`, but it deliberately does not decide which holding, if any, should be closed.

This package performs a fresh, no-mutation review of all plausible count-reducing paths. It must not assume that the 14-share XLU residual is automatically the correct source merely because it is the smallest position.

## Decision framework

The review compares every active holding as a potential closure source using current evidence across:

1. portfolio role and diversification value;
2. current holding recommendation quality;
3. current lane and thesis quality;
4. relative strength and trend condition;
5. contribution and opportunity cost;
6. liquidity and implementation practicality;
7. concentration and factor-overlap effects;
8. whether proceeds should remain in cash or be reallocated only to an already-held ticker.

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
output/lane_reviews/etf_lane_assessment_260716.json
runtime/position_count_contract.py
```

Fresh evidence rules:

- use the latest completed U.S. market close available when the package runs;
- build a read-only price and relative-strength snapshot for every active ticker;
- record source, timestamp, requested close date, observed price date and missing-data status;
- do not overwrite official pricing audits, portfolio state, trade ledger, valuation history, runtime pointers or delivered reports;
- treat prior report scores and thesis fields as continuity evidence, not automatic current-price truth;
- record holding quality and current lane quality separately, with the lower value as the decision-quality floor;
- fail closed to `no_trade_insufficient_evidence` when essential current evidence is unavailable or internally inconsistent.

Every proposed transition uses whole shares and passes the existing position-count transition contract before it may be described as feasible.

## Output contract

Machine-readable evidence and concise bilingual review surfaces state:

- current count and maximum;
- evidence date and freshness status;
- ranked closure-source comparison for all nine holdings;
- selected conclusion and rationale;
- rejected alternatives and why;
- projected whole-share quantities, cash and active count;
- explicit statement that official state was not changed;
- client-safe English and Dutch wording without internal implementation terminology.

The package did not modify or resend historical client reports.

## Operational runbook

Implemented:

1. read-only fresh-evidence builder: `runtime/build_portfolio_close_first_review.py`;
2. deterministic close-first review engine in the same module;
3. projected transition checks through `runtime/position_count_contract.py`;
4. fixtures covering close-to-cash, reallocation to an existing holding and insufficient-evidence outcomes;
5. seven focused regressions in `tests/test_portfolio_close_first_review.py`;
6. evidence validator: `tools/validate_portfolio_close_first_review.py`;
7. read-only GitHub Actions gate: `.github/workflows/validate-portfolio-close-first-review.yml`;
8. persistent English, Dutch, decision and evidence records.

## Review result

Fresh completed-close evidence for 2026-07-17 produced this supported review option:

```text
source: URNM
reviewed quantity: 48 whole shares
destination: cash
estimated proceeds_eur: 2022.23
projected cash_eur: 4556.59
projected active positions: 8
new ticker opened: false
official portfolio mutation: false
```

URNM ranked first at 90.32 and remained first at 87.32 after removing implementation-practicality points. Its holding score was 3.70, current lane score 2.96, one-month relative strength versus SPY -15.64 percentage points, three-month relative strength -33.97 percentage points and trend score 0.0.

XLU ranked second at 75.55. Its smaller position size did not determine the result.

## Validation evidence

```text
pull_request: #95
validated_head: 23a377e5f65cc193b3dead3494681f3dc64b7cc3
workflow_run: 29622365939
workflow_job: 88019775095
result: success
focused_tests: 7 passed
artifact_id: 8422627986
artifact_digest: sha256:9f0b833f6d9dd5bb7b7558afe598c20246e67707fc5cff974e1bfc661479851a
market_close_date: 2026-07-17
market_freshness: complete
protected_authority_hashes: identical
historical_report_hashes: identical
portfolio_execution: false
email_sent: false
```

Persistent records:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
```

## Authority boundary

This package did not:

- perform a transaction;
- change `output/etf_portfolio_state.json`;
- append `output/etf_trade_ledger.csv`;
- change `output/etf_valuation_history.csv`;
- change official pricing pointers or run manifests;
- generate or deliver a production report;
- send email;
- select or open a new ticker while the portfolio remains above the maximum.

## Acceptance status

- work package and claim recorded before implementation: complete;
- latest completed-market-close evidence used: complete;
- all nine holdings compared under one deterministic rubric: complete;
- smallest-position automatic selection blocked: complete;
- projected whole-share transition preflight passed: complete;
- official authority hashes unchanged: complete;
- review evidence, decision record and bilingual surfaces persisted: complete;
- focused tests and workflow validation passed: complete;
- PR merge: pending;
- claim release and exact post-merge handover closeout: pending merge;
- no portfolio mutation, report delivery or email: confirmed.
