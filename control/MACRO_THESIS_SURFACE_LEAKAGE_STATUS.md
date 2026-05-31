# Macro Thesis Surface Leakage Status

## Date
2026-06-01

## Status
The macro/thesis client-surface leakage guard is implemented, workflow-proven, repo-visible, and wired into the production ETF send workflow.

This is a guardrail only. It does not promote Stage-1, Stage-2, deterministic regime, or macro/thesis artifacts into client-facing authority.

## Repo-visible proof

Evidence file:

```text
output/macro/validation/latest_macro_thesis_surface_leakage_validation.json
```

Current evidence reports:

```text
artifact_type: macro_thesis_surface_leakage_validation_evidence
status: passed
workflow.name: Validate ETF macro thesis surface leakage
workflow.run_number: 2
workflow.run_id: 26727496265
workflow.commit_sha: 3acef2f5822feb35db0bca2b7b0bcd85cac6ece3
```

Validated markers:

```text
ETF_MACRO_THESIS_SURFACE_LEAKAGE_SELF_TEST_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_EXPECTED_FAILURE_OK
```

## Guard scope

The evidence confirms these output surfaces are guarded:

```text
english_markdown_guard: true
dutch_markdown_guard: true
delivery_html_guard: true
production_send_workflow_wired: true
```

## Files added

```text
tools/validate_etf_macro_thesis_surface_leakage.py
tools/write_macro_thesis_surface_leakage_validation_evidence.py
fixtures/macro_thesis_surface/safe_client_excerpt.md
fixtures/macro_thesis_surface/unsafe_client_excerpt.md
.github/workflows/validate-macro-thesis-surface-leakage.yml
output/macro/validation/latest_macro_thesis_surface_leakage_validation.json
```

## Production workflow wiring

The production workflow:

```text
.github/workflows/send-weekly-report.yml
```

now calls:

```text
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
```

at multiple guard points:

1. after runtime markdown generation and Dutch scrubbing/linking;
2. after report content contract validation;
3. after guarded model rotation scrub/link pass;
4. after HTML/PDF render;
5. inside delivery HTML contract validation.

## Authority boundary

The evidence explicitly records:

```text
shadow_only: true
client_facing_authority: false
macro_thesis_promotion: false
production_report_path_changed: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
```

The validator blocks internal labels such as:

```text
Stage-1 thesis candidate
stage_2_fundable_ready_shadow
latest_thesis_candidates
latest_stage2_confirmation
client_facing_authority
shadow_only
ai_compute_capex
ETF_STAGE2_CONFIRMATION_*
Fase-2 confirmatie
```

## Next action

With leakage blocking in place, the next safe roadmap choice is Phase 7 Dutch quality/alias consolidation, unless the user asks to pause and run a production report validation first.

Do not connect Stage-1 or Stage-2 artifacts to client-facing macro/thesis wording, lane scoring, fundability, or portfolio actions without a later explicit control-layer promotion decision.
