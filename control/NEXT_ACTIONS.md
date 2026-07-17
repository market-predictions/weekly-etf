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
cockpit_production_feature: enabled
```

The delivered report predates both the whole-share reconciliation and cockpit production enablement. Current shares and cash come from the official portfolio state, not from the delivered report tables. Historical reports remain immutable.

## Completed packages

### Whole-share state contract

```text
package: WP_ETF_WHOLE_SHARE_STATE_CONTRACT
PR: #85
merge_commit: d5532ea15801a3888633ccb824797ab254305433
validation_run: 29580018310
reconciliation_commit: 50b93740efbed537ed9d0daed6e1d88ce912be1e
nav_drift_eur: 0.00
status: closed
```

The official state contains eight whole-share positions. `DFEN` is closed and €582.53 of fractional/policy-close value was transferred to cash.

### Cockpit production enablement

```text
package: WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
PR: #87
feature: MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled
rollback: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled
validation_run: 29582753816
current_runtime_regression_run: 29582753774
wp08_regression_run: 29582753837
status: closed_no_send
```

The exact-current no-send replay proved one front page per language, one added PDF page per language, preserved classic report bodies, no duplicate small cockpit, whole-share official authority and identical protected hashes. No email was sent.

## Immediate next package

Create and claim:

```text
WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP
```

### Layer

```text
output contract
operational runbook
```

### Purpose

Remove confirmed client-facing internal and workflow-derived language from future English and Dutch report surfaces without changing analytical conclusions or machine authority.

Known targets include:

```text
shadow engine
review-only process narration where it dominates client copy
double punctuation in position review lines
raw internal override/release terminology where a client-safe label exists
stale pre-reconciliation wording that implies obsolete holdings authority
```

### Required start sequence

Read:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/decisions/COCKPIT_WP11_PRODUCTION_ENABLEMENT_DECISION_20260717.md
control/handovers/HANDOVER_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT_20260717.md
control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
PROMPT_MASTER_WEEKLY_ETF_REVIEW.md
PROMPT_PRO_REPORT.md
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/scrub_etf_client_surface.py
runtime/client_facing_sanitizer.py
```

Check for an active cleanup-package claim before editing.

### Required safeguards

```text
no change to portfolio state or trade ledger
no pricing-authority change
no macro/thesis authority promotion
no lane-scoring or fundability change
no portfolio action or execution change
no historical report mutation
no email send
preserve EN/NL numeric parity
preserve clickable ticker and PDF/HTML contracts
preserve enabled cockpit front page
```

## Subsequent production proof

After the language-cleanup package closes, a fresh report and email require a separate explicit production request.

That future run should prove in a real delivered package:

1. all holdings and guarded trade deltas remain integer;
2. the cockpit front page appears once in English and once in Dutch;
3. the full classic report remains attached and present in the HTML body;
4. the report is generated from the whole-share official state;
5. delivery is supported by an actual run manifest and receipt/evidence.

## Separate governance cleanup

A later governance-only package may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with report wording or production delivery.
