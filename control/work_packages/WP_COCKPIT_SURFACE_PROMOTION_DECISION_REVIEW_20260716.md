# Work Package — WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `decision/cockpit-promotion-review-additive-front-page`

## Layer

```text
decision framework
output contract
operational runbook
```

## Status

```text
claimed
production_change: false
promotion_status: not_promoted
```

## Purpose

Select the lowest-risk production relationship for the cockpit after WP09 passed all eleven evidence-review dimensions.

This package makes a decision and defines the next implementation contract. It does not modify production rendering, PDF generation, email delivery, state, pricing or execution.

## Authority inputs

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_STATUS_20260716.md
control/work_packages/WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION_20260716.md
control/work_packages/WP_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT_20260716.md
control/decisions/COCKPIT_WP08_EVIDENCE_REVIEW_DECISION_20260716.md
control/decisions/COCKPIT_WP09_REFINEMENT_DECISION_20260716.md
control/handovers/HANDOVER_COCKPIT_SURFACE_09_CURRENT_RUNTIME_CLIENT_SURFACE_REFINEMENT_20260716.md
send_report.py
send_report_runtime_html.py
runtime/delivery_html_overrides.py
runtime/render_cockpit_front_page.py
```

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

## Selected option

```text
B. additive cockpit front page inside the current HTML/PDF report
```

## Rationale

- The current cockpit passed all eleven WP08 dimensions.
- The classic report remains the strongest evidence and audit layer and must remain intact.
- The current production contract sends one complete HTML body and one PDF per language.
- A separate attachment would change attachment and manifest behavior without improving the decision path.
- Full replacement would create unnecessary migration and rollback risk.
- Another refinement cycle is not justified because the evidence review has no blockers.
- Delivery-layer injection is already the canonical architecture for strict-layout, runtime-derived client surfaces.

## Required implementation architecture

The additive front page must be injected at the delivery HTML layer after runtime state is available and before final email/PDF validation.

```text
source renderer: runtime/render_cockpit_front_page.py
production integration layer: send_report_runtime_html.py and/or runtime/delivery_html_overrides.py
classic report body: preserved intact
email count: unchanged
PDF count: unchanged
attachments: unchanged
manifest semantics: unchanged
```

The implementation must not read a committed preview file as production authority. It must render the front-page fragment directly from the same current runtime inputs used by the validated preview.

## Duplicate-surface rule

The full cockpit front page and the existing smaller `Decision cockpit / Besliscockpit` must not create redundant decision surfaces.

The implementation package must choose and test one deterministic rule:

```text
when full cockpit front page is enabled:
  suppress the smaller injected decision cockpit
  preserve all underlying classic report sections and evidence tables
```

## Feature-gate and rollback rule

The implementation must be feature-gated and fail closed:

```text
default during implementation: disabled
validation mode: enabled explicitly
render failure: return unchanged classic production HTML/PDF
rollback: disable one feature flag; no report/state migration required
```

The feature gate may not silently default to enabled until the implementation package has exact-artifact evidence and an explicit promotion closeout.

## Acceptance contract for implementation

The next package must prove:

```text
one cockpit front page appears at the start of EN HTML/PDF
one cockpit front page appears at the start of NL HTML/PDF
classic report body remains complete
smaller decision cockpit is not duplicated
one HTML body and one PDF remain per language
attachment and manifest contract remains unchanged
standalone HTML remains valid
email HTML remains valid
all eleven WP08 dimensions remain pass
production report validators remain pass
protected authority hashes remain unchanged
feature-disabled output equals current classic output contract
failure path returns current classic output
email_send: false during validation
promotion_status: not_promoted until explicit implementation closeout
```

## Next package

```text
WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
```

## Safety boundary

```text
production_render_change: false in this decision package
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
promotion_status: not_promoted
```
