# ETF Macro Report Surface Status

## Snapshot date
2026-06-03

## Current issue

The user paused the delivery-confirmation workstream and asked to continue macro/geopolitical/regime integration into the Weekly ETF report.

The existing runtime already loaded `output/macro/latest.json`, but the English and Dutch report text still had partly hardcoded regime/geopolitical wording. The Dutch native report in particular was not using the shared macro policy pack surface because the polish layer skipped native Dutch macro integration.

## Root cause

There was no explicit bridge between:

```text
output/macro/latest.json
→ runtime state
→ client-safe English/Dutch macro report wording
→ compliance/leakage validation
```

Raw shadow fields such as `deterministic_regime_shadow`, `macro_axes`, `macro_axis_scores`, authority flags, driver IDs, or Stage-1 thesis candidates still must not be copied directly into the client report.

## Implemented change

Added a shared client-safe macro/geopolitical/regime surface:

```text
runtime/macro_report_surface.py
```

This surface renders:

- English executive-summary macro lines
- Dutch executive-summary macro lines
- English Regime Dashboard surface
- Dutch Regime Dashboard surface
- current regime
- confidence
- regime memory
- decision rule
- Fed / ECB stance
- policy/geopolitical status
- portfolio implications
- selected report-transfer policy catalysts

It sanitizes internal vocabulary before report use.

Updated:

```text
runtime/polish_runtime_reports.py
```

The polish layer now injects the shared surface into:

```text
English:
- ## 1. Executive Summary
- ## 3. Regime Dashboard
- Structural Opportunity Radar macro filter notes

Dutch:
- ## 1. Kernsamenvatting
- ## 3. Regime-dashboard
```

Added validator:

```text
tools/validate_macro_report_surface.py
```

The validator proves that the shared surface renders from the macro pack without:

- predictive market/central-bank wording
- internal shadow labels
- driver IDs
- Stage-1/Stage-2 leakage
- direct authority-field leakage

Updated isolated compliance workflow:

```text
.github/workflows/validate-macro-compliance.yml
```

Added isolated read-only report-output workflow:

```text
.github/workflows/validate-macro-report-output.yml
```

This workflow has no SMTP/email secrets and validates committed macro pack/report artifacts only.

## Commits

```text
98f07312ac5f0e7820c4011a6a4abfc90f441727  add client-safe macro report surface builder
e1fbf7faf6d8ca5485bb38ae4e4e351dcdf0cf38  apply client-safe macro surface to English and Dutch reports
2f384147e87bd8e88501f41626d6b8c78f01495f  add macro report surface validator
d4ab9873c5120b73160ad4eb567bffd070870990  wire macro report surface validator into compliance workflow
4f1f79f14942a3950d4a85cf6fd965554ce6b08d  add isolated macro report output validation workflow
81dd6f29602435ba0930e6cbeeb9b99cb3871da8  register macro report surface workflow and validators in system index
```

## Validation status

Validated by the isolated macro report-output workflow in GitHub Actions.

User-provided UI evidence shows:

```text
workflow/job: validate-macro-report-output
status: passed
duration: 9s
observed_at: 2026-06-03
```

This is sufficient to treat the isolated no-secrets macro report-output validation workflow as green for the current stage.

Do not overstate this as a fresh production-send validation. It proves the isolated macro surface/output validation job passed. It does not prove a fresh production report was sent, and it does not by itself prove the production send workflow has a pre-send macro surface guard.

Expected validation markers for future log review remain:

```text
ETF_MACRO_REPORT_SURFACE_OK
ETF_MACRO_REPORT_OUTPUT_OK
ETF_MACRO_COMPLIANCE_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

## Authority boundary

Allowed now:

- client-safe descriptive macro/regime summary
- current regime from `output/macro/latest.json`
- confidence as descriptive model confidence
- Fed/ECB stance wording from the macro pack
- selected policy catalysts marked `transfer_to_report: true`
- portfolio implications as discipline context

Still not allowed:

- raw `deterministic_regime_shadow`
- raw `macro_axes`
- raw `macro_axis_scores`
- Stage-1 thesis candidates
- driver IDs
- macro output as direct lane-scoring/fundability/portfolio-action authority beyond existing legacy-compatible macro pack behavior
- predictive wording about market levels or central-bank actions

## Next action

1. Add production-send pre-send validation through a safe path. The direct full-file edit of `send-weekly-report.yml` was blocked by the tool safety layer because the workflow contains SMTP secret references.
2. Safer production integration path: add a helper script or small workflow patch through a review/PR route that inserts only validation commands and does not expose or rewrite the secret block.
3. Trigger a fresh weekly ETF report run and verify the generated English/Dutch reports use the shared macro surface without leakage.
4. Then update `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and the session changelog with production-run evidence.
