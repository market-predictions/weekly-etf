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
WP29: closed as bilingual macro/thesis alias source verified, preparation-only
WP30: closed as Stage-2 promotion bridge design verified, design-only
WP31: closed as Stage-2 promotion review artifact schema verified, schema/review-artifact validation-only
production_delivery_validation_20260614: closed
fresh_send_validation_20260616: closed

## Active package

WP32: implemented; pending external verification

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
WP29 Codespaces verification: pytest tests/test_macro_thesis_bilingual_aliases.py -> 8 passed
WP29 Codespaces verification: python tools/validate_macro_thesis_bilingual_aliases.py -> MACRO_THESIS_BILINGUAL_ALIASES_OK
WP29 Codespaces verification: macro thesis leakage validator -> passed on 260616 baseline
WP29 Codespaces verification: Dutch language quality validator -> passed on 260616 baseline
WP29 Codespaces verification: macro report surface validator -> ETF_MACRO_REPORT_SURFACE_OK
WP29 Codespaces verification: git diff --check -> clean
control/STAGE2_PROMOTION_BRIDGE_DESIGN.md
tools/validate_stage2_promotion_bridge_design.py
tests/test_stage2_promotion_bridge_design.py
.github/workflows/validate-stage2-promotion-bridge-design.yml
WP30 Codespaces verification: pytest tests/test_stage2_promotion_bridge_design.py -> 7 passed
WP30 Codespaces verification: python tools/validate_stage2_promotion_bridge_design.py -> STAGE2_PROMOTION_BRIDGE_DESIGN_OK
WP30 Codespaces verification: macro thesis leakage validator -> passed on 260616 baseline
WP30 Codespaces verification: macro thesis bilingual aliases validator -> MACRO_THESIS_BILINGUAL_ALIASES_OK
WP30 Codespaces verification: macro report surface validator -> ETF_MACRO_REPORT_SURFACE_OK
WP30 Codespaces verification: git diff --check -> clean
schemas/stage2_promotion_review.schema.json
tools/validate_stage2_promotion_review_schema.py
tests/test_stage2_promotion_review_schema.py
.github/workflows/validate-stage2-promotion-review-schema.yml
WP31 Codespaces verification: pytest tests/test_stage2_promotion_review_schema.py -> 9 passed
WP31 Codespaces verification: python tools/validate_stage2_promotion_review_schema.py -> STAGE2_PROMOTION_REVIEW_SCHEMA_OK
WP31 Codespaces verification: python tools/validate_stage2_promotion_bridge_design.py -> STAGE2_PROMOTION_BRIDGE_DESIGN_OK
WP31 Codespaces verification: macro thesis leakage validator -> passed on 260616 baseline
WP31 Codespaces verification: macro thesis bilingual aliases validator -> MACRO_THESIS_BILINGUAL_ALIASES_OK
WP31 Codespaces verification: macro report surface validator -> ETF_MACRO_REPORT_SURFACE_OK
WP31 Codespaces verification: git diff --check -> clean
tools/validate_stage2_promotion_review_checklist.py
tests/test_stage2_promotion_review_checklist.py
.github/workflows/validate-stage2-promotion-review-checklist.yml

## Recommended next action

Verify WP32 in Codespaces or CI. Use:

```bash
pytest tests/test_stage2_promotion_review_checklist.py
python tools/validate_stage2_promotion_review_checklist.py
python tools/validate_stage2_promotion_review_schema.py
python tools/validate_stage2_promotion_bridge_design.py
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python tools/validate_macro_thesis_bilingual_aliases.py
python tools/validate_macro_report_surface.py
git diff --check
```

If those pass, close WP32. The next roadmap candidate is WP33 — Stage-2 promotion review fixture set.

WP32 remains review-checklist validation only. It does not promote Stage-2 output into production report wording, lane scoring, fundability, portfolio actions, delivery behavior, execution behavior, or historical output mutation.
