# ETF Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

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
```

WP22 evidence:

```text
output/macro/validation/deterministic_regime_client_surface_validation_20260613_codespace.json
control/DETERMINISTIC_REGIME_CLIENT_SURFACE_VALIDATOR_STATUS.md
```

---

## Deterministic macro boundary

Deterministic regime work remains not promoted and not production-integrated.

---

## Active package

```text
WP23 — Deterministic regime safe-surface helper
```

Current status:

```text
not_started / ready_to_start / helper-only required
```

Scope:

```text
- create a narrow helper that can build the safe DTO and render safe EN/NL text
- use the WP21 design and WP22 validator
- no production report integration
- no automatic production promotion
- no scoring/fundability changes
- no portfolio mutation
```

Likely start files:

```text
control/DETERMINISTIC_REGIME_CLIENT_SAFE_SURFACE_DESIGN.md
control/DETERMINISTIC_REGIME_CLIENT_SURFACE_VALIDATOR_STATUS.md
tools/validate_deterministic_regime_client_surface.py
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
```

---

## Next package after WP23

Do not start this until WP23 helper tests are green and recorded.

```text
WP24 — Deterministic regime safe-surface integration review
```

WP24 must remain review-only unless separately approved.
