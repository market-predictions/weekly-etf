# Handover — Portfolio Close-First Execution Review

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Package: `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW`
Status: closed on governance-closeout merge / claim release effective on merge
Implementation pull request: #95
Implementation merge: `2895bbb5940ead8526ab4c10d0ce3687f8aca423`
Governance-closeout pull request: #96
Governance-closeout merge: pending

## Current issue

The official portfolio remains at nine active whole-share positions while the maximum is eight. The prior reconciliation package established the `close_first` rule but intentionally did not choose a source position.

Official state remains:

```text
CIBR 253
GSG 374
IEFA 312
PAVE 107
SMH 59
URNM 48
XBI 40
XLU 14
XLV 37
cash_eur: 2534.36
nav_eur: 107117.94
active_position_count: 9
maximum_active_positions: 8
position_count_status: close_first
```

## Root cause and review objective

The prior `XLU -> PAVE` portfolio change reduced XLU without closing it, so the active count increased to nine. The count contract now prevents repetition, but the current state still needs a justified count-reducing path.

This package compares every active holding. It does not assume that XLU should be closed merely because it is the smallest position.

## Decision framework

The deterministic comparison covers:

1. portfolio role and diversification value;
2. holding recommendation quality;
3. current lane and thesis quality;
4. one- and three-month relative strength versus SPY;
5. trend condition;
6. contribution and opportunity cost;
7. release and replaceability evidence;
8. liquidity and implementation practicality;
9. preservation credits for recent additions, high conviction and strong contribution.

Holding quality and current lane quality are stored separately. The lower score forms the decision-quality floor. Position size is a minor practicality input only. The selected source must remain first without those points and must have multiple independent issue families.

## Input/state contract

The review used:

```text
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/lane_reviews/etf_lane_assessment_260716.json
fresh yfinance completed-close data for 2026-07-17
runtime/position_count_contract.py
```

Missing or stale essential data would have produced `no_trade_insufficient_evidence`. Official pricing audits and pointers were not changed.

## Output contract

Persistent English and Dutch review surfaces disclose the complete nine-position ranking, selected review source, reference-date proceeds, projected count and cash, and the explicit no-change boundary.

Machine conclusion:

```text
close_to_cash_supported
```

Client-safe conclusion:

```text
Close all 48 URNM shares and retain the estimated proceeds as cash, subject to separate approval and refreshed reference pricing.
```

## Review result

```text
selected source: URNM
reviewed quantity: 48 whole shares
destination: cash
estimated proceeds_eur: 2022.23
projected cash_eur: 4556.59
projected active_position_count: 8
opened tickers: none
position_count preflight: passed
```

URNM ranked first at 90.32 and remained first at 87.32 without size/practicality points. Its holding score was 3.70, current lane score 2.96, one-month relative strength versus SPY -15.64 percentage points, three-month relative strength -33.97 percentage points and trend score 0.0.

The structural nuclear-security thesis remains relevant, but current timing and market confirmation are materially weaker than the rest of the portfolio. XLU ranked second at 75.55; its 0.52% weight did not determine the result.

## Exact implementation files

```text
runtime/build_portfolio_close_first_review.py
tools/validate_portfolio_close_first_review.py
tests/test_portfolio_close_first_review.py
fixtures/portfolio_close_first_review/close_to_cash.json
fixtures/portfolio_close_first_review/reallocate_existing.json
fixtures/portfolio_close_first_review/insufficient_evidence.json
.github/workflows/validate-portfolio-close-first-review.yml
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
```

## Validation

```text
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
```

Test coverage includes close-to-cash, reallocation to an existing holding, insufficient-evidence fail-closed behavior, smallest-position non-selection, input immutability, client-surface hygiene and lane-quality flooring.


## Final same-head validation

```text
validated_head: bbf03f8966c93d714ff750c9d177917bcc0eef9d
review_run: 29622792895 success
position_count_run: 29622792864 success
report_language_run: 29622792867 success
current_runtime_cockpit_run: 29622792888 success
wp08_run: 29622792861 success
wp11_run: 29622792862 success
artifact_id: 8422761924
artifact_digest: sha256:1526642d997b2c9055554a3bab969ba84d1bafdf103285af00056fb7f96eae29
protected_authority_hashes: identical
historical_report_hashes: identical
```

## Authority boundary

```text
portfolio_change_applied: false
portfolio_state_changed: false
trade_ledger_changed: false
valuation_history_changed: false
pricing_pointer_changed: false
historical_output_changed: false
production_report_delivered: false
email_sent: false
```

This handover records a supported review option, not a completed portfolio change.

## Next action

A separate explicitly authorized package may be created:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION
```

That package must refresh URNM and EUR/USD prices, rerun the same selection rubric, stop without changes if the selected source changes or evidence becomes incomplete, use whole shares, open no new ticker, and complete position-count and NAV reconciliation before official writes. Report generation and delivery remain separate actions.
