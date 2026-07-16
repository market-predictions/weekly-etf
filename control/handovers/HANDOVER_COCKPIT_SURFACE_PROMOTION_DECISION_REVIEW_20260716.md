# Handover — Cockpit promotion decision review

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `decision/cockpit-promotion-review-additive-front-page`
Status: decision recorded / validation pending

## Claim status

No open promotion decision PR or promotion branch was found at claim time.

## Decision

```text
selected_option: additive_delivery_front_page
promotion_status: not_promoted
production_change_in_this_package: false
next_package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

## Why this option

The additive front page gives the validated cockpit a client-facing role without weakening the classic evidence body or changing the current one-email/one-PDF delivery contract.

It is lower risk than a separate attachment because it does not create extra attachment, manifest or receipt surfaces. It is lower risk than replacement because the current report body and rollback path remain intact.

## Required implementation contract

```text
render directly from current runtime inputs
inject at delivery HTML/PDF layer
preserve complete classic report body
suppress smaller duplicate decision cockpit when enabled
feature flag required
implementation default disabled
validation enablement explicit
render failure returns unchanged classic output
rollback by disabling feature flag
no email send during implementation validation
```

## Files in decision package

```text
control/work_packages/WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW_20260716.md
control/decisions/COCKPIT_PROMOTION_DECISION_20260716.md
control/decisions/cockpit_promotion_decision_20260716.json
control/handovers/HANDOVER_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW_20260716.md
```

## Evidence basis

```text
WP09 merge: 9b679df825fdc4c7ce37cbdc2474acae6d25d67f
WP09 closeout merge: 009e0f1a910c44b43de0d6c5babf3b1e0eae5cfd
WP08 validation: 29536333738
current-runtime validation: 29536333731
review conclusion: ready_for_promotion_decision
blocking findings: 0
all eleven review dimensions: pass
```

## Safety boundary

```text
production_render_change: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
promotion_status: not_promoted
```

## Next package

```text
WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

## Closeout fields

```text
validation_run: pending
PR: pending
merge_commit: pending
```
