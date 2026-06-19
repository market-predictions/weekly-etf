# WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-preview-source-provenance`
Layer: output contract + input/state contract
Status: implemented / locally validated

## Purpose

Improve source/provenance clarity and trust-evidence visibility in the preview-only cockpit surface.

## Scope

Preview-only iteration. The cockpit remains not promoted.

## Files changed

```text
runtime/render_cockpit_front_page.py
tests/test_cockpit_visual_state_contracts.py
control/work_packages/WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619_2015.md
```

## Boundaries

```text
production_report_change: none
delivery_change: none
state_change: none
pricing_change: none
runtime_state_change: none
run_manifest_change: none
delivery_manifest_change: none
```

## Expected output

The cockpit preview visibly includes a source/evidence section in English and Dutch, while continuing to write only under `output/cockpit_preview/`.

## Validation evidence

```text
git diff --check: clean
python -m py_compile runtime/render_cockpit_front_page.py: passed
python -m py_compile runtime/build_cockpit_side_by_side_review.py: passed
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_cockpit_visual_state_contracts.py tests/test_cockpit_side_by_side_review.py: 16 passed in 0.20s
python tools/validate_etf_delivery_html_contract.py --output-dir output: ETF_DELIVERY_HTML_CONTRACT_OK for weekly_analysis_pro_260618_04.md and weekly_analysis_pro_nl_260618_04.md
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output: ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK for 260618_04 EN/NL markdown, clean markdown, and delivery HTML files
```
