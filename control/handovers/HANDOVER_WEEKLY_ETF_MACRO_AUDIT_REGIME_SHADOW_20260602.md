# Handover — Weekly ETF macro audit / deterministic regime shadow

## Date
2026-06-02

## Repository

```text
market-predictions/weekly-etf
```

## Purpose of this work package

Resume the original macro-regime roadmap: macro, policy, regime and thesis inputs should be grounded in deterministic Python evidence and provenance-backed artifacts, not generated as free-form LLM narrative.

This session continued the shadow-mode macro/regime layer only. No production client-facing regime, lane scoring, fundability, or portfolio-action authority was promoted.

## Control-layer boundary

The work remains under the four-layer split:

1. decision framework — shadow deterministic macro/regime comparison only
2. input/state contract — macro data audit observations + market relative-strength metrics
3. output contract — internal JSON only, no client-facing report surface authority
4. operational runbook — fixture replay and validation before any promotion decision

## Starting state before this session

Already present in the repo:

```text
macro_regime/classify.py
macro_regime/confidence.py
config/regime_thresholds.yml
runtime/build_macro_policy_pack_shadow.py
tools/replay_macro_regime_shadow_fixtures.py
tools/validate_macro_regime_shadow.py
.github/workflows/validate-macro-regime-shadow.yml
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
```

The prior shadow validation evidence existed at:

```text
output/macro/validation/latest_macro_regime_shadow_validation.json
```

with authority flags:

```text
shadow_only: true
client_facing_authority: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
production_report_path_changed: false
```

## Changes made in this session

### 1. Extended shadow confidence engine with macro-audit axis agreement

File changed:

```text
macro_regime/confidence.py
```

Commit:

```text
d91cadb6008f1eccc66615d52145a70e31d2b8e0
```

What changed:

- Existing confidence decomposition previously used market proxy axes only.
- It now accepts optional `macro_axes` and `macro_scores`.
- It computes descriptive macro-axis agreement for:
  - volatility
  - real rates
  - yield curve
  - inflation expectations
  - policy rate
- It still returns:

```text
shadow_only: true
client_facing_authority: false
decision_impact: none_shadow_comparison_only
```

Important: confidence remains descriptive cross-axis agreement, not forecast accuracy.

### 2. Extended deterministic shadow classifier to derive macro axes from macro data audit observations

File changed:

```text
macro_regime/classify.py
```

Commit:

```text
ec697e81dec30d296d055ec9fe1e6b56e88869d6
```

What changed:

- Added macro audit observation parsing.
- Added macro axis derivation from observations such as:
  - `us_10y_yield`
  - `us_2y_yield`
  - `us_10y_real_yield`
  - `us_10y_breakeven`
  - `fed_funds_effective`
  - `vix_close`
- Adds shadow payload fields:

```text
macro_axes
macro_axis_scores
macro_evidence
```

- Keeps the production decision boundary intact:

```text
shadow_only: true
client_facing_authority: false
decision_impact: none_shadow_comparison_only
```

### 3. Added macro-axis thresholds

File changed:

```text
config/regime_thresholds.yml
```

Commit:

```text
6fd9257bc97a5141f4d1d6b15fd3b024b2b78a6b
```

New threshold section:

```yaml
macro_axes:
  volatility:
    vix_calm_below: 16.0
    vix_stress_above: 25.0
  real_rates:
    restrictive_above: 1.75
    supportive_below: 0.75
  yield_curve:
    inverted_below: -0.25
    normalizing_above: 0.25
  inflation_expectations:
    elevated_above: 2.6
    contained_below: 2.3
  policy_rate:
    restrictive_above: 4.25
    accommodative_below: 2.0
```

Added `macro_alignment_weight` to the confidence config.

### 4. Wired shadow policy-pack builder to pass the macro audit payload into the classifier

File changed:

```text
runtime/build_macro_policy_pack_shadow.py
```

Commit:

```text
2d3a7223a707620f9e548ba97219633983163380
```

What changed:

- `add_shadow_regime()` now accepts `macro_data_audit_path`.
- It loads the full macro data audit payload and passes it into `classify_regime_shadow()`.
- The builder log now includes which macro axes were present.

