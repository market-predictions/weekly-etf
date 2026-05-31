# Handover — Weekly ETF Macro Regime Shadow Track

**Repository:** `market-predictions/weekly-etf`  
**Handover date:** 2026-06-01  
**Prepared for:** fresh ChatGPT session continuation  
**Scope:** Weekly ETF only, not Weekly ETF EU  
**Current workstream:** Macro/thesis roadmap Phase 2/3 — macro policy pack schema + deterministic regime/confidence shadow layer  

---

## 1. Mandatory start sequence for the next chat

Start by reading in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/ETF_SESSION_CHANGELOG.md`
5. `control/MACRO_POLICY_PACK_SCHEMA_STATUS.md`
6. `control/MACRO_REGIME_SHADOW_STATUS.md`
7. only then the minimum relevant execution files listed below

Do not rely on ChatGPT memory alone. Treat GitHub as the external source of truth.

---

## 2. Current issue

We are implementing the approved macro/thesis roadmap after pricing-lineage closure.

The current subtask is the deterministic regime/confidence engine in **shadow mode**.

The latest state:

```text
Pricing lineage: closed baseline / active regression guard
Macro policy pack schema gate: implemented and production-proven
Deterministic regime/confidence shadow layer: implemented
Fixture replay: implemented
Fixture replay workflow proof after latest import fixes: pending external/Actions confirmation
Production report path: unchanged
Client-facing decision impact: none
```

---

## 3. Root cause / why we are doing this carefully

The legacy macro policy pack already feeds `output/macro/latest.json` into lane discovery.

That means regime and macro fields can eventually affect discovery and portfolio recommendations. Therefore, the new macro/regime engine must not be promoted directly into production. The correct staged path is:

```text
pricing lineage baseline confirmed
→ macro audit foundation
→ macro policy pack schema/compatibility gate
→ deterministic regime/confidence in shadow mode
→ fixture replay
→ methodology and compliance gates
→ thesis candidates in shadow mode
→ Stage-2 confirmation and valuation flags
→ client-surface integration only after validation
```

Authority rule:

> The deterministic regime/confidence engine may produce internal comparison artifacts, but it must not change client-facing regime, confidence, lane scoring, fundability, portfolio actions, or report wording until explicitly promoted by a later control-layer decision.

---

## 4. Completed before this handover

### 4.1 Pricing-lineage baseline closed

Confirmed fresh run:

```text
run_id: 20260531_200843
requested_close_date: 2026-05-29
pricing_lineage_status: passed
workflow_conclusion: success
english_report_path: output/weekly_analysis_pro_260529_22.md
dutch_report_path: output/weekly_analysis_pro_nl_260529_22.md
runtime_state_path: output/runtime/etf_report_state_20260529_20260531_200843.json
pricing_audit_path: output/pricing/price_audit_2026-05-29_20260531_200843.json
total_portfolio_value_eur: 109964.97
```

Important caveat:

```text
delivery_manifest_path: null
```

So workflow and pricing-lineage success were proven, but independent email delivery receipt was not proven by that manifest alone.

### 4.2 Macro policy pack schema gate added and production-proven

Files added/updated:

```text
schemas/macro_policy_pack.schema.json
tools/validate_macro_policy_pack.py
runtime/build_macro_policy_pack.py
.github/workflows/send-weekly-report.yml
control/MACRO_POLICY_PACK_SCHEMA_STATUS.md
```

Fresh run evidence:

```text
run_id: 20260531_203900
requested_close_date: 2026-05-29
workflow_conclusion: success
pricing_lineage_status: passed
english_report_path: output/weekly_analysis_pro_260529_23.md
dutch_report_path: output/weekly_analysis_pro_nl_260529_23.md
macro_pack_path: output/macro/etf_macro_policy_pack_20260529_20260531_203900.json
runtime_state_path: output/runtime/etf_report_state_20260529_20260531_203900.json
pricing_audit_path: output/pricing/price_audit_2026-05-29_20260531_203900.json
total_portfolio_value_eur: 109964.97
```

The macro pack now includes compatibility fields:

```text
schema_version: 1.0
authority.shadow_only: true
authority.client_facing_authority: false
authority.decision_impact: legacy_lane_adjustments_only
macro_data_audit_summary.decision_impact: none_phase2_audit_only
regime.confidence_source: legacy_proxy_static
confidence_decomposition.decision_impact: none_shadow_explanation_only
active_drivers: []
```

### 4.3 Deterministic regime/confidence shadow layer implemented

Files added:

```text
config/regime_thresholds.yml
macro_regime/__init__.py
macro_regime/confidence.py
macro_regime/classify.py
runtime/build_macro_policy_pack_shadow.py
tools/validate_macro_regime_shadow.py
.github/workflows/validate-macro-regime-shadow.yml
control/MACRO_REGIME_SHADOW_STATUS.md
```

The shadow wrapper writes a normal macro policy pack plus:

```text
deterministic_regime_shadow
```

Expected fields:

```text
schema_version: 1.0
method: deterministic_axis_classifier_v1_shadow
shadow_only: true
client_facing_authority: false
decision_impact: none_shadow_comparison_only
candidate_regime
candidate_confidence
legacy_regime
legacy_confidence
differs_from_legacy
axes
axis_scores
confidence_decomposition
```

### 4.4 First shadow workflow validation passed before fixture replay was added

The user supplied an Actions screenshot showing success:

```text
workflow: Validate ETF macro regime shadow
run title: Trigger shadow macro regime validation workflow #2
trigger: push
commit: ddc8496...
branch: main
status: Success
job: validate-shadow-regime
job duration: 1m 37s
total duration: 1m 41s
```

Connector limitation: `fetch_commit_workflow_runs` and combined status did not expose the push-triggered workflow run. The screenshot was the proof source.

---

## 5. Work completed immediately before handover

### 5.1 Fixture replay added

Files added:

```text
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
tools/replay_macro_regime_shadow_fixtures.py
```

The fixture file defines five no-network deterministic scenarios:

```text
risk_on_growth
risk_on_narrow_leadership
defensive_policy_stress
rate_hike_repricing
mixed_policy_transition
```

The replay validator checks:

```text
expected candidate regime
expected axis labels
expected confidence range
shadow-only authority flags
exactly five fixture cases
```

Expected marker:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
```

