# Work Package — WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Layer: decision framework + output contract + operational runbook
Status: closed / production enabled / no send

## Current issue

WP10 implemented and validated an additive English/Dutch cockpit front page, but the real production workflow still defaulted to `disabled`. The official portfolio state was subsequently reconciled to whole shares, so enablement also required exact-current validation against the post-reconciliation authority.

## Decision

Option B was selected and implemented:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

Rollback remains:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: disabled
```

## Implemented change

The `send-report` job in `.github/workflows/send-weekly-report.yml` now carries the explicit job-level feature value. No other production workflow behavior was intentionally changed.

The package also added:

```text
tools/validate_cockpit_wp11_production_enablement.py
tools/run_cockpit_wp11_production_enablement_validation.py
tests/test_cockpit_wp11_production_enablement.py
.github/workflows/validate-cockpit-wp11-production-enablement.yml
control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
control/decisions/COCKPIT_WP11_PRODUCTION_ENABLEMENT_DECISION_20260717.md
```

Two stale cockpit workflows were rebased from the old `260714 / URNM → XBI` fixture to the current `260716 / DFEN → XLV` baseline:

```text
.github/workflows/validate-cockpit-current-runtime.yml
.github/workflows/validate-cockpit-wp08-evidence-review.yml
```

## Exact-current validation

WP11 built a temporary non-persisted overlay from:

```text
base runtime: output/runtime/etf_report_state_20260716_20260717_094728.json
official state: output/etf_portfolio_state.json
whole-share status: compliant
NAV EUR: 107117.94
cash EUR: 2519.05
position count: 8
largest position: SMH
```

Fresh English and Dutch report markdown and disabled/enabled HTML/PDF bundles were rendered only in temporary validation storage.

## Validation evidence

```text
validated_head_sha: 1c02bb4ad5cda51f26011ccde03e49bd0291e99a
WP11 validation run: 29582753816
WP11 validation job: 87892175344
WP11 artifact: 8407711197
WP11 artifact digest: sha256:b483b7157a69939e66c9a7b3624b2401a2211c5ba2db1367b97374aa1b0899a9
current-runtime regression run: 29582753774
WP08 evidence regression run: 29582753837
focused WP11 tests: 3 passed
```

Measured result:

```text
EN disabled front pages: 0
EN enabled front pages: 1
EN PDF pages: 16 -> 17
NL disabled front pages: 0
NL enabled front pages: 1
NL PDF pages: 17 -> 18
classic report body: preserved
small decision cockpit duplicate: false
protected authority hashes: identical
email sent: false
```

## Safety boundary result

```text
production_send: false
portfolio_model_execution: false
official_state_mutation: false
official_trade_ledger_mutation: false
pricing_authority_change: false
report_history_rewrite: false
attachment_count_change: false
manifest_contract_change: false
```

## Stable operating rules

1. The additive cockpit front page is enabled for future real production runs.
2. The full classic English/Dutch report remains the underlying evidence layer.
3. Rollback is one explicit feature value: `disabled`.
4. Invalid values or render failures fail closed to the classic output.
5. A future email send requires a separate explicit production request.
6. No delivery claim is valid without a real manifest and receipt/evidence.
7. Historical delivered reports remain immutable and are not retrofitted with the cockpit front page.

## Closeout

All decision, output-contract, exact-current, whole-share, rollback, bilingual, PDF-page, classic-body, regression and authority-immutability gates passed. The package is closed. No email was sent.
