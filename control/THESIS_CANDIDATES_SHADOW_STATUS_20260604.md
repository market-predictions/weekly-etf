# Thesis Candidates Shadow Status

Snapshot date: 2026-06-04

## Current issue

Stage-1 thesis candidates must remain internal-only shadow artifacts until Stage-2 confirmation and explicit control-layer promotion gates exist and pass.

The latest task was to make the thesis candidate workflow produce repo-visible validation evidence without promoting the candidate artifact to production input.

## Implemented change

Added validation evidence writer:

```text
tools/write_thesis_candidates_validation_evidence.py
```

Updated workflow:

```text
.github/workflows/validate-thesis-candidates-shadow.yml
```

The workflow now:

```text
validates thesis candidate fixtures
builds current shadow thesis candidates
writes validation evidence
commits only output/macro/validation/*thesis_candidates*.json
```

## Validation evidence

Latest confirmed run:

```text
workflow: Validate ETF thesis candidates shadow
run_number: 2
workflow_run_id: 26969716983
trigger_commit: b0579f1f30134b4fdd1b277025867e9db87961da
status: passed
branch: main
duration: 16s
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot and repo-visible evidence file
```

Repo-visible evidence:

```text
output/macro/validation/latest_thesis_candidates_validation.json
```

Evidence summary:

```text
artifact_type: stage_1_thesis_candidates_validation_evidence
status: passed
active_driver_count: 9
candidate_count: 29
reference_date: 2026-05-29
run_id: shadow_validation
```

Active drivers recorded in evidence:

```text
ai_compute_capex
china_policy_recovery
commodity_inflation_hedge
defense_resilience
duration_easing_long_duration
grid_power_demand
healthcare_defensive_growth
non_us_developed_diversification
nuclear_energy_security
```

## Authority boundary

The evidence explicitly preserves:

```text
shadow_only: true
client_facing_authority: false
decision_impact: none_stage1_thesis_candidates_only
production_report_path_changed: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
report_surface_allowed: false
```

Every candidate must remain:

```text
client_facing_authority: false
fundability_status: not_fundable_stage_1_only
portfolio_action: none
requires_stage_2_confirmation: true
```

## Work-package status

Stage-1 thesis candidate shadow validation evidence: closed for this stage.

This does not promote thesis candidates to client-facing, lane-scoring, fundability, portfolio-action, or report recommendation authority.

## Next action

Continue with Stage-2 promotion discipline design only as a contract, not as authority promotion:

```text
runtime/valuation_sanity.py
runtime/score_etf_lanes.py
runtime/discover_etf_lanes.py
challenger/fundability validators
```

Goal: define the required chain from active driver to beneficiary rationale to relative-strength confirmation to valuation-grade pricing to portfolio-discipline clearance before any thesis candidate can become fundable later.
