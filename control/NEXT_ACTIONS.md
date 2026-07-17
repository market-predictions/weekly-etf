# ETF Review OS — Next Actions

## Current authoritative baseline

```text
latest_report_close: 2026-07-16
latest_report_run_id: 20260717_094728
latest_delivered_report: output/weekly_analysis_pro_260716.md
latest_delivered_report_nl: output/weekly_analysis_pro_nl_260716.md
official_portfolio_state: output/etf_portfolio_state.json
whole_share_status: compliant
nav_eur: 107117.94
cash_eur: 2519.05
```

The delivered report predates the later whole-share reconciliation. Current shares and cash come from the official portfolio state, not from the delivered report tables.

## Completed blocker

```text
package: WP_ETF_WHOLE_SHARE_STATE_CONTRACT
PR: #85
merge_commit: d5532ea15801a3888633ccb824797ab254305433
validation_run: 29580018310
focused_tests: 4 passed
reconciliation_commit: 50b93740efbed537ed9d0daed6e1d88ce912be1e
nav_drift_eur: 0.00
status: closed
```

The official state now contains eight whole-share positions. `DFEN` is closed and €582.53 of fractional/policy-close value is held as cash. No report was resent and no cockpit feature was enabled.

## Immediate next package

Create and claim:

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

### Layer

```text
decision framework
output contract
operational runbook
```

### Purpose

Decide whether the validated additive cockpit front page should be enabled in the real production workflow.

### Required start sequence

Read:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/decisions/COCKPIT_PROMOTION_DECISION_20260716.md
control/work_packages/WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
control/handovers/HANDOVER_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
control/decisions/ETF_WHOLE_SHARE_STATE_CONTRACT_DECISION_20260717.md
output/runtime/etf_whole_share_reconciliation_20260716_20260717_094728.json
.github/workflows/send-weekly-report.yml
send_report_runtime_html.py
runtime/additive_cockpit_front_page.py
```

Check for an active WP11 claim before editing.

### Decision options

```text
A. retain production default disabled
B. enable the cockpit front page in the real production workflow
C. require one more validate-only production-bundle replay
```

Technical evidence supports option B, but WP11 must make the explicit decision.

### Required safeguards

```text
use current whole-share-compliant official state
no portfolio model execution during validation
no official state or trade-ledger mutation
no pricing-authority change
validate-only exact-current enabled replay before any send
one HTML body and one PDF per language preserved
attachment and manifest contracts preserved
rollback by MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled
no send without separate explicit authorization
no delivery-success claim without receipt or manifest
```

### Intended production change if enabled

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

The feature default remains disabled until WP11 closes. WP11 must not resend an older report package.

## After WP11

1. Generate the next fresh report from the reconciled whole-share official state.
2. Verify that all rendered holdings and trade deltas remain integer.
3. Inspect client-facing wording for internal terms such as `shadow engine` in a separate report-surface cleanup package.
4. Reconcile stale `planned` labels in `control/SYSTEM_INDEX.md` in a separate governance-only package.