### 5.2 Fixture replay wired into shadow validation workflow

Updated:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

The workflow now performs:

```text
python tools/replay_macro_regime_shadow_fixtures.py
python -m runtime.build_macro_policy_pack_shadow
python tools/validate_macro_policy_pack.py --pack output/macro/latest.json
inline validate_shadow_payload(...)
```

Expected markers:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_REGIME_SHADOW_OK
```

### 5.3 First fixture-replay workflow failure diagnosed

The user supplied an Actions screenshot showing failure in the `Replay deterministic regime fixtures` step:

```text
ModuleNotFoundError: No module named 'macro_regime'
```

Root cause:

```text
python tools/replay_macro_regime_shadow_fixtures.py
```

When Python runs a script from `tools/`, `tools/` is on `sys.path`, not the repo root. Therefore `macro_regime` was not importable.

### 5.4 Import fixes applied

Commits:

```text
1ec587e6d806b6892a48173e960fd7a3f305ed18 — fix shadow fixture replay import path
917d3218aa85db10cc9b0d3316650ae6c3a479c5 — set PYTHONPATH for shadow regime validation workflow
7650ae959637ef51c40f15a6b5d73c9658e4e339 — update macro regime fixture replay status after import hardening
```

Specific changes:

```text
tools/replay_macro_regime_shadow_fixtures.py now inserts repo root into sys.path before importing macro_regime
.github/workflows/validate-macro-regime-shadow.yml now sets PYTHONPATH: . at job level
```

---

## 6. Current blocker / exact continuation point

The fixture replay import issue has been patched, but the latest rerun after commit:

```text
917d3218aa85db10cc9b0d3316650ae6c3a479c5
```

has not yet been independently confirmed as passed.

The connector could not see the push-triggered workflow run:

```text
fetch_commit_workflow_runs: []
combined_status: []
```

A broader attempt to make the workflow self-commit a validation result artifact was blocked by the tool safety layer, so no self-reporting result artifact was added.

### The next chat should start here

Check the GitHub Actions run for:

```text
workflow: Validate ETF macro regime shadow
commit: 917d3218aa85db10cc9b0d3316650ae6c3a479c5
```

Confirm whether the workflow passed and whether logs contain:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_REGIME_SHADOW_OK
```

If it passed:

1. update `control/MACRO_REGIME_SHADOW_STATUS.md` to mark fixture replay workflow-proven;
2. update `control/ETF_SESSION_CHANGELOG.md`;
3. consider updating `control/NEXT_ACTIONS.md` to move from fixture replay proof to methodology/compliance gates.

If it failed:

1. read the failing step and error;
2. patch only the shadow fixture/workflow/modules;
3. do not touch the production report workflow;
4. rerun or trigger again;
5. keep status as shadow-only.

---

## 7. Important boundary rules for next chat

Do not do these yet:

```text
Do not promote deterministic_regime_shadow into production regime/confidence.
Do not use shadow candidate_regime for lane scoring.
Do not change fundability or portfolio actions based on shadow regime.
Do not add WP-9 thesis candidates to client reports.
Do not claim email delivery success from workflow success alone.
```

Production path remains:

