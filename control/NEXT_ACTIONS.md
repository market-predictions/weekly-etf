# ETF Review OS — Next Actions

## Current production baseline

baseline: 260616
run_id: 20260616_211726
requested_close_date: 2026-06-16
workflow_status: workflow_success
workflow_conclusion: success
total_portfolio_value_eur: 108100.61
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
unresolved_tickers: []

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

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
WP28: closed as macro/thesis leakage firewall verified
production_delivery_validation_20260614: closed
fresh_send_validation_20260616: closed

## Active package

WP29: implemented; pending external verification

## Latest evidence

tools/validate_etf_macro_thesis_surface_leakage.py
tests/test_macro_thesis_shadow_leakage_contract.py
control/DECISION_LOG.md
control/CURRENT_STATE.md
WP28 Codespaces verification: pytest tests/test_macro_thesis_shadow_leakage_contract.py -> 6 passed
WP28 Codespaces verification: macro thesis leakage, report content, delivery HTML, and Dutch language validators -> passed on 260616 baseline
WP28 Codespaces verification: git diff --check -> clean
config/macro_thesis_bilingual_aliases.yml
tools/validate_macro_thesis_bilingual_aliases.py
tests/test_macro_thesis_bilingual_aliases.py
.github/workflows/validate-macro-thesis-bilingual-aliases.yml

## Recommended next action

Verify WP29 in Codespaces or CI. Use:

```bash
pytest tests/test_macro_thesis_bilingual_aliases.py
python tools/validate_macro_thesis_bilingual_aliases.py
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python tools/validate_etf_dutch_language_quality.py --output-dir output
python tools/validate_macro_report_surface.py
git diff --check
```

If those pass, close WP29. The next roadmap candidate is WP30 — Design-only Stage-2 promotion bridge.

WP29 remains preparation-only: input/state contract plus output contract. It does not change production report output, portfolio actions, lane scoring, fundability, delivery behavior, or historical output files.
