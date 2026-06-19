# WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-front-page-v1`

## Package title

`WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW`

## Layer

`operational runbook`

## Status

`blocked / workflow-file write unavailable in connector environment`

## Purpose

Add a manual-only GitHub Actions workflow that renders cockpit preview artifacts for the US Weekly ETF report.

The workflow must not replace the production report, send email, update portfolio state, update pricing, update trade ledger, update valuation history, update delivery manifests, or claim delivery success.

## Blocker

The work package was claimed, but implementation could not proceed in this connector-only environment because the attempted write to:

```text
.github/workflows/render-cockpit-preview.yml
```

was blocked by the GitHub connector safety checks.

No workflow file was created.
No production report behavior was changed.
No preview artifact was committed.
No validation was run for WP02.

## Authority and boundaries

The cockpit preview workflow is operational preview infrastructure only.

It may render preview HTML artifacts under:

```text
output/cockpit_preview/
```

It must not mutate:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/pricing/
output/runtime/
output/run_manifests/
output/delivery/
```

## Artifact policy

`upload workflow artifact only`

Generated cockpit preview artifacts must not be committed to the repository in this package.

## Expected implementation files when unblocked

```text
.github/workflows/render-cockpit-preview.yml
tests/test_cockpit_preview_workflow.py
control/handovers/HANDOVER_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW_20260619_<HHMM>.md
```

## Validation required before closeout

```bash
python -m py_compile runtime/render_cockpit_front_page.py
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python -m runtime.render_cockpit_front_page --output-dir output --html-only
ls -la output/cockpit_preview/
git diff --check
```

## Non-goals

- No production report replacement.
- No production send-path change.
- No email send.
- No SMTP secret usage.
- No portfolio-state mutation.
- No pricing mutation.
- No trade-ledger mutation.
- No valuation-history mutation.
- No delivery-manifest mutation.
- No ETF EU / UCITS work.
