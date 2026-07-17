# ETF Review OS — Current State

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`

## Official portfolio authority

```text
portfolio_state: output/etf_portfolio_state.json
trade_ledger: output/etf_trade_ledger.csv
whole_share_status: compliant
cash_eur: 2519.05
invested_market_value_eur: 104598.89
nav_eur: 107117.94
position_count: 8
```

Current whole-share positions:

```text
CIBR 253
GSG 374
IEFA 312
SMH 59
URNM 48
XBI 40
XLU 148
XLV 37
```

`DFEN` was closed because current constraints prohibit leveraged ETFs. Residual fractional positions below one share were converted to cash.

## Latest production report run

```text
requested_close_date: 2026-07-16
run_id: 20260717_094728
report_token: 260716
pricing_lineage_status: passed
workflow_status: workflow_success
production_rotation: DFEN -> XLV
```

Authority files:

```text
output/pricing/price_audit_2026-07-16_20260717_094728.json
output/runtime/etf_report_state_20260716_20260717_094728.json
output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_094728.json
output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_094728.json
```

## Latest delivered client package

```text
output/weekly_analysis_pro_260716.md
output/weekly_analysis_pro_260716.pdf
output/weekly_analysis_pro_nl_260716.md
output/weekly_analysis_pro_nl_260716.pdf
delivery_layer_status: smtp_sendmail_returned_no_exception
```

The delivered package predates the later whole-share reconciliation. It remains historical delivery evidence, but current holdings and cash must be read from `output/etf_portfolio_state.json`.

## Whole-share package

```text
package: WP_ETF_WHOLE_SHARE_STATE_CONTRACT
implementation_PR: #85
merge_commit: d5532ea15801a3888633ccb824797ab254305433
validation_run: 29580018310
focused_tests: 4 passed
reconciliation_commit: 50b93740efbed537ed9d0daed6e1d88ce912be1e
reconciliation_artifact: output/runtime/etf_whole_share_reconciliation_20260716_20260717_094728.json
adjusted_positions: 10
ledger_rows_appended: 10
cash_released_eur: 582.53
nav_drift_eur: 0.00
email_sent: false
status: closed
```

Stable rules:

1. Official positions and future guarded Buy/Sell deltas use whole shares.
2. Long-only quantities are floored, never rounded upward.
3. Unspent proceeds remain explicit EUR cash.
4. Guarded execution fails closed on fractional official state.
5. NAV drift may not exceed EUR 0.05.

## Cockpit roadmap

```text
WP01-WP09: merged
promotion decision: additive delivery front page
WP10 PR: #83
WP10 merge: 23328a9494fb5a2183eacd328365310dbf583af6
feature_default: disabled
production_enablement: false
promotion_status: not_promoted
```

## Immediate next action

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

WP11 must run an exact-current validate-only enabled bundle using the whole-share official state before any send, preserve rollback to `disabled`, and require real delivery evidence for any later delivery claim.
