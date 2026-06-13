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

## 2026-06-13 — WP20 deterministic regime engine promotion review closed as not_promoted

### Current issue

WP19 proved the deterministic regime engine fixture baseline and explicit no-authority payload validation, but a green shadow engine must not be interpreted as production report narrative authority.

### Root cause / architectural tension

The deterministic regime engine now has strong fixture and shadow-validation evidence, but the promotion contract requires more than a working engine. Promotion to client-facing production narrative authority requires methodology approval, bilingual parity approval, compliance validation, old-vs-new review, and an explicit control-layer promotion decision.

### What changed

Added:

```text
control/DETERMINISTIC_REGIME_ENGINE_PROMOTION_REVIEW.md
output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

Updated:

```text
tests/test_macro_regime_promotion_contract.py
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
control/DECISION_LOG.md
```

Implementation details:

```text
- created a WP20 promotion-review artifact under the existing macro regime promotion contract schema
- artifact status is not_promoted
- old-vs-new comparison is marked reviewed for this review package
- methodology, bilingual parity, compliance validator, and explicit control-layer promotion remain false
- added a focused test that validates the WP20 review artifact with tools/validate_macro_regime_promotion_contract.py
- no report renderer, production workflow, portfolio state, scoring, fundability, or delivery files were changed
```

### Validation evidence

Review artifact:

```text
output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

Expected validation command:

```bash
python tools/validate_macro_regime_promotion_contract.py output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

Expected validator marker:

```text
MACRO_REGIME_PROMOTION_CONTRACT_OK
```

Focused test wired:

```bash
python -m pytest tests/test_macro_regime_promotion_contract.py -q
```

Note: the artifact and test are committed. This chat did not execute the pytest command locally; future CI/manual validation can run it directly.

### Authority boundary preserved

```text
review_only=true
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

### Remaining work

Proceed only to a separate design package if desired:

```text
WP21 — Deterministic regime client-safe report surface design
```

WP21 must remain output-contract design work only. It must not promote or integrate deterministic regime output into production reports by implication.

---

## 2026-06-13 — WP19 deterministic regime engine fixture baseline closed

### Current issue

WP19 needed to convert the deterministic regime engine from a working shadow replay path into a stricter fixture baseline. The existing fixtures already covered the major regime labels, but the payload and validator did not yet require every explicit no-authority field requested by the roadmap.

### Root cause / architectural tension

A green deterministic regime fixture replay only proves that the model can classify scenarios. It does not by itself prove that the output is safe to keep away from client-facing narrative, lane scoring, fundability, portfolio action, or historical output mutation. The fixture baseline therefore needed to validate both deterministic regime coverage and authority denial.

### What changed

Updated:

```text
macro_regime/classify.py
tools/validate_macro_regime_shadow.py
tools/replay_macro_regime_shadow_fixtures.py
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
tools/write_macro_regime_shadow_validation_evidence.py
.github/workflows/validate-macro-regime-shadow.yml
control/MACRO_REGIME_SHADOW_STATUS.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
```

Added:

```text
tests/test_macro_regime_shadow.py
```

Implementation details:

```text
- deterministic shadow payload now emits explicit no-authority fields
- validator requires those authority fields to be present and false
- fixture payload now carries the same no-authority fields
- fixture replay checks unique fixture ids and coverage of every threshold-defined regime label
- macro-axis validation now requires macro_audit_present=true and macro evidence when macro axes/scores exist
- evidence writer now records the full no-authority state
- GitHub workflow now installs pytest and runs tests/test_macro_regime_shadow.py before replaying fixtures
```

### Validation evidence

```text
workflow: Validate ETF macro regime shadow
workflow_run_id: 27480244857
workflow_run_number: 46
workflow_commit_sha: 1ba3f4e5a6126fd824a151525b0d9d91d42c3627
latest evidence: output/macro/validation/latest_macro_regime_shadow_validation.json
status: passed
```

Validated markers:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_AXIS_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_OK
```

### Authority boundary preserved

```text
fixture-only=true
shadow_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

### Remaining work

Superseded by WP20 closeout. Proceed only to WP21 if desired.

---

## 2026-06-13 — WP18 macro audit foundation closed and WP19 queued

### Current issue

WP18 had been implemented but still needed conclusive workflow evidence before it could be closed. The dedicated macro-audit foundation workflow passed, but the related macro-regime shadow workflow initially failed in its evidence commit step because GitHub Actions runs rewrote the same `latest_*.json` files and collided during push/rebase.

### Root cause / architectural tension

The macro audit foundation is an input/provenance layer and must remain shadow-only. At the same time, the validation stack needs committed evidence under `output/macro/validation/`. Repeated workflow runs update stable pointer files such as `latest_macro_regime_shadow_validation.json`, so the evidence commit runbook must be robust to remote-ahead races and `latest_*.json` conflicts.

### What changed

Updated:

```text
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
.github/workflows/validate-macro-regime-shadow.yml
```

Implementation / closeout details:

```text
- WP18 status moved from implemented/pending evidence to closed/verified/shadow-only.
- Macro audit foundation validation evidence is committed and passed.
- Macro-regime shadow validation evidence is committed and passed after run #40.
- The macro-regime shadow evidence commit step now commits from a freshly synced origin/main working tree and retries pushes.
- WP19 is now the active next package.
```

### Validation evidence

Dedicated WP18 macro-audit foundation evidence:

```text
artifact: output/macro/validation/latest_wp18_macro_audit_foundation_validation.json
workflow: Validate ETF macro audit foundation
workflow_run_id: 27476145040
workflow_run_number: 6
status: passed
```

Related macro-regime shadow compatibility evidence:

```text
artifact: output/macro/validation/latest_macro_regime_shadow_validation.json
workflow: Validate ETF macro regime shadow
workflow_run_id: 27478580626
workflow_run_number: 40
status: passed
validated_markers:
  ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
  ETF_MACRO_DATA_AUDIT_VALID_OK
  ETF_MACRO_AUDIT_AXIS_SHADOW_OK
  ETF_MACRO_REGIME_SHADOW_OK
```

### Authority boundary preserved

```text
shadow_only=true
client_facing_authority=false
decision_impact=none_phase2_audit_only
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

### Remaining work

Superseded by WP19 and WP20 closeout. Proceed only to WP21 if desired.

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
