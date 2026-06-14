# Deterministic Regime Report Integration Visual QA Status

## Work package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

## Status

```text
started / punctuation repaired / revalidation needed / not closed
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

## WP27 visual QA finding

A fresh polished report showed the deterministic review-only lines correctly and no blocked deterministic internal terms.

However, visual QA found a small client-facing punctuation issue:

```text
changes.; The normal discipline gates remain decisive.
wijzigingen.; De normale discipline blijft leidend.
```

This has been repaired in:

```text
runtime/deterministic_regime_client_surface.py
tests/test_deterministic_regime_report_surface_integration.py
```

New regression protection requires no `.;` in the English or Dutch deterministic safe surface.

## Revalidation required

Run after pulling latest main:

```bash
git pull --ff-only
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_report_surface_integration.py -q
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_client_surface_validator.py tests/test_deterministic_regime_client_surface_helper.py tests/test_deterministic_regime_report_surface_integration.py -q
PYTHONPATH=. python tools/validate_macro_report_surface.py --self-test
PYTHONPATH=. python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json
PYTHONPATH=. python runtime/render_etf_report_from_state.py --output-dir output
PYTHONPATH=. python runtime/polish_runtime_reports.py --output-dir output
```

Then use the exact fresh paths printed by the render command:

```bash
grep -nE "Deterministic regime read|Deterministische regime-inschatting" <fresh_en_path> <fresh_nl_path>
grep -nE "\.\;|macro_axes|macro_axis_scores|macro_evidence|confidence_decomposition|workflow_run_id|commit_sha|output/macro/validation" <fresh_en_path> <fresh_nl_path>
```

Expected:

```text
first grep: finds both review-only lines
second grep: no matches
```

## Closeout condition

WP27 can close only after the revalidation output is recorded.
