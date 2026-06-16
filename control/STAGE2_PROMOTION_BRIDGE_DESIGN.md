# Stage-2 Promotion Bridge Design

## Status

Design-only. No production wiring.

This bridge is a control-layer design for a future promotion-review path. It does not promote Stage-2 output and it does not change production report output, lane scoring, fundability, portfolio actions, delivery behavior, execution behavior, or historical output files.

## Purpose

Define how a future Stage-2 shadow confirmation result could become eligible for a later promotion review without granting authority inside this package.

The bridge sequence is:

```text
Stage-2 shadow confirmation
→ promotion-review eligibility
→ explicit future control-layer decision
→ separate future implementation package
```

Stage-2 confirmation remains shadow-only until a later explicit promotion decision exists.

## Relationship to existing contract

This design complements `control/STAGE2_THESIS_PROMOTION_CONTRACT.md`.

The existing contract defines the chain evidence shape for a Stage-2 thesis promotion artifact. This bridge defines the higher-level review path, authority boundaries, bilingual alias dependency, and validation gates before any future implementation package may consider integration.

## Four-layer bridge

### 1. Decision framework

A later promotion review would need to decide whether a Stage-2 shadow-confirmed lane is eligible for a separate future implementation package.

The decision review may consider only whether the evidence chain is complete and whether the client-surface wording can be made safe. It must not itself create a trade, recommendation, portfolio action, fundability decision, delivery action, or production report mutation.

### 2. Input/state contract

A future review may consider only explicit artifacts and controls, including:

```text
output/macro/validation/latest_stage2_confirmation_validation.json
output/macro/latest_stage2_confirmation.json
output/macro/latest_thesis_candidates.json
output/market_history/etf_relative_strength.json
output/pricing/price_audit_<requested_close_date>_<run_id>.json
output/etf_portfolio_state.json
output/etf_recommendation_scorecard.csv
config/stage2_confirmation_rules.yml
config/driver_catalog.yml
config/driver_beneficiary_map.yml
config/macro_thesis_bilingual_aliases.yml
control/CAPITAL_REUNDERWRITING_RULES.md
control/STAGE2_THESIS_PROMOTION_CONTRACT.md
```

No prompt memory, chat summary, prior report prose, or raw internal reasoning may substitute for those artifacts.

### 3. Output contract

Any future client-facing wording may be proposed only after a later explicit control-layer decision and separate implementation package.

If that later package is approved, output wording must use sanitized bilingual terminology from `config/macro_thesis_bilingual_aliases.yml` and must pass leakage, compliance, Dutch-language, and report-surface validators.

Raw Stage-1, Stage-2, internal, driver, authority, shadow, workflow, or artifact labels must not become client-facing wording.

### 4. Operational runbook

This package adds design and validation only. It does not add production runtime wiring.

Before any future implementation package is considered, the following checks must pass:

```text
Stage-2 shadow validation evidence exists and is passed
pricing-lineage validation is complete for the relevant run
bilingual sanitized alias exists if client wording is proposed
leakage firewall passes
macro/report-surface compliance passes
Dutch language quality passes if Dutch output is touched
promotion-review artifact schema validates
explicit control-layer promotion decision exists
```

## Authority boundaries

Stage-2 confirmation remains not production authority.

The required false/no-authority fields are:

```text
client_facing_authority: false
production_report_narrative_authority: false
portfolio_action_authority: false
lane_scoring_authority: false
fundability_authority: false
portfolio_mutation: false
historical_output_mutation: false
delivery_authority: false
execution_authority: false
report_surface_allowed: false
production_report_path_changed: false
```

A complete evidence chain may at most become eligible for future promotion review. It does not become fundable, recommended, client-facing, executable, or report-authoritative inside this design.

## Prerequisite artifacts

A future promotion-review candidate must cite exact artifact paths and run identifiers for:

```text
Stage-2 shadow confirmation evidence
Stage-1 thesis candidate source
relative-strength / market confirmation source
valuation-grade pricing source
portfolio discipline clearance source
bilingual alias source
leakage/compliance validator outputs
```

## Eligible evidence fields

A future review may consider these evidence classes:

```text
active thesis driver exists
documented driver-to-beneficiary rationale exists
relative-strength / market confirmation passes
valuation-grade pricing exists
portfolio discipline clearance exists
valuation/crowding caution is recorded where relevant
bilingual sanitized alias exists if any client wording is proposed
leakage firewall passes
macro/report-surface compliance passes
```

## Forbidden direct-use fields

The following must not be used directly for client wording, scoring, fundability, or portfolio actions:

```text
driver_id
driver_ids
active_drivers
driver_catalog
driver_beneficiary_map
stage_1_candidate
stage_2_confirmed_not_fundable
stage_2_fundable_ready_shadow
stage2_status
confirmation_status
shadow_only
internal_only
client_facing_authority
lane_scoring_authority
fundability_authority
portfolio_action_authority
report_surface_allowed
```

These fields may exist in internal artifacts and validators, but they must not appear on the client surface.

## Bilingual alias dependency

WP29 is a prerequisite for any later client-surface wording proposal.

A future bridge candidate must show that any proposed public-facing English and Dutch labels are sanitized and present in `config/macro_thesis_bilingual_aliases.yml` or a later explicitly approved successor file.

If Dutch terminology is missing, literal, mixed-language, or not validator-approved, the candidate is not promotion-review ready.

## Promotion-review checklist

A future candidate is promotion-review eligible only if all of the following are true:

```text
active thesis driver exists
documented driver-to-beneficiary rationale exists
relative-strength / market confirmation passes
valuation-grade pricing exists
portfolio discipline clearance exists
valuation/crowding caution is recorded where relevant
pricing lineage is complete
bilingual sanitized alias exists if client wording is proposed
leakage firewall passes
macro/report-surface compliance passes
Dutch terminology is available and validator-approved if Dutch output is proposed
explicit no-authority fields remain false until a later promotion decision
```

A candidate is not promotion-review ready if any of the following are true:

```text
pricing lineage is incomplete
relative strength confirmation is absent
valuation-grade pricing is missing
portfolio discipline clearance is missing
raw driver IDs are needed to understand the client-facing claim
Dutch terminology is not available
any Stage-1/Stage-2/internal/shadow label leaks to client surface
any validator fails
```

## Explicit non-goals

This package does not:

```text
promote Stage-2 output
change production report wording
change Dutch report generation
change lane scoring
change fundability
change portfolio actions
change delivery behavior
change execution behavior
mutate historical outputs
```

## Future implementation gate

A future implementation package may be considered only after:

```text
this bridge design validates
Stage-2 promotion-review artifact schema exists
promotion-review checklist validator exists
all leakage/compliance/bilingual validators pass
an explicit control-layer promotion decision is recorded
```

Until then, Stage-2 output remains shadow-only evidence and review material only.
