# Handover — WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-preview-source-provenance`
Status: implemented / validation pending in Codespaces

## Summary

This package improves the preview-only cockpit source/provenance layer.

Changed files:

```text
runtime/render_cockpit_front_page.py
tests/test_cockpit_source_provenance.py
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

## Validation to run

```bash
git diff --check

python -m py_compile runtime/render_cockpit_front_page.py
python -m py_compile runtime/build_cockpit_side_by_side_review.py

pytest tests/test_cockpit_front_page_preview.py \
       tests/test_cockpit_preview_workflow.py \
       tests/test_cockpit_visual_state_contracts.py \
       tests/test_cockpit_side_by_side_review.py \
       tests/test_cockpit_source_provenance.py

python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
```

Optional smoke test:

```bash
python -m runtime.render_cockpit_front_page --output-dir output --html-only
ls -la output/cockpit_preview/
```

Clean generated files before commit/PR if present:

```bash
git clean -fd __pycache__ runtime/__pycache__ tests/__pycache__ tools/__pycache__ output/cockpit_preview output/cockpit_review
git status --short
```

## Next recommended package

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```
