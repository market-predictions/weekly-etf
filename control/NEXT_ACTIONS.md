# ETF Review OS — Next Actions

## Current production baseline

```text
baseline: 260612_08
run_id: 20260613_113054
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

---

## Closed packages

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
```

WP24 review artifacts:

```text
control/DETERMINISTIC_REGIME_SAFE_SURFACE_INTEGRATION_REVIEW.md
output/macro/validation/deterministic_regime_safe_surface_integration_review_20260613_000000.json
```

---

## Deterministic macro boundary

Deterministic regime work remains not promoted and not production-integrated.

WP24 allows only a separate future proposal package.

---

## Active package

```text
WP25 — Deterministic regime report integration proposal
```

Current status:

```text
not_started / ready_to_start / proposal-only required
```

Scope:

```text
- propose how the safe-surface helper could be integrated later
- no production report integration in WP25
- no automatic production promotion
- no scoring/fundability changes
- no portfolio mutation
```

Likely start files:

```text
control/DETERMINISTIC_REGIME_SAFE_SURFACE_INTEGRATION_REVIEW.md
control/DETERMINISTIC_REGIME_CLIENT_SAFE_SURFACE_DESIGN.md
control/DETERMINISTIC_REGIME_CLIENT_SURFACE_VALIDATOR_STATUS.md
control/DETERMINISTIC_REGIME_SAFE_SURFACE_HELPER_STATUS.md
runtime/deterministic_regime_client_surface.py
tools/validate_deterministic_regime_client_surface.py
```

---

## Next package after WP25

Do not start this until WP25 proposal closes.

```text
WP26 — Deterministic regime report integration implementation, only if explicitly approved
```

WP26 must remain a separate explicit implementation package.
