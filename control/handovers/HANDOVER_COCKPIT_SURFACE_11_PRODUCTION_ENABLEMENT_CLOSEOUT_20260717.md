# Handover — WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp11-production-enablement-closeout`
Status: claimed / implementation in progress

## Decision

```text
selected_option: enable_validated_additive_front_page
workflow_value: MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled
production_send: false
```

## Intended change

Only `.github/workflows/send-weekly-report.yml` may receive production behavior change: one explicit job-level feature value. The validated WP10 renderer is reused unchanged.

## Required evidence

```text
exact current EN/NL render: passed
exact current EN/NL PDF: passed
front page count: 1 per language
classic report body: preserved
small decision cockpit duplicate: false
production validators: passed
WP08 all eleven dimensions: pass
protected authority hashes: identical
email_sent: false
rollback: set flag to disabled
```

## Safety boundary

No report request, email send, model execution, state mutation, pricing change, recipient change, attachment change or manifest change is authorized.

## Closeout fields

```text
validation_run: pending
PR: pending
merge_commit: pending
production_delivery_receipt: none_expected
```