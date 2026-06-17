# ETF Review OS — Current State

## Snapshot date

2026-06-17

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP35 are closed. The latest manifest-linked production baseline remains `260616` with run_id `20260616_211726`. WP36 Stage-2 promotion review decision artifact validator fixtures have been implemented as validator-fixture / sample-fixture validation-only and are pending external pytest/validator verification.**

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
WP36: implemented; pending external pytest/validator verification
```

## Evidence

```text
fixtures/stage2_promotion_review_decision/README.md
fixtures/stage2_promotion_review_decision/manifest.json
fixtures/stage2_promotion_review_decision/pass_not_promoted.json
fixtures/stage2_promotion_review_decision/pass_blocked_missing_evidence.json
fixtures/stage2_promotion_review_decision/pass_ready_for_explicit_promotion_decision_not_promoted.json
fixtures/stage2_promotion_review_decision/fail_status_forbidden.json
fixtures/stage2_promotion_review_decision/fail_authority_true.json
fixtures/stage2_promotion_review_decision/fail_design_ref.json
fixtures/stage2_promotion_review_decision/fail_control_bool.json
fixtures/stage2_promotion_review_decision/fail_plumbing_text.json
fixtures/stage2_promotion_review_decision/fail_claim_text.json
fixtures/stage2_promotion_review_decision/fail_extra_property.json
tools/validate_stage2_promotion_review_decision_fixtures.py
tests/test_stage2_promotion_review_decision_fixtures.py
.github/workflows/validate-stage2-promotion-review-decision-fixtures.yml
```

## Immediate next action

Run the WP36 verification commands from `control/NEXT_ACTIONS.md`. If they pass, close WP36 and then consider:

```text
WP37 — Stage-2 promotion review decision artifact validator hardening
```
