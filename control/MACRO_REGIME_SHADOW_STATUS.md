# Macro Regime Shadow Status

## Date

2026-06-13

## Status

```text
WP19 closed / fixture baseline hardened / workflow-proven as shadow-only
```

Repo-visible proof exists:

```text
output/macro/validation/latest_macro_regime_shadow_validation.json
```

Latest evidence file reports:

```text
artifact_type: macro_regime_shadow_validation_evidence
status: passed
workflow.name: Validate ETF macro regime shadow
workflow.run_number: 46
workflow.run_attempt: 1
workflow.run_id: 27480244857
workflow.commit_sha: 1ba3f4e5a6126fd824a151525b0d9d91d42c3627
candidate_regime: Risk-on growth
legacy_regime: Risk-on growth
differs_from_legacy: true
```

## Authority rule

The deterministic regime engine remains shadow-only. The evidence file explicitly records no client-facing authority, no production report narrative authority, no lane-scoring authority, no fundability authority, no portfolio-action authority, no portfolio mutation, and no historical output mutation.

Do not use this shadow result for report wording, lane scoring, fundability, or portfolio actions until a later control-layer promotion decision is made after methodology, compliance, bilingual, and production-report gates.

Authority fields required by the shadow payload and fixture baseline:

```text
shadow_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
decision_impact=none_shadow_comparison_only
```

## What changed

Core shadow files:

```text
config/regime_thresholds.yml
macro_regime/__init__.py
macro_regime/confidence.py
macro_regime/classify.py
runtime/build_macro_policy_pack_shadow.py
tools/validate_macro_regime_shadow.py
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
tools/replay_macro_regime_shadow_fixtures.py
tools/write_macro_regime_shadow_validation_evidence.py
tests/test_macro_regime_shadow.py
.github/workflows/validate-macro-regime-shadow.yml
```

WP19 hardening:

```text
- deterministic shadow payload now carries explicit no-authority fields
- validator requires all no-authority fields to be present and false
- fixture payload requires all no-authority fields to be present and false
- fixture replay requires coverage of every regime label defined in config/regime_thresholds.yml
- fixture replay rejects duplicate fixture ids
- evidence writer records full no-authority state
- workflow now runs tests/test_macro_regime_shadow.py before fixture replay
```

## Current validation route

The isolated workflow performs:

```text
python -m pytest tests/test_macro_regime_shadow.py -q
python tools/replay_macro_regime_shadow_fixtures.py
python tools/replay_macro_data_audit_shadow_fixture.py
python tools/validate_macro_policy_pack.py --pack output/macro/latest.json
validate deterministic_regime_shadow payload
python tools/write_macro_regime_shadow_validation_evidence.py
python tools/write_macro_regime_shadow_comparison_evidence.py
commit output/macro/validation/*.json
```

Expected markers:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_AXIS_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_EVIDENCE_OK
```

Repo evidence confirms the markers through the latest committed validation artifact.

## Next action

Move to a separate review-only package before any client-facing macro/regime expansion:

```text
WP20 — Deterministic regime engine promotion-review contract
```

WP20 must remain review-only unless a later explicit implementation package is approved. No deterministic macro report narrative authority, scoring authority, fundability authority, or portfolio authority exists yet.

## Relevant commits

```text
85baa8b342177711c9d93878b61d39d11be6d3b2 — Add explicit no-authority flags to regime shadow payload
20138fe669655312aa00af8bc9acfcff5ee65359 — Harden deterministic regime shadow authority validation
261345b6732212d679b2338c821c0b4da8662efb — Validate regime fixture authority and coverage
0498b4ff2d0ca7436a6ce430d6c65834f6e9a7b4 — Add explicit no-authority fields to regime fixtures
baa25de0b7a9300026f3707c2b068db374685af0 — Harden macro regime shadow evidence authority fields
4493e4461f4337e9816a3a05b9dd80e7acfac76c — Test deterministic macro regime shadow fixture baseline
1ba3f4e5a6126fd824a151525b0d9d91d42c3627 — Run WP19 regime shadow tests in workflow
```
