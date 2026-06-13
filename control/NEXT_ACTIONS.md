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

## Phase 1 — WP16 repair status

WP16 is closed on the latest verified report set.

```text
requested_close_date: 2026-06-12
run_id: 20260613_094305
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_06.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_06.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
```

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

Do not continue patching WP16 unless a new defect is found in a later manifest-linked run.

---

## Phase 2 — current baseline rule

Current manifest-linked baseline is `260612_06`, not older `260610_02` or `260611_*` artifacts.

Use:

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260613_094305.json
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_094305.json
```

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

Historical generated outputs remain immutable by default. Do not bulk-edit old reports to remove stale wording or old markers.

---

## Phase 3 — deterministic macro boundary

Current deterministic macro boundary remains:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
```

WP16 and its follow-ups do not promote deterministic macro.

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

## Phase 4 — recommended next action

Recommended next package:

```text
WP17 — PDF visual QA and delivery-runbook hardening
```

Reason:

```text
WP16 showed that text validators can pass while PDF visuals fail. The next small package should add a deterministic visual/report-render gate before returning to larger macro/thesis roadmap work.
```

Scope:

```text
- no macro promotion
- no portfolio mutation
- no scoring/fundability changes
- no historical artifact rewrite
- add or improve visual PDF checks for EN/NL equity curve and product-name corruption
- make runbook evidence easier to verify from latest manifests
```

After WP17, resume the approved macro/thesis roadmap Phase 2: macro audit foundation.

---

## Do-not-do list

```text
Do not claim inbox delivery without receipt evidence.
Do not promote deterministic macro by implication.
Do not rewrite historical generated outputs.
Do not use replacement-edge diagnostics for scoring, fundability, or trades.
Do not weaken pricing-lineage or runtime-state authority.
Do not localize ETF issuer/product names such as iShares, SPDR, VanEck, Sprott, or Global X.
```
