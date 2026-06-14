# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

It is intentionally separate from specialized logs:

- `control/ETF_PRICING_LINEAGE_CHANGELOG.md` — pricing-lineage specific implementation/regression history
- `control/DECISION_LOG.md` — stable architecture decisions only
- `control/CURRENT_STATE.md` — current state snapshot
- `control/NEXT_ACTIONS.md` — roadmap / active backlog

## Rules

- Record every meaningful architecture, workflow, control-file, validator, runtime, delivery, roadmap, and handover-relevant change.
- Include the current issue, root cause, what changed, affected files, validation evidence, and remaining work.
- Keep entries specific enough that a fresh chat can continue without relying on hidden memory.
- Do not use this file for ordinary report-content edits unless they affect workflow, state, validation, delivery, or roadmap direction.
- Specialized changes may be summarized here and tracked in more detail in their dedicated changelog.

---

## 2026-06-13 — WP22 deterministic regime client-safe surface validator closed after Codespace validation

### Current issue

WP21 defined a safe-surface design, but future helper work needed a validator to prevent unsafe deterministic regime text from leaking internal details or raw evidence into client-style text.

### Root cause / architectural tension

A safe surface is only useful if it can be checked mechanically. The validator needed to prove that rendered fixture text uses a narrow DTO, contains review-only wording, avoids raw macro internals, and preserves the no-authority boundary.

### What changed

Added:

```text
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
tools/validate_deterministic_regime_client_surface.py
tests/test_deterministic_regime_client_surface_validator.py
control/DETERMINISTIC_REGIME_CLIENT_SURFACE_VALIDATOR_STATUS.md
output/macro/validation/deterministic_regime_client_surface_validation_20260613_codespace.json
```

Updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
```

Implementation details:

```text
- added a fixture DTO for the deterministic regime safe surface
- added a validator that checks required DTO fields and false authority fields
- validator checks English and Dutch review-only wording
- validator blocks raw macro fields, raw source paths, workflow ids, fixture names, and raw confidence precision
- validator runs existing macro compliance and macro/thesis leakage scans against the safe text
- added focused pytest coverage for safe and unsafe cases
```

### Validation evidence

Manual GitHub Codespace commands reported by the user:

```bash
PYTHONPATH=. python tools/validate_deterministic_regime_client_surface.py --self-test
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_client_surface_validator.py -q
PYTHONPATH=. python tools/validate_deterministic_regime_client_surface.py --surface fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
```

Observed success output:

```text
DETERMINISTIC_REGIME_CLIENT_SURFACE_SELF_TEST_OK
DETERMINISTIC_REGIME_CLIENT_SURFACE_OK
7 passed in 0.03s
DETERMINISTIC_REGIME_CLIENT_SURFACE_OK
```

Repo evidence artifact:

```text
output/macro/validation/deterministic_regime_client_surface_validation_20260613_codespace.json
```

### Authority boundary preserved

```text
validator_or_helper_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
production_report_integration=false
historical_output_mutation=false
```

### Remaining work

Proceed only to a separate helper-only package if desired:

```text
WP23 — Deterministic regime safe-surface helper
```

WP23 must not integrate the helper into production reports unless a separate later package explicitly approves report integration.

---

## 2026-06-13 — WP21 deterministic regime client-safe surface design closed

### Current issue

WP20 kept the deterministic regime engine not promoted, but also identified the next safe step: define a future client-safe surface shape before any validator or implementation work.

### Root cause / architectural tension

The deterministic regime shadow evidence contains useful regime, confidence, comparison and macro-context information, but raw fields such as `macro_axes`, `macro_axis_scores`, `macro_evidence`, `confidence_decomposition`, workflow metadata and fixture names must not be copied directly into client reports. A safe output contract must exist before any helper, validator, or report integration package is allowed.

### What changed

Added:

```text
control/DETERMINISTIC_REGIME_CLIENT_SAFE_SURFACE_DESIGN.md
```

Updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
```

Implementation details:

```text
- defined a design-only client-safe deterministic regime surface contract
- specified a future narrow DTO: DeterministicRegimeClientSurface
- defined allowed English and Dutch surface shapes
- required confidence bands instead of raw confidence precision
- blocked raw macro axes, raw scores, macro evidence, confidence decomposition, workflow metadata, fixture names and source paths from report use
- specified future validator expectations for WP22
- no runtime, renderer, report, delivery, scoring, fundability, portfolio or historical-output files were changed
```

### Validation evidence

WP21 is a specification-only package. Closeout evidence is the committed design artifact:

```text
control/DETERMINISTIC_REGIME_CLIENT_SAFE_SURFACE_DESIGN.md
```

No test execution is required for WP21 because no runtime validator or helper was implemented.

### Authority boundary preserved

```text
design_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
production_report_integration=false
historical_output_mutation=false
```

### Remaining work

Superseded by WP22 validator closeout. Proceed only to WP23 if desired.

---

## Open watch items

### Delivery evidence

Workflow success is not the same as email delivery proof. The current manifest has delivery-manifest evidence for the latest recorded baseline, but inbox receipt remains not proven unless separately confirmed.

### Price verification

Rows may still show `fresh_exact_unverified`. Cross-provider verification could later upgrade rows to `fresh_exact_close` where independent sources agree.

### Dutch alias consolidation

Dutch labels and validator aliases are working but still distributed across several files. Consolidation remains a useful cleanup.

### Replacement-edge diagnostic notes validation

WP11A-FIX is wired into the report surface, but focused pytest and fresh report/content validation evidence still need to be recorded.
