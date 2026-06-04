# Stage-2 Thesis Promotion Contract

## Status

Contract-only. Not promoted.

This document defines the required chain before a Stage-1 thesis candidate may later become fundable. It does not change lane scoring, fundability, portfolio actions, report wording, or recommendations.

## Authority boundary

Stage-1 thesis candidates remain internal-only shadow artifacts.

Stage-2 promotion discipline is a future gate. Until explicit control-layer promotion, every Stage-2 validation artifact must keep:

```text
client_facing_authority: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
report_surface_allowed: false
production_report_path_changed: false
```

## Four-layer contract

### 1. Decision framework

A thesis candidate can become promotion-ready only if the full chain is present:

```text
active thesis driver
+ mapped beneficiary lane
+ documented driver-to-beneficiary rationale
+ relative-strength confirmation
+ valuation-grade pricing
+ portfolio-discipline clearance
+ explicit control-layer promotion decision
```

Without the full chain, the item remains a shadow candidate or research-only candidate.

### 2. Input/state contract

A future Stage-2 promotion check may read only explicit artifacts:

```text
output/macro/latest_thesis_candidates.json
output/macro/validation/latest_thesis_candidates_validation.json
output/lane_reviews/etf_lane_assessment_<report_token>.json
output/market_history/etf_relative_strength.json
output/pricing/price_audit_<requested_close_date>_<run_id>.json
output/etf_portfolio_state.json
output/etf_recommendation_scorecard.csv
control/CAPITAL_REUNDERWRITING_RULES.md
```

No prompt memory, free-text narrative, or prior report wording may substitute for those artifacts.

### 3. Output contract

A Stage-2 validation artifact must expose the chain clearly and remain internal:

```text
stage_2_chain_status
active_driver_id
taxonomy_tag
lane_name
primary_etf
driver_to_beneficiary_rationale
relative_strength_confirmation
valuation_grade_pricing
portfolio_discipline_clearance
missing_requirements
promotion_status
```

Allowed status values:

```text
not_ready_missing_chain
ready_for_promotion_review_not_promoted
blocked_by_authority_boundary
```

Blocked status values until future promotion:

```text
fundable
recommended
portfolio_action_ready
client_facing
```

### 4. Operational runbook

Before any future integration into `runtime/score_etf_lanes.py`, `runtime/discover_etf_lanes.py`, or a future `runtime/valuation_sanity.py`, the following must pass:

```text
validate Stage-1 thesis candidate evidence
validate Stage-2 chain artifact schema
validate relative-strength confirmation source
validate valuation-grade pricing source
validate portfolio-discipline clearance source
validate no client/report surface leakage
validate explicit promotion decision exists
```

## Required chain fields

### Active thesis driver

The driver must come from the closed driver catalog and must appear active in the Stage-1 thesis candidate evidence.

### Beneficiary lane mapping

The candidate `taxonomy_tag` must exist in the ETF discovery universe and must be mapped from the active driver through `config/driver_beneficiary_map.yml`.

### Driver-to-beneficiary rationale

The artifact must preserve a concise rationale explaining why the active driver maps to the beneficiary lane.

### Relative-strength confirmation

Relative-strength confirmation must be artifact-backed. Minimum required fields:

```text
return_1m_pct
return_3m_pct
rs_vs_spy_1m_pct
rs_vs_spy_3m_pct
relative_strength_score
source_artifact
```

A future implementation may set thresholds, but the current contract only requires that the evidence exists and is traceable.

### Valuation-grade pricing

A candidate cannot be Stage-2-ready without valuation-grade pricing.

Required pricing fields:

```text
primary_etf
price_status
pricing_tier: valuation_grade
source
requested_close_date
close_date_used
```

Research-grade pricing is not enough for fundability.

### Portfolio-discipline clearance

Portfolio-discipline clearance must check:

```text
current holding overlap
cash policy / sizing room
capital re-underwriting status
recommendation scorecard memory
replacement or addition rationale
```

The clearance may still return blocked. A blocked clearance means the item is not promotion-ready.

## Explicit promotion decision

Even a complete Stage-2 chain does not itself create fundability or report authority.

The final gate is an explicit control-layer promotion decision recorded in a control file such as:

```text
control/DECISION_LOG.md
```

Until that exists, the maximum allowed status is:

```text
ready_for_promotion_review_not_promoted
```

## Integration boundary

Do not modify these production paths to consume Stage-2 promotion output until the contract and validator are green:

```text
runtime/score_etf_lanes.py
runtime/discover_etf_lanes.py
runtime/build_etf_report_state.py
runtime/render_etf_report_from_state.py
send_report_runtime_html.py
```

## Current next step

Validate this contract with a dedicated contract validator and planted-pass / planted-fail fixtures before implementing any runtime behavior.
