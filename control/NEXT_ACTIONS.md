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
WP25: closed as proposal-only
```

WP25 proposal artifacts:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_PROPOSAL.md
output/macro/validation/deterministic_regime_report_integration_proposal_20260613_000000.json
```

---

## Deterministic macro boundary

Deterministic regime work remains not promoted and not production-integrated.

WP25 allows only a separately approved future implementation package.

---

## Active package

```text
WP26 — Deterministic regime report integration implementation
```

Current status:

```text
not_started / requires_explicit_user_approval / implementation package
```

Scope if approved:

```text
- implement the WP25 proposal with minimal report-surface changes
- use only the narrow safe DTO
- validate exact rendered EN/NL text with the WP22 validator
- no automatic production promotion beyond review-only surface text
- no scoring/fundability changes
- no portfolio mutation
```

Likely start files:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_PROPOSAL.md
runtime/macro_report_surface.py
runtime/deterministic_regime_client_surface.py
tools/validate_macro_report_surface.py
tools/validate_deterministic_regime_client_surface.py
```

---

## Next package after WP26

Do not start this until WP26 is explicitly approved, implemented, and validated.

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```
