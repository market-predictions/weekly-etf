# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

## Rules

- Record meaningful architecture, workflow, control-file, validator, runtime, roadmap, and handover-relevant changes.
- Keep entries specific enough that a fresh chat can continue without hidden memory.

---

## 2026-07-17 — Internal workflow language removed from future client surfaces

`WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP` introduced one shared bilingual output contract for future English/Dutch report Markdown and delivery HTML.

Implemented:

```text
runtime/report_surface_language_contract.py
runtime/wp16_followup3_cleanup.py
runtime/deterministic_regime_client_surface.py
tools/validate_deterministic_regime_client_surface.py
tools/validate_report_surface_internal_language_cleanup.py
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
tests/test_report_surface_internal_language_cleanup.py
tests/test_deterministic_regime_client_surface_helper.py
tests/test_deterministic_regime_client_surface_validator.py
tests/test_deterministic_regime_report_surface_integration.py
.github/workflows/validate-report-surface-internal-language-cleanup.yml
```

The contract blocks client-visible implementation terms including `shadow engine`, `runtime macro pack`, `rotation engine status`, `guarded model rotation`, `guarded auto-execution`, `release score`, raw override wording, `review-only`, `runtime valuation`, `model/action weights`, churn/discipline-gate phrasing, `run(s)` and repeated punctuation.

The supplementary deterministic regime surface now uses `Supplementary regime cross-check` / `Aanvullende regimecontrole`. All explicit false-authority fields remain false.

Validation:

```text
workflow_run: 29590932038
workflow_job: 87919550815
result: success
focused_tests: 30 passed
artifact_id: 8411017345
artifact_digest: sha256:8a7acad3c573ae2eaa9a82fcd92f295ae5c6b33cc6090ca6936b5cd1a7997a74
EN findings: 18 -> 0
NL findings: 6 -> 0
EN numeric tokens: 635 preserved
NL numeric tokens: 588 preserved
EN markdown links: 234 preserved
NL markdown links: 236 preserved
cleanup_idempotent: true
historical reports: byte unchanged
email sent: false
```

Persistent records:

```text
control/evidence/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_EVIDENCE_20260717.json
control/decisions/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_DECISION_20260717.md
control/handovers/HANDOVER_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_20260717.md
```

No report or email was sent. The next operational step is a separate explicitly authorized fresh production run.

---

## 2026-07-17 — Additive cockpit front page enabled for future production runs

WP11 selected and implemented option B: enable the validated additive English/Dutch cockpit front page in the real production workflow.

Production feature:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled
rollback: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled
```

The last delivered `260716` report predates the whole-share reconciliation. WP11 therefore built a temporary exact-current overlay from the latest persisted runtime pricing/macro/lane context plus the current whole-share official portfolio state. The overlay and generated reports were not persisted to production.

Validation:

```text
validation_run: 29582753816
validation_job: 87892175344
current_runtime_regression_run: 29582753774
wp08_regression_run: 29582753837
artifact_id: 8407711197
artifact_digest: sha256:b483b7157a69939e66c9a7b3624b2401a2211c5ba2db1367b97374aa1b0899a9
focused_tests: 3 passed
```

Measured output:

```text
current NAV EUR: 107117.94
current cash EUR: 2519.05
current position count: 8
largest position: SMH
EN front pages: 0 disabled / 1 enabled
EN PDF pages: 16 -> 17
NL front pages: 0 disabled / 1 enabled
NL PDF pages: 17 -> 18
classic report body: preserved
small decision cockpit duplicate: false
protected authority hashes: identical
email sent: false
```

The old current-runtime and WP08 workflow assertions were also rebased from the historical `260714 / URNM → XBI` fixture to the current `260716 / DFEN → XLV` baseline. Both regressions passed.

Persistent evidence:

```text
control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
control/decisions/COCKPIT_WP11_PRODUCTION_ENABLEMENT_DECISION_20260717.md
control/handovers/HANDOVER_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT_20260717.md
```

No report or email was sent. The next package is a separate future-report language cleanup for internal terms such as `shadow engine`.

---

## 2026-07-17 — Whole-share official state contract implemented and reconciled

The latest production state was found to violate the decision-framework rule `whole shares only`. Guarded model execution stored fractional positions and fractional Buy/Sell deltas, and a small leveraged `DFEN` remainder conflicted with the active no-leverage constraint.

Implemented and merged under PR #85:

```text
runtime/whole_share_contract.py
runtime/model_execution_guarded_auto.py
tools/reconcile_etf_whole_share_state.py
tools/validate_etf_whole_share_contract.py
tools/validate_etf_model_execution.py
tests/test_etf_whole_share_contract.py
.github/workflows/validate-etf-whole-share-contract.yml
.github/workflows/reconcile-etf-whole-share-state.yml
```

Validation:

```text
merge_commit: d5532ea15801a3888633ccb824797ab254305433
workflow_run: 29580018310
focused_tests: 4 passed
compile: passed
```

The official state was then reconciled using the persisted 2026-07-16 runtime pricing and FX basis:

```text
request_commit: 3a54f5fb12be1c47420c0922ade4a82213bb3677
result_commit: 50b93740efbed537ed9d0daed6e1d88ce912be1e
artifact: output/runtime/etf_whole_share_reconciliation_20260716_20260717_094728.json
adjusted_positions: 10
ledger_rows_appended: 10
DFEN: policy closed
cash_released_eur: 582.53
cash_after_eur: 2519.05
nav_eur: 107117.94
nav_drift_eur: 0.00
whole_share_validation_errors: []
```

Current official holdings are eight whole-share positions: CIBR 253, GSG 374, IEFA 312, SMH 59, URNM 48, XBI 40, XLU 148 and XLV 37.

No email was sent and cockpit production enablement remained disabled. WP11 may resume using the reconciled official state.

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

---

## 2026-07-17 — Position-count constraint reconciled with close-first enforcement

`WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION` resolved the ambiguity between the official nine-position whole-share state and the eight-position maximum without changing holdings.

Decision:

```text
every non-zero position counts
generic residual exception: false
current state: close_first 9/8
new ticker while over limit: blocked
new ticker at limit: full source close required in same whole-share transition
```

Implemented:

```text
runtime/position_count_contract.py
runtime/position_count_report_surface.py
tools/validate_etf_persisted_valuation_state.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_position_count_contract.py
tests/test_etf_position_count_contract.py
.github/workflows/validate-etf-position-count-contract.yml
```

Validation:

```text
PR: #91
merge: 0bcb6af7e243775d876b59719ce9898fa97c690f
focused tests: 13 passed
final position-count run: 29618185729 success
final report-surface run: 29618185736 success
final current-runtime cockpit run: 29618185701 success
final WP08 run: 29618185711 success
final WP11 run: 29618185709 success
final recovery run: 29618185751 success
final fresh-send diagnostic run: 29618185706 success
protected authority hashes: identical
historical report hashes: identical
portfolio execution: false
email sent: false
```

The client output guard is current-state-aware: it discloses `9 / 8` only when the report ticker set exactly matches official state and leaves historical reports unchanged. The next package is `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW`; it must use fresh evidence and must not assume XLU is automatically the correct closure source.
