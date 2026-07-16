# Handover — WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp10-additive-delivery-front-page`
PR: #83
Status: implementation applied / exact-current validation in progress

## Authority

```text
promotion decision PR: #81
promotion decision merge: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
promotion closeout PR: #82
promotion closeout merge: 61f9a4b27d5e656d566c5679b237b5b31a8f0a47
selected_option: additive_delivery_front_page
promotion_status: not_promoted
```

## Implemented files

```text
runtime/additive_cockpit_front_page.py
send_report_runtime_html.py
tests/test_cockpit_wp10_additive_delivery_front_page.py
tools/validate_cockpit_wp10_delivery_integration.py
.github/workflows/validate-cockpit-wp10-additive-front-page.yml
control/work_packages/WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
control/handovers/HANDOVER_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
```

No temporary patch workflow remains in the pull-request diff.

## Applied implementation

- render a delivery-specific cockpit fragment directly from current runtime inputs;
- use only the explicit `MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled` feature values;
- default a missing flag to `disabled`;
- return the unchanged classic delivery path for invalid values or render/injection failures;
- inject exactly one front page at the start of HTML/PDF after client-facing sanitization;
- suppress the smaller decision cockpit only after successful full-front-page injection;
- preserve the smaller decision cockpit in disabled and fallback modes;
- use client-facing English and Dutch wording without preview/promotion labels;
- emit a structured `COCKPIT_FRONT_PAGE` diagnostic line;
- preserve classic report content, bilingual delivery shape and existing send semantics.

## Validation architecture

The read-only WP10 workflow must validate the exact current `_04` report pair in both disabled and enabled modes without calling the send path. It must also run the planted failure, existing report validators, WP08 v2 and protected-authority hash comparison.

Expected evidence path:

```text
output/wp10_validation/cockpit_wp10_additive_delivery_front_page_260714.json
```

## Safety boundary

```text
feature_default: disabled
production_enablement: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
```

## Completion evidence

Pending workflow results, generated artifact inspection, final PR head and merge evidence.
