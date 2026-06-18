# ETF Review OS — Current State

## Snapshot date

2026-06-18

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP42 are closed. Report Quality Patch 260617 and its Dutch localization bugfix are verified. Latest verified production baseline is `260617` with run_id `20260618_172254`.**

## Latest verified production baseline recorded in control

```text
requested_close_date: 2026-06-17
run_id: 20260618_172254
report_token: 260617
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## Closed package status

```text
WP16: closed
WP17: closed
WP18: closed
WP19: closed
WP20: closed as not_promoted
WP21: closed as design-only
WP22: closed as manually validated
WP23: closed as manually validated
WP24: closed as review-only
WP25: closed as proposal-only
WP26: closed as manually validated
WP27: closed as visual QA passed
WP28: closed as leakage firewall verified
WP29: closed as bilingual alias source verified, preparation-only
WP30: closed as bridge design verified, design-only
WP31: closed as review schema verified, schema-only
WP32: closed as review checklist verified, checklist-only
WP33: closed as review fixture set verified, fixture-only
WP34: closed as decision artifact design verified, design-only
WP35: closed as decision artifact schema verified, schema-only
WP36: closed as decision artifact validator fixtures verified, fixture-only
WP37: closed as decision artifact validator hardening verified, validator-hardening only
WP38: closed as decision sample generation gate verified, validation-only
WP39: closed as decision dry-run builder verified, validation-only
WP40: closed as explicit decision artifact design review verified, design-review only
WP41: closed as decision non-production fixture gate verified, validation-only
WP42: closed as explicit control-layer package design verified, design-only
Report Quality Patch 260617: closed as client-facing report-quality patch verified
Report Quality Patch 260617 post-close Dutch localization bugfix: closed as workflow-validated
```

## In-progress / pending verification

```text
None
```

## Evidence

```text
Fresh report review examples: weekly_analysis_pro_260617.pdf and weekly_analysis_pro_nl_260617.pdf
runtime/polish_runtime_reports.py
runtime/rotation_render_tables.py
tests/test_report_decision_clarity.py
tests/test_report_weight_basis_labels.py
tests/test_report_bilingual_takeaway_parity.py
Report Quality Patch 260617 Codespaces verification: pytest tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py -> 10 passed
Report Quality Patch 260617 Codespaces verification: python tools/validate_macro_report_surface.py -> ETF_MACRO_REPORT_SURFACE_OK
Report Quality Patch 260617 Codespaces verification: python tools/validate_macro_thesis_bilingual_aliases.py -> MACRO_THESIS_BILINGUAL_ALIASES_OK
Report Quality Patch 260617 Codespaces verification: python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output -> ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK on 260617 EN/NL markdown, clean markdown and delivery HTML files
Report Quality Patch 260617 Codespaces verification: python tools/validate_etf_delivery_html_contract.py -> ETF_DELIVERY_HTML_CONTRACT_OK for weekly_analysis_pro_260617.md and weekly_analysis_pro_nl_260617.md
Report Quality Patch 260617 Codespaces verification: python tools/validate_etf_dutch_language_quality.py -> ETF_DUTCH_LANGUAGE_QUALITY_OK
Report Quality Patch 260617 Codespaces verification: git diff --check -> clean
Workflow #256 failure root cause: Dutch localization blocked cockpit term `thesisfit` before write.
Bugfix: replaced `thesisfit` with `aansluiting op de thesis` and added a regression assertion.
Workflow #257: Send weekly ETF Pro report succeeded on main after the Dutch localization bugfix.
Run manifest: output/run_manifests/weekly_etf_run_manifest_2026-06-17_20260618_172254.json
Delivery manifest: output/delivery/weekly_etf_delivery_manifest_2026-06-17_20260618_172254.json
English report: output/weekly_analysis_pro_260617_03.md
Dutch report: output/weekly_analysis_pro_nl_260617_03.md
```

## Immediate next action

Inspect the generated 260617_03 PDF/HTML client surface and confirm that the Decision cockpit, bilingual main takeaway parity, weight-basis note, and softened action wording are visible and useful. Do not claim inbox receipt; delivery evidence remains delivery-layer only.
