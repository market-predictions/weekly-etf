# ETF Macro Policy Pack Contract Status

## Snapshot date
2026-06-03

## Current issue

The macro report surface is now production-validated, but the macro policy pack needed an explicit field-level authority and promotion contract before any future macro/regime/thesis authority expansion.

Without this contract, future work could accidentally treat shadow-only fields such as `deterministic_regime_shadow`, `macro_axes`, `macro_axis_scores`, `active_drivers`, or confidence decomposition as client-facing or decision-authoritative.

## Root cause

The legacy macro policy pack had useful report context and `lane_adjustments`, but the pack did not yet explicitly mark each field as one of:

```text
client-safe descriptive surface
descriptive-only context
legacy-compatible decision input
shadow-only internal evidence
blocked from client surface
blocked from decision authority
```

## Implemented change

Updated schema:

```text
schemas/macro_policy_pack.schema.json
```

The schema now requires:

```text
authority
field_authority
promotion_gates
```

Updated builder:

```text
runtime/build_macro_policy_pack.py
```

The builder now emits:

```text
authority.authority_class: legacy_compatibility_pack
authority.client_surface_allowed: true
authority.decision_authority: legacy_lane_adjustments_only
field_authority
promotion_gates.status: not_promoted
```

Updated validator:

```text
tools/validate_macro_policy_pack.py
```

The validator now enforces:

- all required field-authority entries exist
- client-surface allowed fields are limited to the approved descriptive surface
- shadow/internal fields are not client-surface allowed
- `deterministic_regime_shadow` remains `none_shadow_comparison_only`
- `active_drivers` remain `none_wp9_not_promoted`
- `promotion_gates.status` remains `not_promoted`
- required promotion blockers remain present

Updated methodology:

```text
MACRO_METHODOLOGY.md
```

It now documents the top-level authority rule, field-level authority classes, promotion gates, and blocked authority types.

Added isolated no-secrets validation workflow:

```text
.github/workflows/validate-macro-policy-pack-contract.yml
```

The workflow builds and validates both:

```text
runtime/build_macro_policy_pack.py
runtime/build_macro_policy_pack_shadow.py
```

and proves that the promotion firewall rejects accidental client-surface promotion of `deterministic_regime_shadow`.

## Commits

```text
c0bf4975c03638b3569a8e95636d962a5745359f  add macro policy pack authority contract schema
e180553e2d665087bf60dc6c9317c542ff88ebb0  emit macro policy pack authority contract
b3e665b848e95d3a28d4dc2329604954dc9747ed  enforce macro policy pack promotion firewall
e773363e19c0723e4077cb95082a6f71ad9641db  document macro policy pack promotion contract
5488096f37b4c3095be0a3109858f20fcb096b93  add macro policy pack contract validation workflow
359ee240f3484d5240bc49773566080f55782d68  trigger macro policy pack contract validation workflow
```

## Validation status

Validated by isolated GitHub Actions workflow.

User-provided UI evidence shows:

```text
workflow: Validate ETF macro policy pack contract
run: #2
trigger_commit: 359ee240f3484d5240bc49773566080f55782d68
status: passed
duration: 1m 47s
observed_at: 2026-06-03
```

Expected workflow markers:

```text
ETF_MACRO_POLICY_PACK_OK
ETF_MACRO_POLICY_PACK_SCHEMA_OK
ETF_MACRO_POLICY_PACK_PROMOTION_FIREWALL_OK
```

The GitHub connector did not expose the Actions run through `fetch_commit_workflow_runs`, so the current evidence is user-provided UI confirmation plus committed workflow/validator code.

## Current authority boundary

Allowed now:

```text
regime: client-safe descriptive only
central_banks: client-safe descriptive only
policy_catalysts: client-safe descriptive only
portfolio_implications: client-safe discipline context
report_transfer: output-contract filter
lane_adjustments: legacy-compatible lane input only
```

Still blocked:

```text
raw macro_axes on client surface
raw macro_axis_scores on client surface
deterministic_regime_shadow on client surface
Stage-1 thesis candidates on client surface
macro direct lane-scoring authority
macro direct fundability authority
macro direct portfolio-trade authority
```

## Current work-package status

Macro policy pack schema / promotion contract: **closed for this stage**.

This does not promote macro/regime/thesis output to direct portfolio authority. It gives future phases a validated contract and firewall.

## Next action

Continue with deterministic regime/confidence review in shadow mode:

```text
macro_regime/classify.py
macro_regime/confidence.py
runtime/build_macro_policy_pack_shadow.py
config/regime_thresholds.yml
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json
```

Goal: compare legacy macro regime output versus deterministic shadow output under the new authority contract, without changing production decisions.
