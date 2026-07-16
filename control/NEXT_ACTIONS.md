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

## Closed packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION: closed
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION: closed
WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT: closed
WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW: closed
```

## Promotion decision closeout

```text
selected_option: additive_delivery_front_page
PR: #81
merge_commit: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
promotion_decision_run: 29537562563
WP08_evidence_run: 29537562528
current_runtime_run: 29537562530
production_change: false
promotion_status: not_promoted
```

Selected route:

```text
add one cockpit front page inside the existing English and Dutch HTML/PDF report
preserve the complete classic report body
preserve one email and one PDF per language
preserve attachment and manifest contracts
suppress the smaller duplicate decision cockpit when enabled
feature-gate the integration
default the feature to disabled
fail closed to unchanged classic output
```

Rejected routes:

```text
preview-only as primary route: leaves validated client value unused
separate attachment: adds manifest and recipient friction
full replacement: unnecessary migration and rollback risk
another iteration: no remaining WP08 blockers
```

## Immediate package

Create and claim:

```text
WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

### Layer

```text
output contract
operational runbook
```

### Purpose

Implement the selected additive cockpit front page in the delivery HTML/PDF pipeline without enabling it by default and without sending email.

### Required architecture

```text
render source: current runtime inputs, not a committed preview artifact
integration layer: send_report_runtime_html.py and/or runtime/delivery_html_overrides.py
classic report body: preserved
small decision cockpit: suppressed only when full front page is enabled
email count: unchanged
PDF count: unchanged
attachment count: unchanged
manifest contract: unchanged
```

### Feature gate

```text
flag required: true
recommended name: MRKT_RPRTS_COCKPIT_FRONT_PAGE
accepted values: disabled | enabled
implementation default: disabled
validation enablement: explicit
production enablement: separate closeout required
render failure: unchanged classic output
rollback: disable flag
```

No truthy/falsey aliases should be accepted unless deliberately normalized and tested.

### Required implementation checks

1. Disabled mode produces the current classic delivery contract.
2. Enabled mode adds exactly one cockpit front page at the beginning of EN HTML/PDF.
3. Enabled mode adds exactly one cockpit front page at the beginning of NL HTML/PDF.
4. Classic report content remains complete after the front page.
5. The smaller `Decision cockpit / Besliscockpit` is not duplicated in enabled mode.
6. Standalone HTML equity rendering remains valid.
7. Email HTML validation remains valid.
8. PDF generation remains valid.
9. One PDF and one email body remain per language.
10. Attachment and manifest semantics remain unchanged.
11. The WP08 v2 evidence review remains all-pass.
12. Protected authority hashes remain unchanged.
13. Validation sends no email.
14. A planted cockpit render exception returns unchanged classic output and records a diagnostic result.

### Expected implementation evidence

```text
feature-disabled HTML/PDF comparison
feature-enabled HTML/PDF artifacts
bilingual parity proof
no-duplicate decision surface proof
classic body preservation proof
fail-closed planted failure proof
protected authority before/after hashes
production validator results
WP08 v2 all-pass result
email_sent: false
promotion_status: not_promoted
```

### Safety boundary

```text
production_enablement: false
production_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
```

## Following package

If WP10 succeeds, create a separate implementation-promotion closeout package that decides whether to enable the feature in the real production workflow. Do not combine production enablement with WP10 implementation validation.

## Subsequent report-surface audit

After the cockpit integration path is stable, inspect client-facing `_04` wording for internal or stale terms, including `shadow engine`. Handle confirmed leakage in a separate report-surface cleanup package using existing macro/thesis validators.

## Governance cleanup candidate

A separate governance pass should reconcile stale `planned` labels in `control/SYSTEM_INDEX.md` for the already implemented cockpit renderer, workflow and output directory. Do not mix that cleanup into WP10 production integration.
