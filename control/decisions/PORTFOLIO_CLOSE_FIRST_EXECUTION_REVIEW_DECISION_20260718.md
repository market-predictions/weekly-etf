# Decision — Portfolio Close-First Execution Review

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Package: `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW`
Status: approved as review evidence / not execution authority

## Decision framework

A count-reducing option is supported only when one source ranks first on multiple independent factors, remains first without position-size practicality points, and its projected whole-share transition passes the active-position contract.

Using completed-close evidence for 2026-07-17, the selected review option is:

```text
source: URNM
quantity reviewed for closure: 48 shares
destination: cash
projected active positions: 8
new ticker opened: false
review conclusion: close_to_cash_supported
```

URNM ranks above XLU even without size points. The decisive evidence is its 2.96 current lane score, 3.70 holding score, -15.64 percentage-point one-month relative strength versus SPY, -33.97 percentage-point three-month relative strength versus SPY, 0.0 trend score, material drag, failed portfolio role and existing release evidence.

The structural nuclear-security thesis remains relevant, but current timing and market confirmation are materially weaker than the rest of the portfolio. This supports closing the current vehicle to restore the count while retaining the proceeds as cash rather than automatically rotating into another risk asset.

## Input/state contract

Authority for this review:

```text
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/lane_reviews/etf_lane_assessment_260716.json
fresh yfinance completed-close snapshot for 2026-07-17
runtime/position_count_contract.py
```

Holding quality and current lane quality are recorded separately. The lower score forms the decision-quality floor. Historical reports are continuity evidence only and were not rewritten.

## Output contract

The persistent English and Dutch review surfaces state:

- current count is nine and maximum is eight;
- URNM is the selected review source;
- all 48 shares are the reviewed closure quantity;
- no new ticker is opened;
- projected cash is EUR 4,556.59 using the reference close;
- official portfolio state was not changed;
- separate authorization and execution-time pricing are required.

## Operational runbook

A future execution package may use this decision only after separate explicit authorization. It must:

1. refresh URNM and EUR/USD prices at the execution reference time;
2. revalidate that URNM remains the selected source under the same rubric;
3. fail closed if evidence changes materially or pricing is incomplete;
4. sell only whole shares;
5. open no new ticker;
6. re-run position-count and NAV reconciliation before official writes;
7. persist state, ledger and valuation evidence only after successful validation;
8. treat report generation and delivery as separate authorized actions.

## Authority boundary

This decision did not execute a transaction and did not change portfolio state, trade ledger, valuation history, pricing pointers, historical reports, production reports or email delivery.

Persistent evidence:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
```
