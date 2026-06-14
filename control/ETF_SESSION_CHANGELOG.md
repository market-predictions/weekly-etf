# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

## Rules

- Record meaningful architecture, workflow, control-file, validator, runtime, roadmap, and handover-relevant changes.
- Keep entries specific enough that a fresh chat can continue without hidden memory.

---

## 2026-06-13 — WP25 deterministic regime report integration proposal closed

WP25 created a proposal-only integration path for the deterministic regime safe-surface helper.

Added:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_PROPOSAL.md
output/macro/validation/deterministic_regime_report_integration_proposal_20260613_000000.json
```

Updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
```

Decision:

```text
future_implementation_package_allowed=true
production_report_integration=false
```

Next package:

```text
WP26 — Deterministic regime report integration implementation
```

WP26 requires explicit user approval before implementation.

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
