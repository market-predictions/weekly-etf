# Rerun trigger

Requested because the latest **Validate ETF macro regime shadow** run was not visible in Actions after push-hardening.

This file is intentionally placed under `fixtures/macro_regime_shadow/**`, which is part of the workflow push trigger.

Expected workflow:

```text
Validate ETF macro regime shadow
```

Expected result:

```text
validation passes
evidence commit succeeds
latest_macro_regime_shadow_validation.json updates to this rerun
```
