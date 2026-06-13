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

## Phase 2 — closed repair packages

WP16 is closed on the latest verified report set.

Closed WP16 defects:

```text
macro/ECB recency miss
ECB stance stale neutral wording
non-U.S. / IEFA wording mismatch
English n.v.t. residue
Dutch empty-comment residue
soft-cap / soft-target duplicated copy
Dutch equity-curve clipping / invisible chart
shadow and guarded-auto no-trade validation mismatch
Dutch product-name localization corruption, including iShares -> iAantal aandelen
```

WP17 is closed on the latest verified report set.

Closed WP17 work:

```text
PDF visual contract validator added.
Poppler rendering tools installed in production workflow.
EN/NL PDF equity-curve visual gate runs before send.
Dutch PDF product-name corruption gate runs before send.
Manifest evidence validator added.
Manifest evidence gate runs after final run-manifest write.
```

Do not continue patching WP16/WP17 unless a new defect is found in a later manifest-linked run.

---

## Phase 3 — deterministic macro boundary

Current deterministic macro boundary remains:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
```

WP16/WP17/WP18 do not promote deterministic macro.

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
WP18 — Macro/thesis roadmap Phase 2: macro audit foundation
```

Current WP18 status:

```text
implemented / shadow-only / validation workflow added / pending fresh workflow evidence
```

Implemented in WP18:

```text
tools/validate_macro_data_audit.py hardened
tools/replay_macro_audit_foundation_fixture.py added
tests/test_wp18_macro_data_audit_validator.py added
tests/test_wp18_macro_audit_foundation_fixture.py added
.github/workflows/validate-macro-audit-foundation.yml added
control/MACRO_AUDIT_FOUNDATION_STATUS.md updated
```

Required boundary:

```text
- shadow/audit-only unless separately promoted
- no deterministic macro promotion
- no portfolio mutation
- no scoring/fundability changes
- no client-facing thesis candidates unless a later output contract explicitly allows them
- no historical artifact rewrite
```

Next action to close WP18:

```text
Observe or manually run: Validate ETF macro audit foundation
Confirm green status
Confirm output/macro/validation/latest_wp18_macro_audit_foundation_validation.json is committed
Then update control/CURRENT_STATE.md, control/NEXT_ACTIONS.md, and control/ETF_SESSION_CHANGELOG.md from pending to closed
```

---

## Phase 5 — next package after WP18 closes

Do not start this until WP18 validation evidence is observed.

Recommended next package:

```text
WP19 — Deterministic regime engine fixture baseline
```

Scope:

```text
- fixture-only / shadow-only deterministic regime classification baseline
- no production macro promotion
- no client-facing raw macro axes
- no portfolio mutation
- no scoring/fundability changes
- no historical output rewrite
```

Likely start files:

```text
config/regime_thresholds.yml
macro_regime/classify.py
macro_regime/confidence.py
runtime/build_macro_policy_pack_shadow.py
tools/validate_macro_regime_shadow.py
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
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
Do not start WP19 before WP18 validation evidence is observed.
```
