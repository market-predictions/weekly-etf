# Deterministic Regime Report Integration Visual QA Status

## Work package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

## Status

```text
started / pending fresh report artifact / not closed
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

## Missing evidence for WP27 closeout

WP27 still needs a fresh rendered report artifact, or fresh EN/NL markdown/PDF outputs, generated after the WP26 commits.

Required fresh output evidence:

```text
English markdown or PDF containing the new deterministic review-only line
Dutch markdown or PDF containing the new deterministic review-only line
```

## Visual/readability checks

Check the English report for:

```text
Deterministic regime read — review-only
This does not authorize portfolio changes
The normal discipline gates remain decisive
```

Check the Dutch report for:

```text
Deterministische regime-inschatting — alleen ter review
Dit geeft geen autoriteit voor portefeuillewijzigingen
De normale discipline blijft leidend
```

Check both reports for absence of:

```text
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition
workflow_run_id
commit_sha
output/macro/validation
.json
```

## Suggested local validation commands

After pulling latest main and generating a fresh report, run the report-surface validators again:

```bash
git pull --ff-only
PYTHONPATH=. python tools/validate_macro_report_surface.py --self-test
PYTHONPATH=. python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json
```

Then inspect the newly generated report files:

```bash
rg "Deterministic regime read|Deterministische regime-inschatting" output/weekly_analysis_pro*.md
rg "macro_axes|macro_axis_scores|macro_evidence|confidence_decomposition|workflow_run_id|commit_sha|output/macro/validation|\.json" output/weekly_analysis_pro*.md
```

The first grep should find the safe review-only lines in the fresh reports.

The second grep should not find these blocked internal terms in the fresh current report files.

## Closeout condition

WP27 can close only after fresh generated EN/NL report artifacts are inspected and the output evidence is recorded.

## Next package after WP27

If visual QA passes, the next package should be normal report-generation/delivery validation, not new deterministic regime logic.
