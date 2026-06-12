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

## Phase 1 — current production baseline

Latest fully recorded production evidence:

```text
workflow: Send weekly ETF Pro report
github_actions_run: 27306857013
artifact_commit: e2891ca
requested_close_date: 2026-06-10
run_id: 20260610_211606
report_token: 260610
english_report_path: output/weekly_analysis_pro_260610_02.md
dutch_report_path: output/weekly_analysis_pro_nl_260610_02.md
run_manifest_path: output/run_manifests/weekly_etf_run_manifest_2026-06-10_20260610_211606.json
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-10_20260610_211606.json
pricing_lineage_status: passed
pricing_coverage_count_pct: 100.0
fresh_holdings_count: 9
carried_forward_holdings_count: 0
total_portfolio_value_eur: 103994.26
cash_eur: 1936.52
delivery_status: smtp_sendmail_returned_no_exception
inbox_receipt: not_proven
```

Delivery manifest evidence is delivery-layer evidence only. It is not an end-recipient inbox receipt.

Current holdings:

```text
CIBR
DFEN
GSG
IEFA
PAVE
SMH
SPY
URNM
XLU
```

Historical note: workflow run #216 / run `20260605_081216` remains historical evidence only and must not be described as the latest production baseline.

---

## Phase 2 — completed roadmap status

Completed deterministic macro and control-policy packages:

```text
WP1 — Deterministic macro narrative shadow candidate: completed / not promoted
WP2 — Macro narrative compliance and bilingual parity gate: completed / not promoted
WP3 — Macro promotion decision contract: completed / merged
WP7 — Deterministic macro regime client-surface pilot: completed / non-authoritative / not promoted
WP8 — Macro old-vs-new review evidence package: completed / ready_for_narrative_promotion_review / not promoted
WP9 — Controlled deterministic macro narrative promotion artifact: completed / status=not_promoted
WP10 — Explicit deterministic macro narrative authority promotion decision: completed / status=not_promoted
WP13 — Deterministic macro read promotion review: completed / review-only / not promoted
WP14 — Deterministic macro read shadow replay evidence: completed / replay-only / not promoted
WP15 — Historical artifact cleanup policy: completed / policy-only / no artifact mutation
```

Key artifacts:

```text
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
output/macro/replay/deterministic_macro_shadow_replay_20260612_000000.json
control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md
```

Current deterministic macro boundary:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
```

Do not infer deterministic macro promotion from green validators, review readiness, macro policy pack existence, client-safe macro surface presence, prior pilot output, WP13 review checklist, WP14 replay evidence, or WP15 policy.

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

## Phase 3 — replacement-edge diagnostic notes

Current marker status:

```text
The visible marker ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED is absent from the current 260610_02 Markdown / clean Markdown / HTML / PDF surfaces.
```

Replacement-edge notes remain diagnostic-only and must not influence ranking, lane scoring, fundability, recommendations, target weights, trade intents, execution, or portfolio mutation.

Older historical artifacts may still contain the old marker. Current delivery output is the fresh `260610_02` set.

---

## Phase 4 — historical artifact policy

WP15 policy status:

```text
policy_status=cleanup_policy_defined_no_artifact_mutation
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
historical_output_mutation=false
production_report_behavior_changed=false
scoring_changed=false
fundability_changed=false
execution_changed=false
delivery_changed=false
portfolio_state_changed=false
macro_authority_changed=false
```

Operational rule:

```text
Repo-wide grep can identify historical residue, but current production truth must be determined from CURRENT_STATE plus the latest manifest-linked report/runtime/pricing/delivery artifacts.
```

Do not rewrite, delete, or silently regenerate historical output files without a future explicit cleanup/archive work package.

---

## Phase 5 — next action

There is no automatic cleanup or promotion task after WP15.

Next step is a coordinator/user decision:

```text
Option 1 — stop and observe the clean current production baseline
Option 2 — prepare an explicit deterministic macro promotion decision package
Option 3 — define a scoped historical archive execution package, if grep noise becomes operationally blocking
```

Recommended default:

```text
Option 1 — stop and observe the clean current production baseline
```

---

## Do-not-do list

```text
Do not reintroduce the replacement-edge marker into report output.
Do not treat old historical artifacts as current delivery output.
Do not promote deterministic macro read by inference.
Do not let macro/thesis shadow fields leak into client output.
Do not use replacement-edge diagnostics for scoring, fundability, or trades.
Do not rewrite historical output files without explicit approval.
Do not collapse state authority back into Markdown reports.
```
