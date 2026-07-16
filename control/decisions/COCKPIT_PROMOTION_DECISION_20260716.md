# Decision — Cockpit production relationship

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Status: accepted for implementation planning

## Decision

Select an additive cockpit front page inside the existing English and Dutch HTML/PDF report.

```text
selected_option: additive_delivery_front_page
production_change_in_this_package: false
promotion_status: not_promoted
next_package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

## Rejected alternatives

### Remain preview-only

Rejected as the primary path because the cockpit passed all eleven evidence-review dimensions and now provides material client decision value.

### Separate attachment

Rejected because it would add an extra attachment and manifest surface, increase recipient choice friction and complicate delivery verification while preserving no unique evidence advantage.

### Replace the report entry surface

Rejected for this stage because it creates unnecessary migration and rollback risk. The classic report remains the canonical evidence body.

### Another refinement cycle

Rejected because WP09 closed all WP08 blockers and the exact-current review has no remaining failed or partial dimensions.

## Production architecture decision

The cockpit becomes an additive first surface within the current report render pipeline.

```text
email bodies per language: unchanged
PDF files per language: unchanged
attachment count: unchanged
classic report body: preserved
state authority: unchanged
pricing authority: unchanged
```

The front page must be rendered directly from current runtime inputs. Production must not depend on a previously written preview artifact.

## Existing decision-cockpit interaction

When the full front page is enabled, the smaller HTML `Decision cockpit / Besliscockpit` injection is suppressed to avoid duplicate decisions. The underlying classic report sections remain present.

## Feature-gate decision

Implementation is controlled by an explicit feature flag.

```text
implementation default: disabled
validation: explicit enable
failure behavior: unchanged classic output
rollback: disable feature flag
```

Enabling the feature in actual production requires a separate implementation closeout with exact HTML/PDF and delivery-contract evidence.

## Evidence

```text
WP09 PR: #79
WP09 merge: 9b679df825fdc4c7ce37cbdc2474acae6d25d67f
WP09 closeout merge: 009e0f1a910c44b43de0d6c5babf3b1e0eae5cfd
WP08 validation run: 29536333738
current-runtime validation run: 29536333731
review conclusion: ready_for_promotion_decision
blocking findings: 0
promotion status: not_promoted
```

## Next implementation package

```text
WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

That package may implement a feature-gated production render path but may not send email or enable the feature by default.
