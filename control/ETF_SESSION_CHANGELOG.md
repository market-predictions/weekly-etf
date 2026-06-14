# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

## Rules

- Record meaningful architecture, workflow, control-file, validator, runtime, roadmap, and handover-relevant changes.
- Keep entries specific enough that a fresh chat can continue without hidden memory.

---

## 2026-06-13 — WP24 deterministic regime safe-surface integration review closed

WP24 reviewed the WP21/WP22/WP23 chain and closed as review-only.

Added:

```text
control/DETERMINISTIC_REGIME_SAFE_SURFACE_INTEGRATION_REVIEW.md
output/macro/validation/deterministic_regime_safe_surface_integration_review_20260613_000000.json
```

Updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
control/ETF_SESSION_CHANGELOG.md
```

Decision:

```text
ready_for_separate_integration_proposal
production_report_integration=false
```

Next package:

```text
WP25 — Deterministic regime report integration proposal
```

WP25 must remain proposal-only unless a later package explicitly authorizes implementation.

---

## 2026-06-13 — WP23 deterministic regime safe-surface helper closed

WP23 added the helper-only deterministic regime safe-surface layer.

Added:

```text
runtime/deterministic_regime_client_surface.py
tests/test_deterministic_regime_client_surface_helper.py
control/DETERMINISTIC_REGIME_SAFE_SURFACE_HELPER_STATUS.md
output/macro/validation/deterministic_regime_safe_surface_helper_validation_20260613_codespace.json
```

Updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

Status:

```text
closed / manually validated in GitHub Codespace / not workflow-proven
```

---

## 2026-06-13 — WP22 deterministic regime client-safe surface validator closed

WP22 added and validated the client-safe surface validator.

Evidence artifact:

```text
output/macro/validation/deterministic_regime_client_surface_validation_20260613_codespace.json
```
