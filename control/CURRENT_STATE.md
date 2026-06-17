# ETF Review OS — Current State

## Snapshot date

2026-06-17

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP33 are closed. The latest manifest-linked production baseline remains `260616` with run_id `20260616_211726`. WP34 Stage-2 promotion review decision artifact design has been implemented as decision-artifact design-only and is pending external pytest/validator verification.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-16
run_id: 20260616_211726
report_token: 260616
english_report_path: output/weekly_analysis_pro_260616.md
dutch_report_path: output/weekly_analysis_pro_nl_260616.md
pricing_audit_path: output/pricing/price_audit_2026-06-16_20260616_211726.json
runtime_state_path: output/runtime/etf_report_state_20260616_20260616_211726.json
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-16_20260616_211726.json
total_portfolio_value_eur: 108100.61
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
unresolved_tickers: []
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## Closed package status

```text
WP16: closed
WP17: closed
WP18: closed
WP19: closed
WP20: closed as not_promoted
WP21: closed as design-only
WP22: closed as manually validated
WP23: closed as manually validated
WP24: closed as review-only
WP25: closed as proposal-only
WP26: closed as manually validated
WP27: closed as visual QA passed
WP28: closed as macro/thesis leakage firewall verified
WP29: closed as bilingual macro/thesis alias source verified, preparation-only
WP30: closed as Stage-2 promotion bridge design verified, design-only
WP31: closed as Stage-2 promotion review artifact schema verified, schema/review-artifact validation-only
WP32: closed as Stage-2 promotion review checklist validator verified, review-checklist validation-only
WP33: closed as Stage-2 promotion review fixture set verified, fixture-set design and validation-only
production_delivery_validation_20260614: closed as workflow_success
fresh_send_validation_20260616: closed as workflow_success
```

## In-progress / pending verification

```text
WP34: implemented; pending external pytest/validator verification
```

## Evidence

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_VISUAL_QA_STATUS.md
output/macro/validation/deterministic_regime_report_visual_qa_validation_20260613_codespace.json
control/PRODUCTION_DELIVERY_VALIDATION_STATUS_20260614.md
control/run_queue/weekly_etf_report_request_20260616_231500.md
output/run_manifests/weekly_etf_run_manifest_2026-06-16_20260616_211726.json
output/delivery/weekly_etf_delivery_manifest_2026-06-16_20260616_211726.json
tools/validate_etf_macro_thesis_surface_leakage.py
tests/test_macro_thesis_shadow_leakage_contract.py
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
WP32 Codespaces verification: pytest tests/test_stage2_promotion_review_checklist.py -> 11 passed
WP32 Codespaces verification: python tools/validate_stage2_promotion_review_checklist.py -> STAGE2_PROMOTION_REVIEW_CHECKLIST_OK
WP32 Codespaces verification: python tools/validate_stage2_promotion_review_schema.py -> STAGE2_PROMOTION_REVIEW_SCHEMA_OK
WP32 Codespaces verification: python tools/validate_stage2_promotion_bridge_design.py -> STAGE2_PROMOTION_BRIDGE_DESIGN_OK
WP32 Codespaces verification: macro thesis leakage validator -> passed on 260616 baseline
WP32 Codespaces verification: macro thesis bilingual aliases validator -> MACRO_THESIS_BILINGUAL_ALIASES_OK
WP32 Codespaces verification: macro report surface validator -> ETF_MACRO_REPORT_SURFACE_OK
WP32 Codespaces verification: git diff --check -> clean
fixtures/stage2_promotion_review/README.md
fixtures/stage2_promotion_review/manifest.json
fixtures/stage2_promotion_review/pass_ready_for_review_not_promoted.json
fixtures/stage2_promotion_review/pass_not_ready_missing_evidence.json
fixtures/stage2_promotion_review/fail_authority_true.json
fixtures/stage2_promotion_review/fail_promoted_status.json
fixtures/stage2_promotion_review/fail_missing_bilingual_aliases.json
fixtures/stage2_promotion_review/fail_raw_driver_id_text.json
fixtures/stage2_promotion_review/fail_fundable_claim_text.json
tools/validate_stage2_promotion_review_fixtures.py
tests/test_stage2_promotion_review_fixtures.py
.github/workflows/validate-stage2-promotion-review-fixtures.yml
WP33 Codespaces verification: pytest tests/test_stage2_promotion_review_fixtures.py -> 10 passed
WP33 Codespaces verification: python tools/validate_stage2_promotion_review_fixtures.py -> STAGE2_PROMOTION_REVIEW_FIXTURES_OK
WP33 Codespaces verification: python tools/validate_stage2_promotion_review_checklist.py -> STAGE2_PROMOTION_REVIEW_CHECKLIST_OK
WP33 Codespaces verification: python tools/validate_stage2_promotion_review_schema.py -> STAGE2_PROMOTION_REVIEW_SCHEMA_OK
WP33 Codespaces verification: python tools/validate_stage2_promotion_bridge_design.py -> STAGE2_PROMOTION_BRIDGE_DESIGN_OK
WP33 Codespaces verification: macro thesis leakage validator -> passed on 260616 baseline
WP33 Codespaces verification: macro thesis bilingual aliases validator -> MACRO_THESIS_BILINGUAL_ALIASES_OK
WP33 Codespaces verification: macro report surface validator -> ETF_MACRO_REPORT_SURFACE_OK
WP33 Codespaces verification: git diff --check -> clean
control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md
tools/validate_stage2_promotion_review_decision_artifact_design.py
tests/test_stage2_promotion_review_decision_artifact_design.py
.github/workflows/validate-stage2-promotion-review-decision-artifact-design.yml
```

## Immediate next action

Run the WP34 verification commands from `control/NEXT_ACTIONS.md`. If they pass, close WP34 and then consider:

```text
WP35 — Stage-2 promotion review decision artifact schema
```
