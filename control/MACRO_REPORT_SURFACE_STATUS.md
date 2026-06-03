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
→ production pre-send delivery guard
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

It sanitizes internal vocabulary before report use and now includes source-level Dutch replacements for macro memory, decision-rule, and portfolio-implication strings.

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

Added production delivery-entrypoint guard:

```text
runtime/macro_report_pre_send_guard.py
send_report_runtime_html.py
```

The guard runs before SMTP delivery from the runtime HTML delivery entrypoint and blocks sending if the already-rendered English/Dutch markdown or delivery HTML leaks macro/thesis internals or fails macro compliance.

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
612fa545f021a4bd2abd380b2545ddaa948ad0c1  add production macro report pre-send guard
419a3c6096cef59cb6fb1a66e839f5c7a787d1dd  enforce macro report guard before runtime HTML delivery
fe1a4a809f1b79382512115185db40ef9d070d9b  localize Dutch macro report surface text at source
b6631167ea94483eff127b6675437882a26e7c29  complete Dutch macro dashboard source localization
```

## Validation status

### Isolated validation

Validated by the isolated macro report-output workflow in GitHub Actions.

User-provided UI evidence shows:

```text
workflow/job: validate-macro-report-output
status: passed
duration: 9s
observed_at: 2026-06-03
```

This is sufficient to treat the isolated no-secrets macro report-output validation workflow as green for the current stage.

### Production validation

Validated by a fresh production send workflow run after the Dutch macro-surface localization fix.

User-provided UI evidence shows:

```text
workflow: Send weekly ETF Pro report
run title: request weekly ETF rerun after Dutch macro surface localization fix #201
status: success
duration: 4m 35s
trigger_commit: fec9ff7cf53257891a4c6ef227a173e92ccdf4fb
observed_at: 2026-06-03
```

Repo evidence from the resulting manifest:

```text
run_id: 20260603_165723
requested_close_date: 2026-06-02
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
english_report_path: output/weekly_analysis_pro_260602_04.md
dutch_report_path: output/weekly_analysis_pro_nl_260602_04.md
runtime_state_path: output/runtime/etf_report_state_20260602_20260603_165723.json
pricing_audit_path: output/pricing/price_audit_2026-06-02_20260603_165723.json
total_portfolio_value_eur: 112376.10
```

Do not overstate this as recipient receipt. The manifest still has:

```text
delivery_manifest_path: null
```

The user explicitly paused delivery-receipt development; workflow/send success is sufficient for the current macro-regime integration track, but not proof of recipient-side receipt.

## Current output evidence

The English report now includes client-facing macro/geopolitical/regime content in:

```text
## 1. Executive Summary
## 3. Regime Dashboard
```

The Dutch report now includes native macro/geopolitical/regime content in:

```text
## 1. Kernsamenvatting
## 3. Regime-dashboard
```

The successful report confirmed the Dutch macro surface passed the production workflow. A follow-up source fix was added after reviewing the generated Dutch report, because two English macro-pack sentences were still visible in the Dutch Regime Dashboard even though validation passed. The source-level fix should remove those in the next generated report.

## Expected validation markers for future log review

```text
ETF_MACRO_REPORT_SURFACE_OK
ETF_MACRO_REPORT_OUTPUT_OK
ETF_MACRO_COMPLIANCE_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
ETF_MACRO_REPORT_PRE_SEND_GUARD_OK
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

1. Optionally trigger one more fresh report after commit `b6631167ea94483eff127b6675437882a26e7c29` to confirm the Dutch Regime Dashboard no longer contains English macro memory/decision-rule sentences.
2. Then update `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and the session changelog with final production-run evidence.
3. Continue with macro policy pack schema hardening and promotion contract work before expanding macro/thesis authority further.
