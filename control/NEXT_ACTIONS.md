# ETF Review OS — Next Actions

## Current production baseline recorded in control

baseline: 260616
run_id: 20260616_211726
requested_close_date: 2026-06-16
workflow_status: workflow_success
workflow_conclusion: success

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

## Fresh report review baseline

baseline: 260617
examples: weekly_analysis_pro_260617.pdf and weekly_analysis_pro_nl_260617.pdf

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

## Active package

Report Quality Patch 260617: implemented; pending external verification

## Latest report-quality patch files

runtime/polish_runtime_reports.py
runtime/rotation_render_tables.py
tests/test_report_decision_clarity.py
tests/test_report_weight_basis_labels.py
tests/test_report_bilingual_takeaway_parity.py

## Verification commands

```bash
pytest tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_macro_report_surface.py
python tools/validate_macro_thesis_bilingual_aliases.py
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python tools/validate_etf_delivery_html_contract.py
python tools/validate_etf_dutch_language_quality.py
git diff --check
```

If a validator file is not present locally, report the missing validator and run the available validators without mutating output artifacts.

## Recommended next action

Verify the report-quality patch in Codespaces or CI. If verification passes, regenerate or inspect a fresh report and perform client-grade QA.

Do not create another Stage-2 package unless a roadmap consolidation review identifies a concrete need.
