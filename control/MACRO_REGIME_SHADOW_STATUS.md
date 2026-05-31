# Macro Regime Shadow Status

## Date
2026-06-01

## Status
Implemented, fixture-replayed, and workflow-proven as shadow-only scaffolding.

Repo-visible proof now exists:

```text
output/macro/validation/latest_macro_regime_shadow_validation.json
```

The evidence file reports:

```text
artifact_type: macro_regime_shadow_validation_evidence
status: passed
workflow.name: Validate ETF macro regime shadow
workflow.run_number: 8
workflow.run_attempt: 1
workflow.run_id: 26726251811
workflow.commit_sha: 348a43f6c2afbae34d8c78c129865a773030e8a2
candidate_regime: Risk-on narrow leadership
legacy_regime: Risk-on growth
differs_from_legacy: true
```

## Authority rule

The deterministic regime engine remains shadow-only. The evidence file explicitly records no client-facing authority and no production-report-path change. Do not use this shadow result for report wording, lane scoring, fundability, or portfolio actions until a later control-layer promotion decision is made after methodology, compliance, bilingual, and production-report gates.

## What changed

Core shadow files:

- `config/regime_thresholds.yml`
- `macro_regime/__init__.py`
- `macro_regime/confidence.py`
- `macro_regime/classify.py`
- `runtime/build_macro_policy_pack_shadow.py`
- `tools/validate_macro_regime_shadow.py`
- `fixtures/macro_regime_shadow/regime_shadow_fixtures.json`
- `tools/replay_macro_regime_shadow_fixtures.py`
- `tools/write_macro_regime_shadow_validation_evidence.py`
- `.github/workflows/validate-macro-regime-shadow.yml`

Latest hardening:

- import path fixed for fixture replay
- workflow-level `PYTHONPATH: .` added
- repo-native evidence writer added
- evidence commit detection fixed to detect untracked JSON files

## Current validation route

The isolated workflow performs:

```text
python tools/replay_macro_regime_shadow_fixtures.py
python -m runtime.build_macro_policy_pack_shadow
python tools/validate_macro_policy_pack.py --pack output/macro/latest.json
validate deterministic_regime_shadow payload
python tools/write_macro_regime_shadow_validation_evidence.py
commit output/macro/validation/*.json
```

Expected markers:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_EVIDENCE_OK
```

Repo evidence confirms the first two markers and writes the dedicated evidence JSON after the workflow succeeds.

## Next action

Move to methodology/compliance gates before any client-facing macro/regime expansion:

1. Add a methodology note for allowed versus blocked macro/regime wording.
2. Add a macro compliance validator.
3. Keep deterministic regime output internal until the validator and bilingual gates exist.
4. Only later consider thesis candidates and Stage-2 confirmation.

## Relevant commits

- `895648d8c37a7b116fd255d27c4e973ebc8b1d68` — add macro regime shadow validation evidence writer
- `d994e08db319187f08cf6e2668c7e218d61b56ca` — commit shadow macro regime validation evidence after pass
- `c7c930c77dde6385d22a692a98356b6e1fbc0110` — trigger shadow macro regime validation evidence workflow
- `348a43f6c2afbae34d8c78c129865a773030e8a2` — fix shadow evidence commit detection
