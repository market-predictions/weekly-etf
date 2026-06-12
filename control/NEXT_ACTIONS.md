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

## Phase 1 — WP16 follow-up status

WP16 has been implemented, and a follow-up repair has been committed for the two remaining `260611_02` client-surface defects.

```text
WP16-FOLLOWUP — Empty-comment and constraint-copy repair: implemented / rerun requested / delivery not yet verified
```

Follow-up rerun request:

```text
control/run_queue/weekly_etf_report_request_20260612_wp16_followup_rerun.md
```

Do not claim successful report delivery until the workflow produces valid evidence.

Required verification after rerun:

```text
GitHub Actions run conclusion=success
run manifest exists
delivery manifest exists
English and Dutch report artifacts exist
pricing lineage passes
Dutch empty-comment residue absent
English/Dutch constraint duplication absent
ECB policy catalyst still appears
ECB stance remains Tightening / inflation-sensitive
non-U.S. exposure wording remains reconciled with active IEFA exposure
English n.v.t. residue remains absent
Dutch equity-curve render checked
```

---

## Phase 2 — current baseline rule

The latest fully verified clean baseline before WP16 remains:

```text
requested_close_date: 2026-06-10
run_id: 20260610_211606
report_token: 260610
english_report_path: output/weekly_analysis_pro_260610_02.md
dutch_report_path: output/weekly_analysis_pro_nl_260610_02.md
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception
```

The uploaded `260611_02` reports show the macro/ECB fixes landed, but still had comment-residue and duplicated constraint-copy defects. They should not be treated as clean premium final output until the WP16 follow-up rerun is verified.

---

## Phase 3 — deterministic macro boundary

Current deterministic macro boundary remains:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
```

WP16 and WP16-FOLLOWUP do not promote deterministic macro.

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

## Phase 4 — historical artifact policy

WP15 remains active:

```text
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
historical_output_mutation=false
```

WP16-FOLLOWUP did not manually rewrite historical outputs. A clean report must be produced by workflow rerun.

---

## Phase 5 — next action

Next action:

```text
Verify WP16 follow-up rerun result.
```

If the WP16 follow-up rerun succeeds, update:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

with the new run id, report token, pricing audit, runtime state, run manifest, delivery manifest, and delivery status.

If the WP16 follow-up rerun fails, inspect the failing workflow step first and do not manually edit generated report artifacts.

---

## Do-not-do list

```text
Do not claim successful delivery without run/delivery manifest evidence.
Do not promote deterministic macro by implication.
Do not rewrite historical generated outputs.
Do not use replacement-edge diagnostics for scoring, fundability, or trades.
Do not weaken pricing-lineage or runtime-state authority.
```
