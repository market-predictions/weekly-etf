# Macro Regime Shadow Status

## Date
2026-05-31

## Status
Implemented and workflow-validated as shadow-only scaffolding. Fixture replay has been added and is pending independent workflow proof.

## Current issue

The roadmap requires replacing hardcoded legacy regime/confidence logic with a deterministic regime and derived confidence engine, but only in shadow mode first.

## What changed

Added:

- `config/regime_thresholds.yml`
- `macro_regime/__init__.py`
- `macro_regime/confidence.py`
- `macro_regime/classify.py`
- `runtime/build_macro_policy_pack_shadow.py`
- `tools/validate_macro_regime_shadow.py`
- `.github/workflows/validate-macro-regime-shadow.yml`
- `fixtures/macro_regime_shadow/regime_shadow_fixtures.json`
- `tools/replay_macro_regime_shadow_fixtures.py`

## Authority rules

- This layer is shadow-only.
- It must not change client-facing regime, confidence, lane scoring, fundability, portfolio actions, or report wording.
- The production workflow still uses the legacy macro policy pack builder unless explicitly changed later.
- Legacy `regime`, `confidence`, and `lane_adjustments` remain the backward-compatible production path.

## Shadow output contract

The wrapper builder writes a normal macro policy pack plus:

```text
deterministic_regime_shadow
```

Expected fields include:

- `schema_version: 1.0`
- `method: deterministic_axis_classifier_v1_shadow`
- `shadow_only: true`
- `client_facing_authority: false`
- `decision_impact: none_shadow_comparison_only`
- `candidate_regime`
- `candidate_confidence`
- `legacy_regime`
- `legacy_confidence`
- `differs_from_legacy`
- `axes`
- `axis_scores`
- `confidence_decomposition`

## Fixture replay contract

The fixture replay file defines five stable no-network scenarios:

```text
risk_on_growth
risk_on_narrow_leadership
defensive_policy_stress
rate_hike_repricing
mixed_policy_transition
```

The replay validator checks:

- expected candidate regime
- expected axis labels
- expected confidence range
- shadow payload authority flags
- exactly five fixture cases

Expected replay marker:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
```

## Current validation route

The separate workflow:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

now performs:

```text
python tools/replay_macro_regime_shadow_fixtures.py
python -m runtime.build_macro_policy_pack_shadow
python tools/validate_macro_policy_pack.py --pack output/macro/latest.json
python inline validate_shadow_payload(...)
```

Expected markers:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_REGIME_SHADOW_OK
```

## Validation status

Earlier workflow validation passed in GitHub Actions according to the Actions UI screenshot supplied by the user.

Evidence from that screenshot:

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

Fixture replay was added after that passing run. The updated workflow was committed at:

```text
58509114c84ee1118c930fa38f89c5ec23551903
```

Connector limitation:

- `fetch_commit_workflow_runs` did not expose this push-triggered workflow run through the connector.
- Therefore fixture replay is implemented and wired, but not yet independently confirmed through connector-visible workflow evidence or a user-supplied Actions screenshot.

No production report path has been changed to depend on this shadow classifier.

## Next action

1. Verify the updated `Validate ETF macro regime shadow` workflow after commit `58509114c84ee1118c930fa38f89c5ec23551903`.
2. Confirm markers:
   - `ETF_MACRO_REGIME_FIXTURE_REPLAY_OK`
   - `ETF_MACRO_REGIME_SHADOW_OK`
3. If it passes, mark fixture replay as workflow-proven.
4. Keep deterministic regime shadow-only until methodology, compliance, bilingual, and production-report validation gates exist.

## Commits

- `8f39c282902d1e62c5c25bd1e0e8cdeb03b5b876` — add shadow deterministic regime thresholds
- `82fcce61b6b124f704c58652d8383c38e32afbf8` — add macro_regime package
- `971a12aa4057d602a38f83fe9a3309c55b3e8472` — add shadow deterministic regime confidence model
- `e5474cbcc5301542b6ad8ec443f0bac2118cbb36` — add shadow deterministic regime classifier
- `45459c0f8b41edf16e9b15caa3c641ee3e36f60b` — add shadow deterministic regime macro pack wrapper
- `458d6d2641b65c1348e50456c3ceb40c0263a860` — add minimal shadow regime payload validator
- `6909a458ad9d5d0ca940725b9c67705d82238076` — add shadow macro regime validation workflow
- `ddc84962191b8779bfa908b6dac2d09221408890` — trigger shadow macro regime validation workflow
- `9fa8b92e2e579ae29b4c68d71661b0876f9d71c4` — add deterministic macro regime shadow fixtures
- `96253967d9410bc9ad259d1f1d5dc4aeb6efb055` — add macro regime shadow fixture replay validator
- `58509114c84ee1118c930fa38f89c5ec23551903` — run macro regime fixture replay in shadow validation workflow
