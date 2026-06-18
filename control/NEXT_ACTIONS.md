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
Cockpit-first surface roadmap anchor: recorded

## Active package

WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER: implemented on branch / validation pending
branch: feature/cockpit-front-page-v1
scope: preview renderer only
handover: control/handovers/HANDOVER_COCKPIT_SURFACE_01_PREVIEW_RENDERER_20260618_2238.md

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

## Cockpit-first surface roadmap

Roadmap:

```text
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
```

Initial work package:

```text
control/work_packages/WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_20260618.md
```

Stable decision:

```text
The current production report remains intact. Cockpit-first development proceeds as a forked surface branch and preview lane. Promotion requires an explicit decision.
```

Six-step roadmap:

```text
1. Create isolated branch and preview lane.
2. Add deterministic cockpit renderer.
3. Add manual-only preview workflow.
4. Add visual and state-safety contract tests.
5. Produce side-by-side comparison review.
6. Record explicit promotion decision.
```

Scope boundary:

```text
US ETF report only. ETF EU / UCITS mapping is parked for the parallel ETF EU track.
```

## Recommended next action

Run local validation for WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER on feature/cockpit-front-page-v1 before opening a pull request.

Required validation:

```bash
python -m py_compile runtime/render_cockpit_front_page.py
pytest tests/test_cockpit_front_page_preview.py tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
git diff --check
```

Optional smoke test:

```bash
python -m runtime.render_cockpit_front_page --output-dir output --html-only
ls -la output/cockpit_preview/
```

Do not promote the cockpit into the production report in this package.
