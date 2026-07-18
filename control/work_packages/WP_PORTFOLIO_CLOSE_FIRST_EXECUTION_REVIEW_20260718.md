# Work Package — WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: closed / merged / validated_no_change

## Current issue

The official portfolio contains nine active whole-share positions while the maximum is eight. The position-count contract classifies the state as `close_first`, but it deliberately did not choose which holding should be closed.

This package performed a fresh, read-only review of all plausible count-reducing paths. It did not assume that the 14-share XLU residual was automatically the correct source merely because it is the smallest position.

## Decision framework

Every active holding was compared using:

1. portfolio role and diversification value;
2. current holding recommendation quality;
3. current lane and thesis quality;
4. relative strength and trend condition;
5. contribution and opportunity cost;
6. liquidity and implementation practicality;
7. concentration and factor-overlap effects;
8. preservation credits for recent additions, high conviction and strong contribution.

Holding quality and current lane quality were recorded separately. The lower score formed the decision-quality floor. Position size was a minor practicality input only; a selected source had to remain first without those points and needed multiple independent issue families.

## Input/state contract

Authoritative inputs:

```text
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/lane_reviews/etf_lane_assessment_260716.json
runtime/position_count_contract.py
fresh yfinance completed-close data for 2026-07-17
```

Missing or stale essential evidence would have forced `no_trade_insufficient_evidence`. Official pricing audits, pointers, state, ledger, valuation history and delivered reports were not changed.

## Output contract

The package persisted:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
control/handovers/HANDOVER_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md
```

The English and Dutch surfaces state the full nine-position comparison, selected review source, projected count and cash, and the explicit no-change boundary. Raw machine conclusions are translated into client-readable wording.

## Operational implementation

```text
runtime/build_portfolio_close_first_review.py
tools/validate_portfolio_close_first_review.py
tests/test_portfolio_close_first_review.py
fixtures/portfolio_close_first_review/close_to_cash.json
fixtures/portfolio_close_first_review/reallocate_existing.json
fixtures/portfolio_close_first_review/insufficient_evidence.json
.github/workflows/validate-portfolio-close-first-review.yml
```

The builder fetches completed-close market data, computes current relative-strength and trend evidence, combines it with current lane and holding continuity, ranks all nine sources, validates the projected whole-share transition and fails closed when evidence is incomplete or insufficiently differentiated.

## Review result

```text
source: URNM
reviewed quantity: 48 whole shares
destination: cash
estimated proceeds_eur: 2022.23
projected cash_eur: 4556.59
projected active positions: 8
new ticker opened: false
portfolio change applied: false
```

URNM ranked first at 90.32 and remained first at 87.32 after removing size/practicality points. Its holding score was 3.70, current lane score 2.96, one-month relative strength versus SPY -15.64 percentage points, three-month relative strength -33.97 percentage points and trend score 0.0.

XLU ranked second at 75.55. The smallest position did not determine the result.

## Merge and validation evidence

```text
implementation_pull_request: #95
implementation_merge: 2895bbb5940ead8526ab4c10d0ce3687f8aca423
implementation_head: bbf03f8966c93d714ff750c9d177917bcc0eef9d
closeout_pull_request: #96
closeout_merge: b2d32e327023ea515c1c78ccbc66f69b69afab45
metadata_pull_request: #97
primary_review_run: 29622365939 success
primary_review_job: 88019775095
primary_artifact_id: 8422627986
primary_artifact_digest: sha256:9f0b833f6d9dd5bb7b7558afe598c20246e67707fc5cff974e1bfc661479851a
final_review_run: 29622792895 success
final_position_count_run: 29622792864 success
final_report_language_run: 29622792867 success
final_current_runtime_cockpit_run: 29622792888 success
final_wp08_run: 29622792861 success
final_wp11_run: 29622792862 success
focused_tests: 7 passed
final_artifact_id: 8422761924
final_artifact_digest: sha256:1526642d997b2c9055554a3bab969ba84d1bafdf103285af00056fb7f96eae29
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

## Acceptance status

- work package and claim recorded before implementation: complete;
- latest completed-close evidence used: complete;
- all nine holdings compared under one deterministic rubric: complete;
- smallest-position automatic selection blocked: complete;
- projected whole-share transition preflight passed: complete;
- official authority hashes unchanged: complete;
- review evidence, decision record, bilingual surfaces and handover persisted: complete;
- focused and compatibility validation passed: complete;
- implementation PR merged: complete;
- governance-closeout PR merged: complete;
- claim release: complete;
- no portfolio change, report delivery or email: confirmed.

## Next package

A separate explicitly approved package may be created:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION
```

It must refresh prices, rerun the same rubric and stop without changes if URNM is no longer selected or evidence is incomplete.
