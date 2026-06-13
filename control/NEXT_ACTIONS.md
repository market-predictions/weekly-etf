# ETF Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 0 — control-layer operating discipline

Every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, localization, macro/thesis, or lab-optimization session starts with:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution files

For deterministic macro work, also read:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
control/MACRO_REPORT_SURFACE_STATUS.md
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/MACRO_REGIME_SHADOW_STATUS.md
```

For historical-output cleanup/archive questions, also read:

```text
control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md
```

---

## Phase 1 — current baseline rule

Current manifest-linked production baseline is `260612_08`.

Use:

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260613_113054.json
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_113054.json
```

Latest verified production baseline:

```text
requested_close_date: 2026-06-12
run_id: 20260613_113054
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_08.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_08.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

Historical generated outputs remain immutable by default. Do not bulk-edit old reports to remove stale wording or old markers.

---

## Phase 2 — closed repair / foundation packages

WP16 is closed on the latest verified report set.

WP17 is closed on the latest verified report set.

WP18 is closed.

WP19 is closed.

Closed WP19 work:

```text
macro_regime/classify.py now emits explicit no-authority fields.
tools/validate_macro_regime_shadow.py now requires no-authority fields and macro-audit consistency.
tools/replay_macro_regime_shadow_fixtures.py now validates fixture authority and regime-label coverage.
fixtures/macro_regime_shadow/regime_shadow_fixtures.json now carries explicit no-authority fields.
tools/write_macro_regime_shadow_validation_evidence.py now records full no-authority state.
tests/test_macro_regime_shadow.py added.
.github/workflows/validate-macro-regime-shadow.yml now runs tests/test_macro_regime_shadow.py.
control/MACRO_REGIME_SHADOW_STATUS.md updated to closed.
```

WP19 closeout evidence:

```text
Validate ETF macro regime shadow: green
workflow_run_id: 27480244857
workflow_run_number: 46
commit_sha: 1ba3f4e5a6126fd824a151525b0d9d91d42c3627
latest_macro_regime_shadow_validation.json: committed
```

Do not continue patching WP16/WP17/WP18/WP19 unless a new defect is found in a later manifest-linked run.

---

## Phase 3 — deterministic macro boundary

Current deterministic macro boundary remains:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
```

WP16/WP17/WP18/WP19 do not promote deterministic macro.

Standing authority boundary:

```text
client_facing_narrative_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
delivery_authority=false
execution_authority=false
production_report_mutation=false
```

---

## Phase 4 — active package

Active package:

```text
WP20 — Deterministic regime engine promotion-review contract
```

Current WP20 status:

```text
not_started / ready_to_start / review-only required
```

Scope:

```text
- review-only promotion-readiness contract for deterministic regime engine
- compare deterministic shadow output quality and safety after WP19 fixture baseline
- no automatic production promotion
- no client-facing raw macro axes
- no portfolio mutation
- no scoring/fundability changes
- no historical output rewrite
```

Likely start files:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
control/MACRO_REPORT_SURFACE_STATUS.md
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/MACRO_REGIME_SHADOW_STATUS.md
output/macro/validation/latest_macro_regime_shadow_validation.json
output/macro/validation/latest_macro_regime_shadow_comparison.json
```

Required boundary:

```text
review_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

---

## Phase 5 — next package after WP20 closes

Do not start this until WP20 is reviewed and closed.

Likely next package:

```text
WP21 — Deterministic regime client-safe report surface design, if WP20 keeps review path open
```

Tentative scope:

```text
- output-contract design only
- client-safe text surface only
- no raw macro axes in report
- no automatic production promotion
- no scoring/fundability changes
- no portfolio mutation
```

---

## Do-not-do list

```text
Do not claim inbox delivery without receipt evidence.
Do not promote deterministic macro by implication.
Do not rewrite historical generated outputs.
Do not use replacement-edge diagnostics for scoring, fundability, or trades.
Do not weaken pricing-lineage or runtime-state authority.
Do not localize ETF issuer/product names such as iShares, SPDR, VanEck, Sprott, or Global X.
Do not bypass the PDF visual gate after WP17.
Do not start WP21 before WP20 is reviewed and closed.
```
