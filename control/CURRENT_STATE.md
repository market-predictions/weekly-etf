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

The delivered package predates the later whole-share reconciliation and cockpit production enablement. It remains historical delivery evidence, but current holdings and cash must be read from `output/etf_portfolio_state.json`. Historical files are not retrofitted.

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

Stable whole-share rules:

1. Official positions and future guarded Buy/Sell deltas use whole shares.
2. Long-only quantities are floored, never rounded upward.
3. Unspent proceeds remain explicit EUR cash.
4. Guarded execution fails closed on fractional official state.
5. NAV drift may not exceed EUR 0.05.

## Cockpit production status

```text
WP01-WP09: merged
promotion decision: additive delivery front page
WP10 PR: #83
WP10 merge: 23328a9494fb5a2183eacd328365310dbf583af6
WP11 PR: #87
feature: MRKT_RPRTS_COCKPIT_FRONT_PAGE
production_feature_value: enabled
rollback_value: disabled
production_enablement: true
promotion_status: production_enabled_no_send
```

WP11 exact-current validation:

```text
validation_run: 29582753816
validation_job: 87892175344
current_runtime_regression_run: 29582753774
wp08_regression_run: 29582753837
evidence: control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
whole_share_overlay: passed
EN_front_page_count: 1
NL_front_page_count: 1
EN_PDF_page_delta: +1
NL_PDF_page_delta: +1
classic_report_body: preserved
small_decision_cockpit_duplicate: false
protected_authority_hashes: identical
email_sent: false
```

Stable cockpit rules:

1. Future production runs add one cockpit front page per language.
2. The full classic report remains the evidence layer behind that page.
3. Invalid values or front-page render failure fail closed to the unchanged classic output.
4. Operational rollback is `MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled`.
5. WP11 did not send or mutate portfolio, ledger, valuation, pricing or historical reports.
6. A real delivery claim requires a separate production run and real manifest/receipt evidence.

## Immediate next action

```text
WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP
```

The next package should remove confirmed client-facing internal terms such as `shadow engine`, repeated punctuation and workflow-derived phrasing from future English/Dutch report surfaces. It must preserve the whole-share state contract, macro/thesis leakage firewall, pricing authority, portfolio execution, delivery contracts and historical-output immutability.

After that cleanup, a new report and email require a separate explicit production request. That future run should prove the enabled cockpit front page in a real delivered whole-share package.
