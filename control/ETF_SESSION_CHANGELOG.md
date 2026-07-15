# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

## Rules

- Record meaningful architecture, workflow, control-file, validator, runtime, roadmap, and handover-relevant changes.
- Keep entries specific enough that a fresh chat can continue without hidden memory.

---

## 2026-07-15 — Rotation current-run authority and alternative-candidate package validated

The 2026-07-14 production output was audited after its no-mutation result. Fresh relative-strength data existed, but rotation still consumed stale recommendation-memory P/L and could not select alternative ETFs independently.

Implemented under PR #58:

```text
runtime/rotation_state_authority.py
runtime/portfolio_rotation_engine_v2.py
runtime/portfolio_rotation_engine.py
tools/validate_etf_rotation_state_authority.py
tests/test_etf_rotation_state_authority.py
.github/workflows/validate-etf-rotation-state-authority.yml
```

The package now:

- derives NAV, weights and P/L from current-run pricing;
- reconstructs missing average entries from official trade-ledger and model-execution artifacts;
- refreshes the scorecard before release scoring;
- blocks stale dates, prices, entry basis and P/L;
- evaluates primary and alternative ETFs independently;
- resolves capped candidate-score ties using quality evidence.

Final clean PR validation:

```text
head_sha: 68432f65e2c19e039956bc129d3a484d46ce9b78
workflow_run_id: 29438154551
job_id: 87429929415
result: success
focused_tests: 10 passed
validated_holdings: 9
```

The actual 2026-07-14 production artifacts were replayed. The corrected deterministic plan contains one intent:

```text
URNM -> XBI
source_delta_weight_pct: -5.00
destination_delta_weight_pct: +5.00
estimated_notional_EUR: 5511.24
```

Production execution remains pending merge and a fresh standard U.S. Weekly ETF report run.

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