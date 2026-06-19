# Handover — WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-review-after-provenance`
Status: implemented / validation pending in Codespaces

## Summary

This package updates the cockpit review layer after WP07 improved source/provenance clarity.

Changed files:

```text
runtime/build_cockpit_side_by_side_review.py
tests/test_cockpit_side_by_side_review.py
control/work_packages/WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260619_2105.md
```

## What changed

The review builder now records the WP07 source/provenance iteration in metadata and English/Dutch review artifacts.

The review states that the cockpit now exposes Source & evidence / Bronnen en bewijs, including runtime-state, valuation-history, pricing-audit, macro-pack, and run-manifest references when available.

## Boundary

This package is review-only. The cockpit remains not promoted. The classic production report remains authoritative.

No production report, send workflow, state, pricing, runtime, run-manifest, or delivery-manifest files are intentionally changed.

## Validation to run

```bash
git diff --check

python -m py_compile runtime/render_cockpit_front_page.py
python -m py_compile runtime/build_cockpit_side_by_side_review.py

pytest tests/test_cockpit_front_page_preview.py \
       tests/test_cockpit_preview_workflow.py \
       tests/test_cockpit_visual_state_contracts.py \
       tests/test_cockpit_side_by_side_review.py

python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output

python -m runtime.build_cockpit_side_by_side_review --output-dir output
ls -la output/cockpit_review/
```

Before PR, clean generated files and caches:

```bash
git clean -fd __pycache__ runtime/__pycache__ tests/__pycache__ tools/__pycache__ output/cockpit_preview output/cockpit_review
git status --short
```

## Next recommended package

```text
WP_COCKPIT_SURFACE_09_PROMOTION_REVIEW_OR_FURTHER_ITERATION_DECISION
```
