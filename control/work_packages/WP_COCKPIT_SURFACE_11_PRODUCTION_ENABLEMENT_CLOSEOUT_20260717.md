# Work Package — WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp11-production-enablement-closeout`

## Layer

```text
decision framework
output contract
operational runbook
```

## Status

```text
status: claimed
selected_option: enable_validated_additive_front_page
production_send: false
promotion_status: enablement_under_validation
```

## Purpose

Enable the already validated additive cockpit front page in the real Weekly ETF production workflow without sending a report during this package.

## Authority basis

```text
WP10 PR: #83
WP10 merge: 23328a9494fb5a2183eacd328365310dbf583af6
feature flag: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
WP10 status: validated_ready_for_enablement_decision
all eleven WP08 dimensions: pass
```

## Decision

Select option B:

```text
enable MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled in .github/workflows/send-weekly-report.yml
```

Technical and visual evidence already proves one bilingual front page, preserved classic report content, no duplicate decision cockpit and unchanged delivery semantics.

## Exact intended production change

Add one job-level environment value to the existing production workflow:

```yaml
jobs:
  send-report:
    env:
      MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

No renderer redesign, state change, pricing change, model-execution change, recipient change, attachment change or manifest change is permitted.

## Validate-only acceptance

Before merge, a read-only workflow must prove against exact current `_04` artifacts:

1. the production workflow contains the exact explicit value `enabled`;
2. EN and NL HTML each contain exactly one delivery cockpit front page;
3. EN and NL PDF each gain exactly one front page and render successfully;
4. the complete classic report remains present;
5. the smaller Decision cockpit / Besliscockpit is not duplicated;
6. standalone HTML equity embedding remains valid;
7. email HTML equity CID behavior remains valid;
8. production report validators remain green;
9. all eleven WP08 dimensions remain pass;
10. protected authority files remain byte-identical;
11. no SMTP function is invoked and `email_sent=false`;
12. rollback remains one-line: set the workflow value to `disabled`.

## Failure rule

Any validation failure blocks merge. No send fallback is permitted. Runtime rendering itself remains fail closed to unchanged classic output.

## Safety boundary

```text
production_send: false
report_generation_request: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
recipient_change: false
attachment_contract_change: false
manifest_contract_change: false
```

## Closeout result

If all gates pass and this package merges:

```text
production_workflow_feature_value: enabled
production_delivery_executed: false
next_real_report: uses additive cockpit front page
rollback: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled
```

No delivery success may be claimed until a future real report run produces its own positive manifest and inbox receipt evidence.