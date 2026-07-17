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
client_language_contract: active_pending_PR88_merge
```

The delivered report predates the whole-share reconciliation, cockpit production enablement and internal-language cleanup. Current shares and cash come from the official portfolio state, not from historical report tables. Historical reports remain immutable.

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
status: closed_no_send
```

The exact-current no-send replay proved one front page per language, one added PDF page per language, preserved classic report bodies, no duplicate small cockpit, whole-share official authority and identical protected hashes.

### Report-surface internal-language cleanup

```text
package: WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP
PR: #88
validation_run: 29590932038
validation_job: 87919550815
focused_tests: 30 passed
EN findings: 18 -> 0
NL findings: 6 -> 0
numeric_parity: preserved
markdown_link_parity: preserved
historical_reports: byte_unchanged
email_sent: false
status: closed_pending_merge
```

Persistent evidence:

```text
control/evidence/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_EVIDENCE_20260717.json
```

## Immediate next action

No new development package is required before production proof.

A fresh report and email require a separate explicit user authorization. Do not create a run-queue request as part of PR #88.

When authorized, the fresh production run should prove:

1. all official holdings and guarded trade deltas remain integer;
2. the cockpit front page appears exactly once in English and once in Dutch;
3. the full classic report remains present behind the front page;
4. the new internal-language clean gate passes for Markdown and delivery HTML;
5. numbers, percentages and ticker links remain coherent across EN/NL output;
6. pricing lineage and run manifests pass;
7. a delivery manifest is written;
8. inbox receipt is confirmed before claiming delivery success.

## Separate governance cleanup

A later governance-only package may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with production delivery.
