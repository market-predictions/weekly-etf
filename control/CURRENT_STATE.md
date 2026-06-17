# ETF Review OS — Current State

## Snapshot date

2026-06-17

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP38 are closed. WP39 has been implemented and is pending external verification. Latest baseline remains `260616` with run_id `20260616_211726`.**

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
WP30: closed as Stage-2 bridge design verified, design-only
WP31: closed as Stage-2 review schema verified, schema-only
WP32: closed as Stage-2 review checklist verified, checklist-only
WP33: closed as Stage-2 review fixture set verified, fixture-only
WP34: closed as Stage-2 decision artifact design verified, design-only
WP35: closed as Stage-2 decision artifact schema verified, schema-only
WP36: closed as Stage-2 decision artifact validator fixtures verified, fixture-only
WP37: closed as Stage-2 decision artifact validator hardening verified, validator-hardening only
WP38: closed as Stage-2 decision sample generation gate verified, validation-only
```

## In-progress / pending verification

```text
WP39: implemented; pending external verification
```

## Evidence

```text
tools/build_stage2_promotion_review_decision_dry_run.py
tools/validate_stage2_promotion_review_decision_dry_run.py
tests/test_stage2_promotion_review_decision_dry_run.py
.github/workflows/validate-stage2-decision-dry-run.yml
```

## Immediate next action

Run the WP39 verification commands from `control/NEXT_ACTIONS.md`. If they pass, close WP39 and then consider WP40.
