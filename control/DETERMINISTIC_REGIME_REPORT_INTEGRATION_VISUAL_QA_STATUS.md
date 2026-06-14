# Deterministic Regime Report Integration Visual QA Status

## Work package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

## Status

```text
started / validator green / pending fresh report artifact / not closed
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
```

The report-text search was not completed because `rg` was unavailable and the fallback `grep` was run against all historical output files before a fresh report was generated.

Historical `.json` hits in older April reports are pricing-audit references, not deterministic-regime leakage.

## Missing evidence for WP27 closeout

WP27 still needs a fresh rendered report artifact, or fresh EN/NL markdown/PDF outputs, generated after the WP26 commits.

Required fresh output evidence:

```text
English markdown or PDF containing the new deterministic review-only line
Dutch markdown or PDF containing the new deterministic review-only line
```

## Generate fresh markdown reports

Run:

```bash
PYTHONPATH=. python runtime/render_etf_report_from_state.py --output-dir output
```

The command prints:

```text
ETF_RUNTIME_RENDER_OK | en=<fresh_en_path> | nl=<fresh_nl_path>
```

Use those exact two fresh paths for the checks below.

## Visual/readability checks

Check the fresh English report for:

```text
Deterministic regime read — review-only
This does not authorize portfolio changes
The normal discipline gates remain decisive
```

Check the fresh Dutch report for:

```text
Deterministische regime-inschatting — alleen ter review
Dit geeft geen autoriteit voor portefeuillewijzigingen
De normale discipline blijft leidend
```

Check both fresh reports for absence of:

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

After generating a fresh report, replace the placeholders with the exact paths printed by the renderer:

```bash
grep -nE "Deterministic regime read|Deterministische regime-inschatting" <fresh_en_path> <fresh_nl_path>
grep -nE "macro_axes|macro_axis_scores|macro_evidence|confidence_decomposition|workflow_run_id|commit_sha|output/macro/validation" <fresh_en_path> <fresh_nl_path>
```

The first grep should find the safe review-only lines in the fresh reports.

The second grep should return no matches in the fresh reports.

## Closeout condition

WP27 can close only after fresh generated EN/NL report artifacts are inspected and the output evidence is recorded.

## Next package after WP27

If visual QA passes, the next package should be normal report-generation/delivery validation, not new deterministic regime logic.
