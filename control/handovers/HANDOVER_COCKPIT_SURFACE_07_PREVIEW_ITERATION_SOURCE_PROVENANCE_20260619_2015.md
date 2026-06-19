# Handover — WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-preview-source-provenance`
Status: implemented / locally validated

## Summary

This package improves the preview-only cockpit source/provenance layer.

Changed files:

```text
runtime/render_cockpit_front_page.py
tests/test_cockpit_visual_state_contracts.py
control/work_packages/WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619_2015.md
```

## What changed

The cockpit preview now includes a visible source/evidence section in English and Dutch.

The section records:

```text
runtime state source
valuation history source
pricing audit reference when available
macro pack reference when available
run-manifest reference when available
preview-only status
no delivery claim
not promoted to production
```

## Boundary

This package does not promote the cockpit into production.

This package does not change delivery behavior, state, pricing, trade ledger, valuation history, runtime state, run manifests, delivery manifests, production report artifacts, or the production send workflow.

## Validation evidence

Codespaces validation completed successfully:

```text
git diff --check: clean
python -m py_compile runtime/render_cockpit_front_page.py: passed
python -m py_compile runtime/build_cockpit_side_by_side_review.py: passed
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_cockpit_visual_state_contracts.py tests/test_cockpit_side_by_side_review.py: 16 passed in 0.20s
python tools/validate_etf_delivery_html_contract.py --output-dir output: ETF_DELIVERY_HTML_CONTRACT_OK for weekly_analysis_pro_260618_04.md and weekly_analysis_pro_nl_260618_04.md
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output: ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK for 260618_04 EN/NL markdown, clean markdown, and delivery HTML files
```

## Remaining work

- Pull the validation-status commits from the branch.
- Confirm local status is clean and only intended files are part of the branch diff.
- Open PR: `Improve cockpit preview source provenance`.

## Next recommended package

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```
