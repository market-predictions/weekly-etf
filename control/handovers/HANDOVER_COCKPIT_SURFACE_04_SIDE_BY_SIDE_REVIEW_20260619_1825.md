# Handover — WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-side-by-side-review`
Status: implemented / validation pending in Codespaces

## Summary

This package adds deterministic side-by-side review generation for the US Weekly ETF cockpit preview lane.

Added files:

```text
runtime/build_cockpit_side_by_side_review.py
tests/test_cockpit_side_by_side_review.py
control/work_packages/WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW_20260619_1825.md
```

## Output contract

The builder writes review-only artifacts under:

```text
output/cockpit_review/
```

Expected generated files:

```text
weekly_etf_cockpit_side_by_side_review_<token>.md
weekly_etf_cockpit_side_by_side_review_<token>.html
weekly_etf_cockpit_side_by_side_review_nl_<token>.md
weekly_etf_cockpit_side_by_side_review_nl_<token>.html
weekly_etf_cockpit_side_by_side_review_<token>.json
```

## No-promotion status

```text
promotion_status: not_promoted
```

The cockpit remains preview-only. This package does not promote the cockpit into production and does not change production report generation or delivery behavior.

## Mutation boundary

The implementation is designed to write only to `output/cockpit_review/` and to leave state, pricing, runtime, run-manifest, delivery, cockpit-preview, and classic production report artifacts unchanged.

## Required validation

Run in Codespaces:

```bash
python -m py_compile runtime/render_cockpit_front_page.py
python -m py_compile runtime/build_cockpit_side_by_side_review.py
python -m py_compile tests/test_cockpit_side_by_side_review.py

pytest tests/test_cockpit_front_page_preview.py \
       tests/test_cockpit_preview_workflow.py \
       tests/test_cockpit_visual_state_contracts.py \
       tests/test_cockpit_side_by_side_review.py \
       tests/test_delivery_html_decision_cockpit.py \
       tests/test_pdf_surface_decision_cockpit.py \
       tests/test_report_decision_clarity.py \
       tests/test_report_weight_basis_labels.py \
       tests/test_report_bilingual_takeaway_parity.py

python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output

python -m runtime.render_cockpit_front_page --output-dir output --html-only
python -m runtime.build_cockpit_side_by_side_review --output-dir output

ls -la output/cockpit_preview/
ls -la output/cockpit_review/

git diff --check
```

Then clean generated files before commit/PR closeout:

```bash
git clean -fd __pycache__ runtime/__pycache__ tests/__pycache__ tools/__pycache__ output/cockpit_preview output/cockpit_review
git status --short
```

## Remaining work

- Run the required validation locally.
- If green, open PR: `Add cockpit side-by-side review artifacts`.
- After merge, continue with `WP_COCKPIT_SURFACE_05_PROMOTION_DECISION_REVIEW`.
