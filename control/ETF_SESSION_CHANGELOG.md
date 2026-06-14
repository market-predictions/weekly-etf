# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

## Rules

- Record meaningful architecture, workflow, control-file, validator, runtime, roadmap, and handover-relevant changes.
- Keep entries specific enough that a fresh chat can continue without hidden memory.

---

## 2026-06-13 — WP23 deterministic regime safe-surface helper implemented, pending validation

### Current issue

WP22 validated the safe-surface contract, but there was not yet a helper that could build the narrow DTO and render deterministic English/Dutch review-only text from committed shadow evidence.

### What changed

Added:

```text
runtime/deterministic_regime_client_surface.py
tests/test_deterministic_regime_client_surface_helper.py
control/DETERMINISTIC_REGIME_SAFE_SURFACE_HELPER_STATUS.md
```

Updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

Implementation details:

```text
- added confidence-band helpers
- added a helper that builds the narrow DTO from committed validation/comparison evidence
- added English and Dutch render functions for the DTO
- added tests that pass the helper output through the WP22 validator
- no report integration was added
```

### Validation status

Pending. Run:

```bash
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_client_surface_helper.py -q
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_client_surface_validator.py tests/test_deterministic_regime_client_surface_helper.py -q
```

### Remaining work

After validation passes, record evidence and close WP23. Then consider WP24 as a review-only integration review package.

---

## 2026-06-13 — WP22 deterministic regime client-safe surface validator closed after Codespace validation

WP22 added and validated the client-safe surface validator.

Evidence artifact:

```text
output/macro/validation/deterministic_regime_client_surface_validation_20260613_codespace.json
```

Observed success:

```text
DETERMINISTIC_REGIME_CLIENT_SURFACE_SELF_TEST_OK
DETERMINISTIC_REGIME_CLIENT_SURFACE_OK
7 passed in 0.03s
DETERMINISTIC_REGIME_CLIENT_SURFACE_OK
```
