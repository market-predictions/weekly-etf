# Handover — Cockpit Surface 11 Production Enablement Closeout

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT`
Status: closed / production enabled / no send

## Decision

The additive English/Dutch cockpit front page is enabled for future real Weekly ETF production runs through:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

Rollback remains:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: disabled
```

## Production file changed

```text
.github/workflows/send-weekly-report.yml
```

The feature value is defined at the `send-report` job level. The send workflow was not dispatched during WP11.

## Exact-current validation design

The last delivered `260716` report predates the whole-share state reconciliation and was not misrepresented as current authority.

WP11 created a temporary validation overlay using:

```text
runtime/pricing/macro/lane context:
  output/runtime/etf_report_state_20260716_20260717_094728.json
current position/cash/NAV authority:
  output/etf_portfolio_state.json
```

The overlay was never persisted to production. It cleared stale trade intents and rotation-plan mutation state, then rendered fresh English/Dutch report markdown and disabled/enabled delivery bundles in temporary storage only.

## Current authority validated

```text
whole_share_status: compliant
position_count: 8
nav_eur: 107117.94
cash_eur: 2519.05
largest_position: SMH
```

## Evidence

```text
control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
validation_run: 29582753816
validation_job: 87892175344
artifact_id: 8407711197
artifact_digest: sha256:b483b7157a69939e66c9a7b3624b2401a2211c5ba2db1367b97374aa1b0899a9
current_runtime_regression_run: 29582753774
wp08_regression_run: 29582753837
```

Measured output:

```text
EN disabled front pages: 0
EN enabled front pages: 1
EN PDF pages: 16 -> 17
NL disabled front pages: 0
NL enabled front pages: 1
NL PDF pages: 17 -> 18
classic body: preserved
small decision cockpit duplicate: false
protected authority hashes: identical
email sent: false
```

Front-page facts:

```text
Portfolio value: EUR 107118 rounded display
Return since inception: +7.1%
Cash: 2.4% / EUR 2519 rounded display
Positions: 8
Largest position: SMH 27.4%
EUR/USD: 1.1443
Maximum drawdown: -7.5%
```

## Supporting changes

The following historical regressions were rebased to the current production baseline:

```text
.github/workflows/validate-cockpit-current-runtime.yml
.github/workflows/validate-cockpit-wp08-evidence-review.yml
```

Their old hardcoded `260714 / URNM → XBI` assertions were replaced by the current `260716 / DFEN → XLV` evidence. Both workflows passed and authority files remained unchanged.

## Authority boundary

WP11 changed the production output contract only.

It did not change:

```text
portfolio positions
portfolio cash or NAV
trade ledger
valuation history
pricing audit
macro/thesis authority
lane scoring
fundability
portfolio execution
historical delivered reports
email delivery
```

A new report and email require a separate explicit production request. A delivery claim requires an actual run manifest plus delivery evidence.

## Recommended next package

```text
WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP
```

Purpose: remove confirmed client-facing internal terms such as `shadow engine`, double punctuation and other workflow-derived phrasing from future EN/NL report surfaces while preserving macro/thesis leakage, state, pricing, execution and delivery contracts.

After that cleanup, the next separately authorized fresh production run should prove the enabled front page in a real delivered package generated from the whole-share state.
