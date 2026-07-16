# ETF Review OS — Next Actions

## Current production baseline

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

```text
URNM: Sell -122.008961 shares; 7.01% -> 2.01%
XBI: Buy +40.491749 shares; 0.00% -> 5.00%
```

## Delivered client baseline

```text
report_en: output/weekly_analysis_pro_260714_03.md
report_nl: output/weekly_analysis_pro_nl_260714_03.md
pdf_en: output/weekly_analysis_pro_260714_03.pdf
pdf_nl: output/weekly_analysis_pro_nl_260714_03.pdf
delivery_workflow_run: 29455717158
inbox_receipt_status: verified_bilingual
```

Do not resend `_03`.

## Validated non-delivered baseline

```text
report_en: output/weekly_analysis_pro_260714_04.md
report_nl: output/weekly_analysis_pro_nl_260714_04.md
html_en: output/weekly_analysis_pro_260714_04_delivery.html
html_nl: output/weekly_analysis_pro_nl_260714_04_delivery.html
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

Do not describe `_04` as delivered.

## Cockpit roadmap status

```text
WP01-WP09: implemented and merged
promotion relationship decision: additive delivery front page
promotion decision PR: #81
promotion decision closeout PR: #82
WP10 implementation PR: #83
promotion_status: not_promoted
```

## WP10 validation result

```text
package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
status: validated_ready_for_enablement_decision
validated_code_head: b2ca4b032793f23f13b0d4557a919623366dc501
final_validation_run: 29541727393
visual_artifact_run: 29542004498
feature_flag: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
feature_default: disabled
production_enablement: false
email_sent: false
promotion_status: not_promoted
```

Acceptance result:

```text
focused_and_existing_tests: 30 passed
production_delivery_html_contract: passed
macro_thesis_surface_leakage: passed
WP08_review_conclusion: ready_for_promotion_decision
WP08_blocking_findings: []
disabled_EN_HTML_byte_identical: true
disabled_NL_HTML_byte_identical: true
enabled_front_page_count_EN: 1
enabled_front_page_count_NL: 1
enabled_front_page_PDF_pages_EN: 1
enabled_front_page_PDF_pages_NL: 1
classic_report_body: preserved
small_decision_cockpit_duplicate: false
standalone_equity_embed: passed
email_equity_CID: passed
email_count_change: false
pdf_count_change: false
attachment_contract_change: false
manifest_contract_change: false
protected_authority_mutation: false
```

Persistent evidence:

```text
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Immediate next package

After PR #83 is merged, create and claim:

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

Decide whether the validated feature gate should be enabled in the real production workflow.

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
.github/workflows/send-weekly-report.yml
send_report_runtime_html.py
runtime/additive_cockpit_front_page.py
```

Check for an active WP11 claim before editing.

### Decision to make

```text
A. retain production default disabled
B. enable the cockpit front page in the real production workflow
C. require one more validate-only production-bundle replay
```

The evidence supports option B technically, but WP11 must make the explicit operational decision and preserve a one-flag rollback.

### Required safeguards

```text
no renderer redesign
no state, pricing or execution change
validate-only exact-current replay before any send
one HTML body and one PDF per language preserved
attachment and manifest contracts preserved
rollback by MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled
no send without separate explicit authorization
no delivery-success claim without receipt/manifest
```

### If enablement is accepted

The only intended production behavior change is an explicit workflow environment value:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

WP11 must validate the enabled production bundle without email before merging. It must not send the `_04` package or mutate state.

### Safety boundary

```text
production_send: false during WP11 validation
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
```

## Subsequent report-surface audit

After the cockpit production path is closed, inspect client-facing `_04` wording for internal or stale terms, including `shadow engine`. Handle confirmed leakage in a separate report-surface cleanup package using existing macro/thesis validators.

## Governance cleanup candidate

A separate governance pass may reconcile stale `planned` labels in `control/SYSTEM_INDEX.md` for cockpit assets that are already implemented. Do not combine that documentation cleanup with WP11 production enablement.
