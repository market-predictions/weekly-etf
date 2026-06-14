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

---

## Active package

```text
WP26 — Deterministic regime report integration implementation
```

Current status:

```text
implemented / pending validation evidence
```

Status file:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_IMPLEMENTATION_STATUS.md
```

Run these validation commands:

```bash
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_report_surface_integration.py -q
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_client_surface_validator.py tests/test_deterministic_regime_client_surface_helper.py tests/test_deterministic_regime_report_surface_integration.py -q
PYTHONPATH=. python tools/validate_macro_report_surface.py --self-test
PYTHONPATH=. python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json
```

Expected result:

```text
all tests pass
ETF_MACRO_REPORT_SURFACE_OK
```

---

## Next package after WP26

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```
