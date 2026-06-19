# WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-visual-contracts`

## Package title

`WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS`

## Layer

`output contract + operational runbook`

## Status

`claimed / in_progress`

## Purpose

Add focused visual/state-safety contract tests for the US Weekly ETF cockpit preview lane.

WP03 proves, with deterministic tests, that the cockpit preview lane remains separate from the production report and does not damage production state, delivery evidence, or existing report output.

## Authority and boundaries

The cockpit preview surface remains preview-only.

It may write generated preview artifacts only under:

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

## Expected implementation files

```text
tests/test_cockpit_visual_state_contracts.py
control/handovers/HANDOVER_COCKPIT_SURFACE_03_VISUAL_CONTRACTS_20260619_<HHMM>.md
```

## Validation required before closeout

```bash
python -m py_compile runtime/render_cockpit_front_page.py
python -m py_compile tests/test_cockpit_visual_state_contracts.py
pytest tests/test_cockpit_front_page_preview.py tests/test_cockpit_preview_workflow.py tests/test_cockpit_visual_state_contracts.py tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
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
- No runtime-state mutation.
- No run-manifest mutation.
- No delivery-manifest mutation.
- No report delivery claim.
- No inbox receipt claim.
- No ETF EU / UCITS work.
