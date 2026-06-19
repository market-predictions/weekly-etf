# Handover — WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW

Repository: market-predictions/weekly-etf
Branch: feature/cockpit-front-page-v1

## Package title

WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW

## Layer

operational runbook

## Files changed

- .github/workflows/render-cockpit-preview.yml
- tests/test_cockpit_preview_workflow.py
- control/work_packages/WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW_20260619.md
- control/handovers/HANDOVER_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW_20260619_0709.md

## What was implemented

Added a manual-only GitHub Actions workflow for rendering cockpit preview HTML artifacts.

The workflow:
- uses workflow_dispatch only
- compiles the cockpit renderer
- runs cockpit preview tests
- renders cockpit preview HTML using runtime.render_cockpit_front_page
- uploads output/cockpit_preview/ as a workflow artifact

## What was not implemented

No production report replacement.
No production send-path change.
No email send.
No SMTP secret usage.
No portfolio-state update.
No pricing update.
No trade-ledger update.
No valuation-history update.
No delivery-manifest update.
No committed preview output.
No ETF EU or UCITS work.

## Artifact policy

Uploaded workflow artifact only.

Generated cockpit preview HTML files are not committed to the repository.

## Tests and checks run

python -m py_compile runtime/render_cockpit_front_page.py
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python -m runtime.render_cockpit_front_page --output-dir output --html-only
ls -la output/cockpit_preview/
git diff --check

Result:
- 20 passed in 2.19s
- ETF_DELIVERY_HTML_CONTRACT_OK for EN and NL 260618_03
- ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
- COCKPIT_PREVIEW_OK for EN and NL
- git diff --check clean

## Workflow safety statement

The workflow is manual-only and does not call production delivery scripts, SMTP secrets, report sending, state persistence, pricing, trade-ledger mutation, valuation-history mutation, run manifest writing, or delivery manifest writing.

## Mutation statement

The workflow renders preview files under output/cockpit_preview/ during the workflow run and uploads them as artifacts. It does not commit generated preview output.

## Remaining risks

The workflow still needs to be run manually in GitHub Actions after push to confirm artifact upload behavior in GitHub-hosted CI.

## Recommended next package

WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS

## Commit SHA

To be filled after commit.
