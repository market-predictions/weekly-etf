# ETF Macro Methodology

## Purpose

This document defines the methodology and compliance boundary for the Weekly ETF macro/regime/thesis workstream.

It is an internal control document. It does not by itself promote any macro/regime output into client-facing report authority.

## Current authority status

The macro/regime modernization track is shadow-first.

The current production report may use the legacy macro policy pack compatibility path, but the deterministic macro-regime shadow engine is not client-facing authority yet.

Until a later control-layer promotion decision is made, the shadow engine may produce internal comparison artifacts only.

It must not change:

- client-facing regime wording
- confidence wording
- lane scoring
- fundability
- portfolio actions
- final recommendations
- Dutch companion wording

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
