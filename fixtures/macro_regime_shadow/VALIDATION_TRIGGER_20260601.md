# Macro regime shadow validation trigger — 2026-06-01

Purpose: trigger the isolated `Validate ETF macro regime shadow` workflow after adding repo-native validation evidence output.

This file is not read by `tools/replay_macro_regime_shadow_fixtures.py` and has no production-report authority.

Expected repo-visible result after the workflow passes:

```text
output/macro/validation/latest_macro_regime_shadow_validation.json
```

Expected markers:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_EVIDENCE_OK
```
