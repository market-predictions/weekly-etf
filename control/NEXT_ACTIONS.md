# ETF Review OS — Next Actions

## Current production baseline recorded in control

baseline: 260617
run_id: 20260618_172254
requested_close_date: 2026-06-17
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

## Fresh report review baseline

baseline: 260618_03 client-surface PDF QA
reports: weekly_analysis_pro_260618_03.pdf and weekly_analysis_pro_nl_260618_03.pdf
client_surface_status: Decision cockpit / Besliscockpit visible in final PDF surface

## Closed packages

WP16: closed
WP17: closed
WP18: closed
WP19: closed
WP20: closed
WP21: closed
WP22: closed
WP23: closed
WP24: closed
WP25: closed
WP26: closed
WP27: closed
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
PDF Surface Patch — Decision cockpit visible in final PDF/HTML: closed as client-surface verified

## Active package

None

## Latest PDF Surface Patch evidence

The PDF Surface Patch is closed. Decision cockpit / Besliscockpit visibility is verified in the 260618_03 PDFs.

- English 260618_03 PDF visibly shows "Decision cockpit" near the top, directly under Portfolio Action Snapshot.
- Dutch 260618_03 PDF visibly shows "Besliscockpit" near the top, directly under Portefeuille-acties.
- Main takeaway remains aligned between English and Dutch.
- Weight-basis note remains visible near the final action table.
- Hold-with-override explanation remains visible near the final action table.
- Dutch forbidden term "thesisfit" is absent; Dutch uses "aansluiting op de thesis".

Focused tests/checks referenced:

```text
pytest tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_etf_dutch_language_quality.py
python tools/validate_etf_delivery_html_contract.py
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
git diff --check
```

## Recommended next action

No new Stage-2 package. Next work should be normal report QA / roadmap consolidation only if a concrete client-facing issue is identified.

Do not claim inbox receipt unless separate inbox-receipt evidence exists.
