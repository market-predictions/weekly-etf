# ETF Macro Methodology

## Purpose

This document defines the methodology and compliance boundary for the Weekly ETF macro/regime/thesis workstream.

It is an internal control document. It does not by itself promote any macro/regime output into client-facing report authority.

## Current authority status

The macro/regime modernization track is shadow-first.

The current production report may use the legacy macro policy pack compatibility path, but the deterministic macro-regime shadow engine is not client-facing authority yet.

Until a later control-layer promotion decision is made, the shadow engine may produce internal comparison artifacts only.

It must not change:

- client-facing regime wording outside the approved client-safe report surface
- confidence wording outside the approved client-safe report surface
- lane scoring beyond current legacy-compatible `lane_adjustments`
- fundability
- portfolio actions
- final recommendations
- Dutch companion wording outside the same authority and language-quality gates

## Macro policy pack authority contract

The macro policy pack must explicitly state its authority model. Every pack must include:

```text
authority.authority_class
authority.client_surface_allowed
authority.decision_authority
field_authority
promotion_gates
```

Current allowed top-level authority is:

```text
authority_class: legacy_compatibility_pack
client_surface_allowed: true
decision_authority: legacy_lane_adjustments_only
shadow_only: true
client_facing_authority: false
decision_impact: legacy_lane_adjustments_only
```

This means the pack may support descriptive macro context in the client-safe report surface and preserve legacy-compatible lane adjustments, but it does not promote the deterministic macro/regime shadow engine to production decision authority.

## Field-level authority classes

The following field-level contract applies until a later control-layer decision changes it:

```text
regime:
  client_surface_allowed: true
  decision_authority: descriptive_only

central_banks:
  client_surface_allowed: true
  decision_authority: descriptive_only

policy_catalysts:
  client_surface_allowed: true
  decision_authority: descriptive_only

portfolio_implications:
  client_surface_allowed: true
  decision_authority: descriptive_only

report_transfer:
  client_surface_allowed: true
  decision_authority: output_contract_only

lane_adjustments:
  client_surface_allowed: false
  decision_authority: legacy_lane_adjustments_only

confidence_decomposition:
  client_surface_allowed: false
  decision_authority: none_shadow_explanation_only

macro_signals:
  client_surface_allowed: false
  decision_authority: none_internal_evidence_only

macro_data_audit_summary:
  client_surface_allowed: false
  decision_authority: none_phase2_audit_only

deterministic_regime_shadow:
  client_surface_allowed: false
  decision_authority: none_shadow_comparison_only

active_drivers:
  client_surface_allowed: false
  decision_authority: none_wp9_not_promoted
```

The validator must fail if a shadow-only field is marked client-surface allowed or if its decision authority is upgraded without an explicit control-layer promotion decision.

## Promotion gates

The macro policy pack must include `promotion_gates.status: not_promoted` until a later control-layer decision changes it.

Decision authority is blocked until all required gates exist and pass:

```text
macro_policy_pack_schema_contract_green
+ deterministic_regime_fixture_replay_green
+ macro_audit_fixture_replay_green
+ macro_compliance_validator_green
+ bilingual_report_surface_validation_green
+ production_report_validation_green
+ explicit_control_layer_promotion_decision
```

The following remain blocked:

```text
raw_macro_axes_client_surface
raw_macro_axis_scores_client_surface
deterministic_regime_shadow_client_surface
stage1_thesis_candidates_client_surface
macro_direct_lane_scoring_authority
macro_direct_fundability_authority
macro_direct_portfolio_trade_authority
```

## Descriptive, not predictive

The macro engine is descriptive. It classifies the current observable macro backdrop from configured inputs and thresholds.

Allowed wording:

- describes current conditions
- describes evidence alignment or disagreement
- describes what the model is observing
- describes why confidence is high, medium, or low
- describes what would need to be confirmed before a candidate becomes fundable

Blocked wording:

- forecasts exact market levels
- predicts central-bank actions as certain
- states that an ETF, index, sector, rate, or currency will move in a specific direction
- presents model output as investment certainty
- converts Stage-1 thesis candidates into client-facing recommendations

## Macro data provenance

Every client-surfaced macro figure must trace to provenance.

For macro data, provenance means the report or upstream artifact can identify at minimum:

- source or provider
- series or field name
- as-of date
- fetch or build time when available
- stale/unavailable status when applicable

A macro figure without provenance is an orphan macro claim and should fail compliance validation before client-facing use.

## Institutional overlay

Institutional overlay is allowed only as curated, cited, paraphrased context.

It may:

- cap confidence
- add caution
- explain disagreement across market narratives

It may not:

- set regime by itself
- create a portfolio action by itself
- replace source-backed macro inputs
- quote long copyrighted research
- appear without citation/provenance

## Thesis candidates

Stage-1 thesis candidates are internal only.

They may identify possible lanes for further review, but they must not appear in client-facing reports as recommendations, tips, or portfolio actions.

A thesis can become fundable only after Stage-2 confirmation gates exist and pass, including:

```text
active thesis driver
+ documented driver to beneficiary rationale
+ relative-strength / duel confirmation
+ valuation-grade pricing
+ portfolio discipline clearance
+ caution flag where valuation/crowding risk is elevated
```

## Client-surface gate

Before any expanded macro/regime/thesis content reaches English or Dutch client-facing output, it must pass a compliance validator that blocks:

- predictive market or central-bank phrasing
- uncited institutional overlay entries
- orphan macro figures
- Stage-1 candidate leakage
- internal labels such as driver IDs, shadow payload names, or config labels

## Bilingual rule

English is canonical. Dutch is a companion render from the same runtime state.

Dutch macro/regime content may not become an independent research pass. Any Dutch client-facing macro wording must pass the same authority and compliance rules as English, plus the Dutch language-quality gate.

## Promotion rule

Promotion from shadow-only to production authority requires an explicit control-layer decision after methodology, compliance, bilingual, and production-report validation gates exist and pass.
