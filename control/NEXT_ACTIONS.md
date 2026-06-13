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
```

For historical-output cleanup/archive questions, also read:

```text
control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md
```

---

## Phase 1 — current baseline rule

Current manifest-linked baseline is `260612_08`.

Use:

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260613_113054.json
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_113054.json
```

Latest verified baseline:

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

WP16 and WP17 do not promote deterministic macro.

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

## Phase 4 — recommended next package

Recommended next package:

```text
WP18 — Macro/thesis roadmap Phase 2: macro audit foundation
```

Purpose:

```text
Resume the approved macro/thesis roadmap now that the report-surface and delivery visual gates are stable.
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

Likely start files:

```text
docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md
config/macro_data_sources.yml
macro_sources/build_macro_data_audit.py
tools/validate_macro_data_audit.py
schemas/macro_data_audit.schema.json
```

Recommended next action:

```text
Define and execute WP18 as a small macro-audit foundation package with one verifiable audit artifact and validator, keeping all outputs shadow-only.
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
```
