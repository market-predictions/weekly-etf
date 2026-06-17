# ETF Review OS — Current State

## Snapshot date

2026-06-17

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP35 are closed. The latest manifest-linked production baseline remains `260616` with run_id `20260616_211726`. WP35 Stage-2 promotion review decision artifact schema is verified and closed as schema/design validation-only.**

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
WP34: closed as Stage-2 promotion review decision artifact design verified, decision-artifact design-only
WP35: closed as Stage-2 promotion review decision artifact schema verified, schema/design validation-only
production_delivery_validation_20260614: closed as workflow_success
fresh_send_validation_20260616: closed as workflow_success
```

## In-progress / pending verification

```text
None
```

## Evidence

```text
schemas/stage2_promotion_review_decision.schema.json
tools/validate_stage2_promotion_review_decision_schema.py
tests/test_stage2_promotion_review_decision_schema.py
.github/workflows/validate-stage2-promotion-review-decision-schema.yml
WP35 Codespaces verification: pytest tests/test_stage2_promotion_review_decision_schema.py -> 12 passed
WP35 Codespaces verification: python tools/validate_stage2_promotion_review_decision_schema.py -> STAGE2_PROMOTION_REVIEW_DECISION_SCHEMA_OK
WP35 Codespaces verification: python tools/validate_stage2_promotion_review_decision_artifact_design.py -> STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN_OK
WP35 Codespaces verification: python tools/validate_stage2_promotion_review_fixtures.py -> STAGE2_PROMOTION_REVIEW_FIXTURES_OK
WP35 Codespaces verification: python tools/validate_stage2_promotion_review_checklist.py -> STAGE2_PROMOTION_REVIEW_CHECKLIST_OK
WP35 Codespaces verification: python tools/validate_stage2_promotion_review_schema.py -> STAGE2_PROMOTION_REVIEW_SCHEMA_OK
WP35 Codespaces verification: python tools/validate_stage2_promotion_bridge_design.py -> STAGE2_PROMOTION_BRIDGE_DESIGN_OK
WP35 Codespaces verification: macro thesis leakage validator -> passed on 260616 baseline
WP35 Codespaces verification: macro thesis bilingual aliases validator -> MACRO_THESIS_BILINGUAL_ALIASES_OK
WP35 Codespaces verification: macro report surface validator -> ETF_MACRO_REPORT_SURFACE_OK
WP35 Codespaces verification: git diff --check -> clean
```

## Immediate next action

Consider the next roadmap package:

```text
WP36 — Stage-2 promotion review decision artifact validator fixtures
```
