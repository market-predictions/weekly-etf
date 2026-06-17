# ETF Review OS — Current State

## Snapshot date

2026-06-17

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 through WP41 are closed. WP42 has been implemented and is pending external verification. Latest baseline remains `260616` with run_id `20260616_211726`.**

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
WP28: closed as leakage firewall verified
WP29: closed as bilingual alias source verified, preparation-only
WP30: closed as bridge design verified, design-only
WP31: closed as review schema verified, schema-only
WP32: closed as review checklist verified, checklist-only
WP33: closed as review fixture set verified, fixture-only
WP34: closed as decision artifact design verified, design-only
WP35: closed as decision artifact schema verified, schema-only
WP36: closed as decision artifact validator fixtures verified, fixture-only
WP37: closed as decision artifact validator hardening verified, validator-hardening only
WP38: closed as decision sample generation gate verified, validation-only
WP39: closed as decision dry-run builder verified, validation-only
WP40: closed as explicit decision artifact design review verified, design-review only
WP41: closed as decision non-production fixture gate verified, validation-only
```

## In-progress / pending verification

```text
WP42: implemented; pending external verification
```

## Evidence

```text
control/STAGE2_CONTROL_LAYER_PACKAGE_DESIGN.md
tools/wp42_validator.py
tests/test_wp42_control_layer_design.py
```

## Immediate next action

Run the WP42 verification commands from `control/NEXT_ACTIONS.md`. If they pass, close WP42 and then consider WP43.