### 5. Added a no-network macro data audit fixture

File created:

```text
fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json
```

The fixture includes provenance-style observations across required source groups:

```text
fred
ecb
treasury_fiscaldata
volatility
```

Representative observation keys:

```text
us_10y_yield
us_2y_yield
us_10y_real_yield
us_10y_breakeven
fed_funds_effective
ecb_eurusd_reference
treasury_3m_yield
treasury_2y_yield
treasury_10y_yield
treasury_30y_yield
vix_close
```

The fixture has:

```text
mode: fixture
status: passed
summary.shadow_only: true
summary.client_facing_authority: false
```

## Not completed yet

### A. Shadow workflow does not yet replay the new macro-audit fixture

The existing workflow:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

currently replays only:

```text
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
```

It does not yet run a no-network macro-data-audit fixture replay using:

```text
fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json
```

### B. Need a dedicated macro-audit shadow replay tool or workflow step

Recommended new/updated tool:

```text
tools/replay_macro_data_audit_shadow_fixture.py
```

or extend:

```text
tools/replay_macro_regime_shadow_fixtures.py
```

The replay should prove:

1. `tools/validate_macro_data_audit.py` accepts the fixture.
2. `runtime.build_macro_policy_pack_shadow` consumes the fixture via `--macro-data-audit`.
3. `deterministic_regime_shadow.macro_axes` is populated.
4. `tools/validate_macro_regime_shadow.py` accepts the resulting payload.
5. Evidence is written under `output/macro/validation/`.

### C. Need Actions trigger path update

The existing workflow trigger includes:

```yaml
fixtures/macro_regime_shadow/**
macro_regime/**
config/regime_thresholds.yml
runtime/build_macro_policy_pack_shadow.py
```

It should also include:

```yaml
fixtures/macro_data_audit/**
tools/replay_macro_data_audit_shadow_fixture.py
```

or whichever replay tool is created.

### D. Need to run/verify the shadow workflow after wiring fixture replay

No claim should be made yet that macro-audit-derived axes are validated in CI. The code and fixture exist, but the end-to-end CI proof is not complete.

## Current implementation status

```text
Pricing/state foundation: green
PDF-polish gate: green
Delivery receipt layer: still missing
Macro regime shadow market-proxy classifier: exists and previously validated
Macro audit fixture: created
Macro audit axes in classifier: implemented
Macro audit axes in confidence: implemented
Macro audit payload passed into shadow builder: implemented
Macro audit fixture replay in CI: not yet wired
Production macro authority: not promoted
Client-facing macro regime authority: not promoted
Thesis/fundability authority: not promoted
```

## Recommended next action in fresh chat

1. Read the control layer:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

2. Read this handover:

```text
control/handovers/HANDOVER_WEEKLY_ETF_MACRO_AUDIT_REGIME_SHADOW_20260602.md
```

3. Implement no-network macro-audit fixture replay:

```text
tools/replay_macro_data_audit_shadow_fixture.py
```

4. Wire it into:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

5. Trigger/verify the workflow and confirm logs include something like:

```text
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_AUDIT_AXIS_SHADOW_OK
```

6. Write validation evidence under:

```text
output/macro/validation/
```

7. Update:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
```

## Suggested next prompt

```text
Continue in market-predictions/weekly-etf. Read control/SYSTEM_INDEX.md, control/CURRENT_STATE.md, control/NEXT_ACTIONS.md, and control/handovers/HANDOVER_WEEKLY_ETF_MACRO_AUDIT_REGIME_SHADOW_20260602.md. We extended the shadow deterministic macro regime classifier to derive macro axes from macro data audit observations and added a no-network macro audit fixture. The code exists, but the new macro-audit fixture replay is not yet wired into CI. Please add the fixture replay tool/workflow step, run validation, and record evidence. Do not promote macro/regime output to client-facing or portfolio authority.
```

## Explicit authority warning

Do not use `deterministic_regime_shadow`, `macro_axes`, or `macro_axis_scores` for:

```text
client-facing regime labels
lane scoring
fundability decisions
portfolio trades
report recommendations
```

until a future control-layer decision explicitly promotes the layer after fixture replay, compliance, methodology, and bilingual gates pass.
