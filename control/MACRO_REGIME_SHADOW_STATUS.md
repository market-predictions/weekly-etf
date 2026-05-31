# Macro Regime Shadow Status

## Date
2026-05-31

## Status
Implemented as shadow-only scaffolding. Not yet production-proven by a workflow run.

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

## Current validation route

The separate workflow:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

builds the shadow macro pack using:

```text
python -m runtime.build_macro_policy_pack_shadow
```

Then validates:

```text
python tools/validate_macro_policy_pack.py --pack output/macro/latest.json
python - <<'PY'
from tools.validate_macro_regime_shadow import validate_shadow_payload
...
PY
```

Expected marker:

```text
ETF_MACRO_REGIME_SHADOW_OK
```

## Validation status

Not yet proven by GitHub run evidence through the connector at the time this note was written.

No production report path has been changed to depend on this shadow classifier.

## Next action

1. Verify the `Validate ETF macro regime shadow` workflow run.
2. If it passes, update this file to production-proven shadow validation.
3. If it fails, patch only the shadow workflow/modules.
4. Only after shadow validation passes should we consider adding the shadow field into the main production macro policy pack.

## Commits

- `8f39c282902d1e62c5c25bd1e0e8cdeb03b5b876` — add shadow deterministic regime thresholds
- `82fcce61b6b124f704c58652d8383c38e32afbf8` — add macro_regime package
- `971a12aa4057d602a38f83fe9a3309c55b3e8472` — add shadow deterministic regime confidence model
- `e5474cbcc5301542b6ad8ec443f0bac2118cbb36` — add shadow deterministic regime classifier
- `45459c0f8b41edf16e9b15caa3c641ee3e36f60b` — add shadow deterministic regime macro pack wrapper
- `458d6d2641b65c1348e50456c3ceb40c0263a860` — add minimal shadow regime payload validator
- `6909a458ad9d5d0ca940725b9c67705d82238076` — add shadow macro regime validation workflow
