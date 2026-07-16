# Work Package — WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `decision/cockpit-promotion-review-additive-front-page`
PR: #81

## Layer

```text
decision framework
output contract
operational runbook
```

## Status

```text
status: closed
selected_option: additive_delivery_front_page
production_change: false
promotion_status: not_promoted
merge_commit: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
next_package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

## Purpose and decision

Select the lowest-risk production relationship for the cockpit after WP09 passed all eleven evidence-review dimensions.

Selected:

```text
B. additive cockpit front page inside the current HTML/PDF report
```

This package made a decision only. It did not modify production rendering, PDF generation, email delivery, state, pricing or execution.

## Options considered

```text
A. remain preview-only experiment
B. additive cockpit front page inside the current HTML/PDF report
C. separate cockpit attachment beside the current report
D. replace the current report entry surface while retaining the classic evidence body
E. another refinement cycle
```

## Decision criteria

```text
client decision clarity
premium appearance
preservation of audit evidence
email usability
PDF usability
operational complexity
determinism
failure isolation
rollback path
English/Dutch parity
impact on delivery manifests and attachment contracts
```

## Rationale

- The cockpit passed all eleven WP08 dimensions.
- The classic report remains the strongest evidence and audit layer.
- The current delivery contract sends one complete HTML body and one PDF per language.
- A separate attachment would add manifest and recipient friction without adding evidence value.
- Full replacement would create unnecessary migration and rollback risk.
- Another refinement cycle is not justified because no review blockers remain.
- Delivery-layer injection is the canonical architecture for strict-layout runtime-derived client surfaces.

## Required implementation architecture

```text
source renderer: current runtime inputs; never a committed preview artifact
integration layer: send_report_runtime_html.py and/or runtime/delivery_html_overrides.py
classic report body: preserved intact
email count: unchanged
PDF count: unchanged
attachment contract: unchanged
manifest contract: unchanged
```

## Duplicate-surface rule

When the full cockpit front page is enabled:

```text
suppress the smaller injected Decision cockpit / Besliscockpit
preserve all underlying classic report sections and evidence tables
```

## Feature-gate and rollback rule

```text
feature gate: required
implementation default: disabled
validation mode: explicitly enabled
production enablement: separate closeout required
render failure: unchanged classic production HTML/PDF
rollback: disable one feature flag
```

## WP10 acceptance contract

```text
one cockpit front page appears at the start of EN HTML/PDF
one cockpit front page appears at the start of NL HTML/PDF
classic report body remains complete
smaller decision cockpit is not duplicated
one HTML body and one PDF remain per language
attachment and manifest contracts remain unchanged
standalone HTML remains valid
email HTML remains valid
all eleven WP08 dimensions remain pass
production report validators remain pass
protected authority hashes remain unchanged
feature-disabled output preserves the current classic contract
failure path returns current classic output
email_send: false during validation
promotion_status: not_promoted until explicit implementation closeout
```

## Validation and merge evidence

```text
final_validated_head: d37c43cb1e36f376a58f00c7f4bd469d7133dc8f
promotion_decision_run: 29537562563
WP08_evidence_run: 29537562528
current_runtime_run: 29537562530
validation_conclusion: success
PR: #81
merge_commit: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
```

The decision validator proved that the package contained no unauthorized production renderer, delivery, state, pricing or execution change.

## Safety result

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