```text
runtime/build_macro_policy_pack.py
→ output/macro/latest.json
→ lane discovery
```

Shadow path remains isolated:

```text
runtime/build_macro_policy_pack_shadow.py
→ deterministic_regime_shadow
→ validate-macro-regime-shadow.yml
```

---

## 8. Exact files most relevant for continuation

Read these after the control files:

```text
control/MACRO_POLICY_PACK_SCHEMA_STATUS.md
control/MACRO_REGIME_SHADOW_STATUS.md
config/regime_thresholds.yml
macro_regime/confidence.py
macro_regime/classify.py
runtime/build_macro_policy_pack_shadow.py
tools/validate_macro_regime_shadow.py
tools/replay_macro_regime_shadow_fixtures.py
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
.github/workflows/validate-macro-regime-shadow.yml
```

---

## 9. Most important commits in this workstream

Pricing-lineage and runtime baseline:

```text
53ae01ae182beb3b070cbe39ad59189c82673e20 — update current state after pricing-lineage confirmation
f94ae972c1697f9b584e82e50d84d03ece6ea51a — update next actions after pricing-lineage closure
```

Macro policy pack schema:

```text
7dbaadaaa66ffa44a84b5cd9682619aac0a5828c — add macro policy pack schema
296559dc4e84c12124a46ef9217106ed0c2602fb — add macro policy pack validator
54e1f3d8b6408266bd98c72f585d693c24e3bbf4 — add schema compatibility fields to macro pack builder
cacfe1de2546b75303793158ffcaf42577ba5b63 — validate macro policy pack before lane discovery
24ba1314bef158dd2e8c9786ae6536f1d3a22b19 — mark macro policy pack schema gate production-proven
```

Deterministic regime shadow:

```text
8f39c282902d1e62c5c25bd1e0e8cdeb03b5b876 — add shadow deterministic regime thresholds
82fcce61b6b124f704c58652d8383c38e32afbf8 — add macro_regime package
971a12aa4057d602a38f83fe9a3309c55b3e8472 — add shadow deterministic regime confidence model
e5474cbcc5301542b6ad8ec443f0bac2118cbb36 — add shadow deterministic regime classifier
45459c0f8b41edf16e9b15caa3c641ee3e36f60b — add shadow deterministic regime macro pack wrapper
458d6d2641b65c1348e50456c3ceb40c0263a860 — add minimal shadow regime payload validator
6909a458ad9d5d0ca940725b9c67705d82238076 — add shadow macro regime validation workflow
ddc84962191b8779bfa908b6dac2d09221408890 — trigger shadow macro regime validation workflow
```

Fixture replay and latest blocker:

```text
9fa8b92e2e579ae29b4c68d71661b0876f9d71c4 — add deterministic macro regime shadow fixtures
96253967d9410bc9ad259d1f1d5dc4aeb6efb055 — add macro regime shadow fixture replay validator
58509114c84ee1118c930fa38f89c5ec23551903 — run macro regime fixture replay in shadow validation workflow
1ec587e6d806b6892a48173e960fd7a3f305ed18 — fix shadow fixture replay import path
917d3218aa85db10cc9b0d3316650ae6c3a479c5 — set PYTHONPATH for shadow regime validation workflow
7650ae959637ef51c40f15a6b5d73c9658e4e339 — update macro regime fixture replay status after import hardening
```

---

## 10. Suggested next prompt for fresh chat

Use this prompt:

```text
Continue the Weekly ETF macro regime shadow work from the handover file:
control/handovers/HANDOVER_WEEKLY_ETF_MACRO_REGIME_SHADOW_20260601.md

Follow the repo control-layer read order:
1. control/SYSTEM_INDEX.md
2. control/CURRENT_STATE.md
3. control/NEXT_ACTIONS.md
4. control/ETF_SESSION_CHANGELOG.md
5. control/MACRO_POLICY_PACK_SCHEMA_STATUS.md
6. control/MACRO_REGIME_SHADOW_STATUS.md
7. the handover file

First verify whether the Validate ETF macro regime shadow workflow passed after commit 917d3218aa85db10cc9b0d3316650ae6c3a479c5.
Expected markers:
- ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
- ETF_MACRO_REGIME_SHADOW_OK

If passed, update status/changelog and propose the next roadmap step.
If failed, patch only the shadow fixture/workflow/modules. Do not change the production report path or client-facing decisions.
```

---

## 11. Bottom line

The weekly ETF production report baseline is stable with pricing-lineage proof. The macro policy pack schema gate is production-proven. The deterministic regime/confidence layer is implemented and isolated in shadow mode. Fixture replay has been added, and the only open item is to confirm the post-import-fix shadow validation workflow result after commit `917d3218aa85db10cc9b0d3316650ae6c3a479c5`.
