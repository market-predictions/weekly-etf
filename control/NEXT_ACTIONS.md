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

## Validated review baseline

```text
report_en: output/weekly_analysis_pro_260714_04.md
report_nl: output/weekly_analysis_pro_nl_260714_04.md
html_en: output/weekly_analysis_pro_260714_04_delivery.html
html_nl: output/weekly_analysis_pro_nl_260714_04_delivery.html
validation: output/validation/etf_report_freshness_260714_04.json
email_sent: false
```

Do not describe `_04` as delivered. It is non-sending review evidence.

## Closed packages

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH: closed
WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP: closed
PR #70 merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
PR #72 merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
correction_runbook_validation_run: 29520607344
post_execution_consistency_run: 29520608204
```

## Canonical correction runbook

```text
workflow: .github/workflows/resend-corrected-post-execution-report.yml
modes: validate_only | recover_no_send | send
contract: runtime/post_execution_correction_runbook.py
```

Operating rules:

1. `send` is manual-only and requires `confirm_correction_resend` in both the request file and workflow dispatch.
2. A send must use a new correction suffix and cannot overwrite an existing report package.
3. Production mail configuration uses only the established `MRKT_RPRTS_*` contract.
4. Delivery evidence is the persisted positive `DELIVERY_OK` text receipt and the English/Dutch `*_delivery_manifest.txt` names recorded in it.
5. `recover_no_send` strips mail configuration, uses render-only asset generation and may not invoke the mail delivery entrypoint.
6. Recovery restores original bytes and fails if existing historical report artifacts would change.
7. Every operation proves current official state and trade-ledger hashes unchanged.
8. Historical manifest hashes are historical immutability evidence, not a requirement that future legitimate production state retain the same hash.

No send or recovery mode was executed during the cleanup package.

## Recommended next package

Select and claim the next explicit product-roadmap package:

```text
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER
```

### Immediate purpose

Resume validation of the isolated cockpit-first preview renderer against the current runtime and delivery contracts without changing the production report.

### Required start sequence

Read:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
control/work_packages/WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_20260618.md
```

Then inspect only the minimum relevant execution files, beginning with:

```text
runtime/render_cockpit_front_page.py
.github/workflows/render-cockpit-preview.yml
```

### Safety boundary

```text
production_promotion: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
preview_output_only: output/cockpit_preview/
```

The next package must assess the existing preview implementation before adding new product-surface work. Do not mix cockpit validation with correction-runbook changes.
