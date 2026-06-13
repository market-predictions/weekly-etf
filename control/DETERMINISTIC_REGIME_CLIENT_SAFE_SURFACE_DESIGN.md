# Deterministic Regime Client-Safe Surface Design

## Work package

```text
WP21 — Deterministic regime client-safe report surface design
```

## Repository

```text
market-predictions/weekly-etf
```

## Snapshot date

```text
2026-06-13
```

## Layer

```text
output contract
```

## Status

```text
design_only / specification_only / not_implemented / not_promoted
```

## Purpose

WP21 defines the allowed client-safe shape for a possible future deterministic regime report surface.

This package is design only. It does not implement report integration, does not promote the deterministic regime engine, and does not change production reports, state files, scoring files, delivery files, or historical outputs.

## Starting authority

WP20 explicitly keeps the deterministic regime engine not promoted:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

WP21 therefore defines only a possible safe surface contract for a later package.

## Authority boundary

WP21 keeps:

```text
design_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
execution_authority=false
delivery_authority=false
production_report_mutation=false
historical_output_mutation=false
```

## Four-layer distinction

### 1. Decision framework

WP21 does not decide promotion. It defines the safe output shape that would be required before a later implementation package may be considered.

Decision:

```text
safe surface design is defined
production promotion is not granted
production integration is not granted
```

### 2. Input/state contract

A future safe surface may be derived only from committed shadow evidence and comparison evidence:

```text
output/macro/validation/latest_macro_regime_shadow_validation.json
output/macro/validation/latest_macro_regime_shadow_comparison.json
```

The current production macro input remains:

```text
output/macro/latest.json
```

Raw deterministic fields remain blocked from direct report use:

```text
deterministic_regime_shadow
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition
raw authority fields
workflow metadata
fixture names
```

A future implementation must first transform shadow evidence into a narrow client-safe DTO.

Suggested DTO name:

```text
DeterministicRegimeClientSurface
```

Suggested DTO fields:

```text
schema_version
surface_status
surface_mode
source_evidence_path
source_comparison_path
regime_label_en
regime_label_nl
confidence_band_en
confidence_band_nl
comparison_status_en
comparison_status_nl
short_explanation_en
short_explanation_nl
discipline_note_en
discipline_note_nl
authority_disclaimer_en
authority_disclaimer_nl
prohibited_source_fields_confirmed_absent
```

Required DTO authority fields:

```text
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
```

### 3. Output contract

The future client-safe text must be concise, descriptive, and explicitly review-only.

Allowed English shape:

```text
Title: Deterministic regime read — review-only
Sentence 1: The shadow engine currently classifies the backdrop as <regime_label>, broadly aligned / not aligned with the legacy regime read.
Sentence 2: Confidence is described as <low/moderate/high>, based on evidence consistency, not as a forecast.
Sentence 3: This is an internal review signal only; the normal portfolio discipline gates remain decisive.
```

Allowed Dutch shape:

```text
Titel: Deterministische regime-inschatting — alleen ter review
Zin 1: De shadow-engine classificeert de marktomgeving momenteel als <regime_label_nl>, grotendeels in lijn / niet in lijn met de bestaande regime-inschatting.
Zin 2: De betrouwbaarheid wordt beschreven als <laag/gemiddeld/hoog>, op basis van samenhang in het bewijs, niet als voorspelling.
Zin 3: Dit is alleen een intern reviewsignaal; de normale portefeuillediscipline blijft leidend.
```

Allowed concepts:

```text
sanitized regime label
legacy-versus-shadow alignment status
confidence band, not raw score
short explanation of broad confirmation or conflict
discipline disclaimer
```

Blocked concepts:

```text
raw macro axes
raw macro axis scores
raw macro evidence
raw confidence decomposition
raw conflict scores
workflow run ids
fixture names
source file paths in client report
production action wording
scoring or fundability wording
predictive certainty
```

Allowed confidence bands:

```text
0.00 <= confidence < 0.55: low / laag
0.55 <= confidence < 0.72: moderate / gemiddeld
0.72 <= confidence <= 1.00: high but review-only / hoog maar alleen ter review
```

Confidence wording rule:

```text
Confidence describes evidence consistency only. It must not be described as a forecast probability, expected return, or portfolio conviction.
```

Allowed comparison wording:

```text
if regime_label_differs=false: broadly aligned with the legacy regime read
if regime_label_differs=true: different from the legacy regime read and therefore review-only
if confidence_differs=true: confidence differs from the legacy read, but this does not change authority
```

### 4. Operational runbook

WP21 does not add runtime code.

A future WP22 may add a validator or helper that checks a fixture-rendered safe surface for:

```text
no raw macro axes
no raw macro axis scores
no confidence decomposition leakage
no authority field leakage
no predictive wording
no scoring/fundability wording
English and Dutch parity
required authority disclaimer
```

A future implementation package may be considered only after validator coverage exists.

## Required future implementation constraints

A future implementation must preserve these boundaries:

```text
1. Raw shadow evidence is not client-facing.
2. The safe surface is generated from a narrow DTO.
3. Confidence is translated to bands, not numeric precision.
4. Macro conflict is described only as broad confirmation/conflict, never as a raw score.
5. Existing portfolio discipline remains the governing layer.
6. Dutch text must be native Dutch.
7. Evidence paths and workflow IDs remain internal.
```

## Required safe-renderer behavior for a future package

A future safe renderer should expose only:

```text
render_deterministic_regime_surface_en(dto) -> str
render_deterministic_regime_surface_nl(dto) -> str
```

It should not accept the full macro pack or full shadow payload directly.

It should accept only a sanitized DTO that has already dropped blocked fields.

## Example safe English output

```text
Deterministic regime read — review-only: The shadow engine currently classifies the backdrop as Risk-on growth, broadly aligned with the legacy regime read. Confidence is high but review-only, reflecting evidence consistency rather than a forecast. This does not authorize portfolio changes; the normal discipline gates remain decisive.
```

## Example safe Dutch output

```text
Deterministische regime-inschatting — alleen ter review: De shadow-engine classificeert de marktomgeving momenteel als Risk-on groei, grotendeels in lijn met de bestaande regime-inschatting. De betrouwbaarheid is hoog maar alleen ter review en beschrijft samenhang in het bewijs, geen voorspelling. Dit geeft geen autoriteit voor portefeuillewijzigingen; de normale discipline blijft leidend.
```

## Non-goals

WP21 does not:

```text
create runtime renderer code
change runtime/macro_report_surface.py
change report markdown
change report HTML/PDF
change send workflow
change portfolio state
change lane scoring
change fundability
promote deterministic macro
```

## Closeout status

WP21 is complete when this design file is committed and the control layer records the next package.

Next package:

```text
WP22 — Deterministic regime client-safe surface validator
```

WP22 should remain validator/spec-only or helper-only, with no production report integration.
