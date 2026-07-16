# Handover — WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp10-additive-delivery-front-page`
Status: claimed / implementation in progress

## Authority

```text
promotion decision PR: #81
promotion decision merge: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
promotion closeout PR: #82
promotion closeout merge: 61f9a4b27d5e656d566c5679b237b5b31a8f0a47
selected_option: additive_delivery_front_page
promotion_status: not_promoted
```

## Intended implementation

- add a runtime-derived delivery front-page fragment;
- inject it at the start of delivery HTML/PDF only when the explicit feature flag is enabled;
- preserve disabled output;
- suppress the smaller decision cockpit only after successful full-front-page injection;
- fail closed to unchanged classic output;
- preserve EN/NL, PDF, attachment, manifest and authority contracts.

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

Pending implementation, exact-current validation, artifact inspection, PR and merge evidence.
