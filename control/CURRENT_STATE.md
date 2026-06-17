# ETF Review OS — Current State

## Snapshot date

2026-06-17

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP37 are closed. WP38 sample generation gate has been implemented and is pending external verification. Latest baseline remains `260616` with run_id `20260616_211726`.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-16
run_id: 20260616_211726
report_token: 260616
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
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
WP36: closed as Stage-2 promotion review decision artifact validator fixtures verified, validator-fixture / sample-fixture validation-only
WP37: closed as Stage-2 promotion review decision artifact validator hardening verified, validator-hardening only
```

## In-progress / pending verification

```text
WP38: implemented; pending external verification
```

## Evidence

```text
tools/build_stage2_promotion_review_decision_sample.py
tools/validate_stage2_promotion_review_decision_sample_gate.py
tests/test_stage2_promotion_review_decision_sample_gate.py
.github/workflows/validate-stage2-promotion-review-decision-sample-gate.yml
```

## Immediate next action

Run the WP38 verification commands from `control/NEXT_ACTIONS.md`. If they pass, close WP38 and then consider:

```text
WP39 — Stage-2 promotion review decision dry-run artifact builder
```
