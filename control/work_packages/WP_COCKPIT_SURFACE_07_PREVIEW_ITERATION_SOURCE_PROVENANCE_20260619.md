# WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE

Date: 2026-06-19
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-preview-source-provenance`
Layer: output contract + input/state contract
Status: implemented / validation pending in Codespaces

## Purpose

Improve source/provenance clarity and trust-evidence visibility in the preview-only cockpit surface.

## Scope

Preview-only iteration. The cockpit remains not promoted.

## Files changed

```text
runtime/render_cockpit_front_page.py
tests/test_cockpit_source_provenance.py
control/work_packages/WP_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619.md
control/handovers/HANDOVER_COCKPIT_SURFACE_07_PREVIEW_ITERATION_SOURCE_PROVENANCE_20260619_2015.md
```

## Boundaries

```text
production_report_change: none
delivery_change: none
state_change: none
pricing_change: none
runtime_state_change: none
run_manifest_change: none
delivery_manifest_change: none
```

## Expected output

The cockpit preview visibly includes a source/evidence section in English and Dutch, while continuing to write only under `output/cockpit_preview/`.

## Validation pending

Codespaces validation still needs to be run and recorded in the handover.
