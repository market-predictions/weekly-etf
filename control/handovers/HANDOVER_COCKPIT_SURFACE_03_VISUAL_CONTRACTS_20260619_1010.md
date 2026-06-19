# Handover — WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS

Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-visual-contracts`

## Package title

`WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS`

## Layer

`output contract + operational runbook`

## Files changed

```text
control/work_packages/WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS_20260619.md
tests/test_cockpit_visual_state_contracts.py
control/handovers/HANDOVER_COCKPIT_SURFACE_03_VISUAL_CONTRACTS_20260619_1010.md
```

## What was implemented

Added focused visual/state-safety contract tests for the cockpit preview lane.

The tests cover:

- required cockpit front-page components in English and Dutch;
- preview output remaining under `output/cockpit_preview/`;
- classic report surfaces not being overwritten;
- portfolio state, valuation history, trade ledger, recommendation scorecard, pricing pointer, runtime pointer, run-manifest pointer, and delivery manifest fixture not being mutated;
- cockpit preview HTML not claiming delivery or email success;
- generated cockpit files using preview-only `_cockpit_` names rather than production report names.

## What was not implemented

No production report replacement.
No production send-path change.
No email send.
No SMTP secret usage.
No portfolio-state update.
No pricing update.
No trade-ledger update.
No valuation-history update.
No runtime-state update.
No run-manifest update.
No delivery-manifest update.
No committed preview output.
No ETF EU / UCITS work.
No cockpit promotion.

## Tests/checks run

Not run in this connector environment.

Required next validation in Codespaces:

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

## Visual contract statement

The new tests assert that the generated cockpit preview includes the required English and Dutch cockpit components and the preview-only disclaimer surface.

## State-safety statement

The new tests use a temporary output fixture and compare protected file bytes before and after rendering to verify no mutation of portfolio, valuation, ledger, scorecard, pricing pointer, runtime pointer, run-manifest pointer, or delivery manifest fixture files.

## Delivery-safety statement

The new tests assert that delivery manifests are not changed and cockpit preview HTML does not claim SMTP success, delivery manifest success, inbox receipt, or email send success.

## Mutation statement

The implementation adds tests and control/handover files only. It does not change renderer behavior, production report rendering, send workflow behavior, pricing, portfolio state, trade ledger, valuation history, runtime state, run manifests, or delivery manifests.

## Remaining risks

The test suite still needs to be run in Codespaces.
The manual cockpit preview workflow artifact should remain recorded as WP02 evidence, not as report delivery evidence.
Visual QA beyond deterministic surface assertions remains for the side-by-side review package.

## Recommended next package

After Codespaces validation passes:

```text
WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW
```

That package should compare current classic report artifacts against cockpit preview artifacts without promotion.

## Commit SHA

To be filled after local validation/PR closeout if needed.
