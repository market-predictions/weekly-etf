# Decision — Adopt Two-Role Governance for Weekly ETF

## Date

2026-08-05

## Decision

Adopt `CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1` for consequential Weekly ETF work.

The user continues to issue one instruction. Internally:

- `implementation_operations` prepares the report, state change, workflow change, or release candidate;
- `governance_release_assurance` independently reconstructs the candidate and issues `PASS`, `FAIL`, or `INDETERMINATE`.

Implementation may not certify its own completion. Governance may not silently modify the candidate it certifies.

## Current maturity

```text
current=LEVEL_1_CHECKLIST
target=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
```

Existing pricing-lineage, manifest, rendering, language, and inbox-receipt controls remain valid. They do not become independent assurance merely by being relabeled.

## Required follow-up

Create `control/ETF_RELEASE_ASSURANCE_CONTRACT_V1.md`, machine-readable assurance evidence, a hard pre-send gate, and post-send independent closeout verification.

## Authority boundary

This decision changes governance and reporting semantics only. It does not authorize portfolio mutation, report generation, email delivery, resend, or production workflow execution.
