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

baseline: 260617
reports: weekly_analysis_pro_260617_03.md and weekly_analysis_pro_nl_260617_03.md
run_manifest: output/run_manifests/weekly_etf_run_manifest_2026-06-17_20260618_172254.json
delivery_manifest: output/delivery/weekly_etf_delivery_manifest_2026-06-17_20260618_172254.json

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

## Active package

None

## Latest Report Quality Patch 260617 evidence

pytest tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py -> 10 passed
python tools/validate_macro_report_surface.py -> ETF_MACRO_REPORT_SURFACE_OK
python tools/validate_macro_thesis_bilingual_aliases.py -> MACRO_THESIS_BILINGUAL_ALIASES_OK
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output -> ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK on 260617 EN/NL markdown, clean markdown and delivery HTML files
python tools/validate_etf_delivery_html_contract.py -> ETF_DELIVERY_HTML_CONTRACT_OK for weekly_analysis_pro_260617.md and weekly_analysis_pro_nl_260617.md
python tools/validate_etf_dutch_language_quality.py -> ETF_DUTCH_LANGUAGE_QUALITY_OK
git diff --check -> clean
workflow #257 -> Send weekly ETF Pro report succeeded on main
run manifest -> output/run_manifests/weekly_etf_run_manifest_2026-06-17_20260618_172254.json
delivery manifest -> output/delivery/weekly_etf_delivery_manifest_2026-06-17_20260618_172254.json

## Recommended next action

Inspect the generated 260617_03 PDF/HTML client surface.

The QA should verify only the client-facing surface:

1. Decision cockpit appears near the top in English and Dutch.
2. Main takeaway has equivalent meaning in English and Dutch.
3. Weight-basis note appears near the final action table.
4. Hold-with-override explanation is understandable.
5. Harsh role wording is absent.
6. Delivery status wording remains evidence-bound.

Do not claim inbox receipt unless separate inbox-receipt evidence exists.
Do not create another Stage-2 package unless a roadmap consolidation review identifies a concrete need.
