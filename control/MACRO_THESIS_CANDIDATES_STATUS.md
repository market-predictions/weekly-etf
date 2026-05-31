# Macro Thesis Candidates Status

## Date
2026-06-01

## Status
Phase 5 Stage-1 thesis candidates are implemented and workflow-proven as an internal-only shadow artifact.

They are not connected to:

- client-facing English reports
- Dutch companion reports
- lane scoring
- fundability
- portfolio actions
- final recommendations

## Files added

```text
config/driver_catalog.yml
config/driver_beneficiary_map.yml
runtime/build_thesis_candidates.py
fixtures/thesis_candidates/macro_pack_ai_grid_defense.json
fixtures/thesis_candidates/macro_pack_china_commodity.json
.github/workflows/validate-thesis-candidates-shadow.yml
```

## Authority boundary

The thesis candidate layer has this authority status:

```text
shadow_only: true
client_facing_authority: false
decision_impact: none_stage1_thesis_candidates_only
portfolio_action_authority: false
fundability_authority: false
report_surface_allowed: false
```

Each candidate emitted by the builder must remain:

```text
stage: stage_1_shadow_candidate_only
fundability_status: not_fundable_stage_1_only
portfolio_action: none
client_facing_authority: false
requires_stage_2_confirmation: true
```

## Validation route

The isolated workflow is:

```text
.github/workflows/validate-thesis-candidates-shadow.yml
```

It validates:

```text
python runtime/build_thesis_candidates.py \
  --macro-pack fixtures/thesis_candidates/macro_pack_ai_grid_defense.json \
  --validate-only \
  --expect-driver ai_compute_capex \
  --expect-driver grid_power_demand \
  --expect-driver defense_resilience

python runtime/build_thesis_candidates.py \
  --macro-pack fixtures/thesis_candidates/macro_pack_china_commodity.json \
  --validate-only \
  --expect-driver china_policy_recovery \
  --expect-driver non_us_developed_diversification \
  --expect-driver commodity_inflation_hedge

python runtime/build_thesis_candidates.py \
  --macro-pack output/macro/latest.json \
  --reference-date 2026-05-29 \
  --run-id shadow_validation
```

Expected marker:

```text
ETF_THESIS_CANDIDATES_SHADOW_OK
```

## Workflow proof

Workflow-proven by GitHub Actions screenshot supplied by the user.

Evidence from screenshot:

```text
workflow: Validate ETF thesis candidates shadow
run title: add shadow thesis candidates validation workflow #1
trigger: push
commit: 7a6a1ff
branch: main
status: Success
job: validate-thesis-candidates-shadow
total duration: 13s
```

## Design contract

The driver catalog is closed and versioned. The beneficiary map uses existing ETF discovery universe `taxonomy_tag` values so the thesis layer does not create a separate taxonomy.

The builder validates that every candidate `taxonomy_tag` exists in:

```text
config/etf_discovery_universe.yml
```

## Next action

Move to Phase 6 only after preserving the Stage-1 boundary:

1. Add Stage-2 confirmation discipline.
2. Require active thesis driver plus documented driver-to-beneficiary rationale.
3. Require relative-strength or direct duel confirmation.
4. Require valuation-grade pricing.
5. Keep valuation/crowding as a caution flag, not automatic hard block.
6. Do not make any candidate fundable until all Stage-2 gates pass.
