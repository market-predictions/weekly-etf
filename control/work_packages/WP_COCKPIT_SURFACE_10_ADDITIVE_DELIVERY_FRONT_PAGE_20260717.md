# Work Package — WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp10-additive-delivery-front-page`

## Layer

```text
output contract
operational runbook
```

## Status

```text
status: claimed
production_enablement: false
promotion_status: not_promoted
email_send: false
```

## Purpose

Implement the promotion decision selected in `COCKPIT_PROMOTION_DECISION_20260716`:

```text
selected_option: additive_delivery_front_page
```

The implementation must add one runtime-derived cockpit front page to the beginning of the existing English and Dutch delivery HTML/PDF while preserving the complete classic report body and all current delivery semantics.

This package implements and validates the path. It does not enable the path by default and does not send email.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/decisions/COCKPIT_PROMOTION_DECISION_20260716.md
control/decisions/cockpit_promotion_decision_20260716.json
runtime/render_cockpit_front_page.py
send_report_runtime_html.py
runtime/delivery_html_overrides.py
send_report.py
.github/workflows/send-weekly-report.yml
```

Check for an active WP10 branch or pull request before editing.

## Decision framework

The front page improves the client entry surface but does not replace the classic report evidence layer.

```text
client entry surface: additive cockpit front page
classic report evidence body: preserved intact
small Decision cockpit / Besliscockpit: suppressed only when full front page is enabled
production enablement: separate closeout decision
```

## Input/state contract

Render directly from current runtime authority, never from a committed cockpit preview artifact.

```text
runtime state pointer: output/runtime/latest_etf_report_state_path.txt
valuation history: output/etf_valuation_history.csv
macro pack: current runtime-linked macro policy pack
pricing audit pointer: output/pricing/latest_price_audit_path.txt
run manifest pointer: output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

Preserve current authority precedence:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

## Output contract

### Disabled mode

With the feature disabled, output must preserve the current classic delivery contract without a cockpit front page.

### Enabled mode

With the feature enabled:

```text
exactly one cockpit front page at the start of EN email HTML
exactly one cockpit front page at the start of EN PDF HTML
exactly one cockpit front page at the start of NL email HTML
exactly one cockpit front page at the start of NL PDF HTML
complete classic report body follows unchanged in semantic content
small Decision cockpit / Besliscockpit is not injected
one HTML body per language remains
one PDF per language remains
attachment and manifest semantics remain unchanged
standalone HTML remains valid
```

The delivery surface must use client-facing delivery wording. It must not expose preview-only labels such as:

```text
Preview lane
Preview-only cockpit
No delivery claim
Not promoted to production
Voorbeeldcockpit
Geen leveringsclaim
Niet naar productie gepromoveerd
```

## Feature gate

Use exactly:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
```

Rules:

```text
missing value -> disabled
implementation default -> disabled
validation enablement -> explicit enabled
other values -> fail closed to unchanged classic output
production enablement -> separate closeout package
rollback -> set disabled
```

Do not accept implicit truthy or falsey aliases.

## Failure isolation

Any front-page render or injection exception must:

1. return the unchanged classic HTML;
2. retain the current smaller decision cockpit behavior;
3. emit a machine-readable diagnostic status;
4. avoid modifying output authority, state, pricing, ledger or delivery manifests.

A planted-failure regression is mandatory.

## Exact implementation files

Expected narrow scope:

```text
runtime/render_cockpit_front_page.py
runtime/additive_cockpit_front_page.py
send_report_runtime_html.py
tests/test_cockpit_wp10_additive_delivery_front_page.py
.github/workflows/validate-cockpit-wp10-additive-front-page.yml
control/work_packages/WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
control/handovers/HANDOVER_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
```

Existing report or delivery files may only be changed when required by the narrow integration contract.

## Required tests

1. Feature flag parser accepts only `disabled` and `enabled`.
2. Missing flag behaves as `disabled`.
3. Disabled injection returns byte-identical classic HTML.
4. Enabled injection adds exactly one delivery front page before the classic body.
5. English and Dutch front pages use client-facing delivery wording.
6. Preview-only labels do not appear in enabled delivery output.
7. The smaller decision cockpit is suppressed only after successful full-front-page injection.
8. Classic body markers remain present and in original order.
9. Planted renderer failure returns unchanged classic output and a fallback diagnostic.
10. Existing delivery HTML validator remains green.
11. Existing report freshness/equity contracts remain green.
12. Existing WP08 evidence review remains all-pass.
13. Protected authority hashes remain byte-identical.
14. No email is sent.

## Validation workflow

Create a read-only workflow that:

- installs focused render dependencies;
- snapshots protected authority files and pointer targets;
- compiles modified modules;
- runs WP10 plus existing cockpit/report regressions;
- renders exact current `_04` delivery assets with the feature disabled and enabled without calling the send path;
- validates EN/NL HTML and PDF generation;
- verifies one front page, no duplicate small cockpit, complete classic body, valid embedded equity graph and unchanged attachment/manifest shape;
- executes a planted failure and proves fail-closed output;
- reruns WP08 v2;
- proves protected hashes unchanged;
- uploads evidence artifacts;
- records `email_sent: false` and `promotion_status: not_promoted`.

## Acceptance

```text
implementation_status: validated_ready_for_enablement_decision
feature_default: disabled
enabled_validation: passed
fail_closed_validation: passed
classic_report_body: preserved
small_decision_cockpit_duplicate: false
email_count_change: false
pdf_count_change: false
attachment_contract_change: false
manifest_contract_change: false
protected_authority_mutation: false
email_sent: false
promotion_status: not_promoted
```

Passing this package does not enable the feature in the production send workflow. A separate implementation-promotion closeout must decide production enablement.

## Safety boundary

```text
production_send: false
production_enablement: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
report_markdown_rewrite: false
```
