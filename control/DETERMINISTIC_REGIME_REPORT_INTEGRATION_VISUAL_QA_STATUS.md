# Deterministic Regime Report Integration Visual QA Status

## Work package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

## Status

```text
started / validator green / pending polished fresh report artifact / not closed
```

## Scope

WP27 is a closeout and visual/readability QA package for the WP26 deterministic regime report integration.

It must not add new report logic, change portfolio state, change lane scoring, change fundability, change delivery behavior, or rewrite historical generated outputs.

## Current evidence already available

WP26 is closed based on manual Codespace validation evidence:

```text
output/macro/validation/deterministic_regime_report_integration_validation_20260613_codespace.json
```

Observed WP26 validation evidence:

```text
5 passed in 0.05s
18 passed in 0.06s
ETF_MACRO_REPORT_SURFACE_OK | label=fixture | en_chars=2088 | nl_chars=2318
ETF_MACRO_REPORT_SURFACE_OK | label=output/macro/latest.json | en_chars=2455 | nl_chars=2674
```

## WP27 partial QA evidence

Repo evidence artifact:

```text
output/macro/validation/deterministic_regime_report_visual_qa_partial_20260613_codespace.json
```

Observed user-reported evidence:

```text
git pull --ff-only: passed
PYTHONPATH=. python tools/validate_macro_report_surface.py --self-test: passed
PYTHONPATH=. python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json: passed
PYTHONPATH=. python runtime/render_etf_report_from_state.py --output-dir output: passed
```

The raw renderer created:

```text
output/weekly_analysis_pro_260612_11.md
output/weekly_analysis_pro_nl_260612_11.md
```

The deterministic review-only line was not present in the raw rendered markdown because the shared macro report surface is applied by the polish step.

Production order:

```text
runtime/render_etf_report_from_state.py
→ runtime/polish_runtime_reports.py
```

Historical `.json` hits in older April reports are pricing-audit references, not deterministic-regime leakage.

## Missing evidence for WP27 closeout

WP27 still needs fresh polished EN/NL markdown or PDF outputs generated after the WP26 commits.

Required fresh output evidence:

```text
English polished markdown or PDF containing the new deterministic review-only line
Dutch polished markdown or PDF containing the new deterministic review-only line
```

## Generate and polish fresh markdown reports

Run both commands:

```bash
PYTHONPATH=. python runtime/render_etf_report_from_state.py --output-dir output
PYTHONPATH=. python runtime/polish_runtime_reports.py --output-dir output
```

The first command prints:

```text
ETF_RUNTIME_RENDER_OK | en=<fresh_en_path> | nl=<fresh_nl_path>
```

The polish step updates the latest matching EN/NL report files in place.

Use the exact two fresh paths printed by the render command for the checks below.

## Visual/readability checks

Check the fresh polished English report for:

```text
Deterministic regime read — review-only
This does not authorize portfolio changes
The normal discipline gates remain decisive
```

Check the fresh polished Dutch report for:

```text
Deterministische regime-inschatting — alleen ter review
Dit geeft geen autoriteit voor portefeuillewijzigingen
De normale discipline blijft leidend
```

Check both fresh polished reports for absence of:

```text
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition
workflow_run_id
commit_sha
output/macro/validation
```

## Suggested local validation commands

After generating and polishing a fresh report, replace the placeholders with the exact paths printed by the renderer:

```bash
grep -nE "Deterministic regime read|Deterministische regime-inschatting" <fresh_en_path> <fresh_nl_path>
grep -nE "macro_axes|macro_axis_scores|macro_evidence|confidence_decomposition|workflow_run_id|commit_sha|output/macro/validation" <fresh_en_path> <fresh_nl_path>
```

The first grep should find the safe review-only lines in the fresh polished reports.

The second grep should return no matches in the fresh polished reports.

## Closeout condition

WP27 can close only after fresh polished EN/NL report artifacts are inspected and the output evidence is recorded.

## Next package after WP27

If visual QA passes, the next package should be normal report-generation/delivery validation, not new deterministic regime logic.
