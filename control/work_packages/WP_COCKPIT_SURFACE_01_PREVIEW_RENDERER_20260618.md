# Work Package — WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER

Repository:

```text
market-predictions/weekly-etf
```

Do not touch:

```text
market-predictions/weekly-etf-eu
market-predictions/weekly-index
market-predictions/weekly-fx
```

## Layer

```text
output contract + operational runbook
```

## Status

```text
not_started
```

## Purpose

Create the isolated cockpit-first preview renderer for the US Weekly ETF report.

The current production report must remain intact. This package creates a parallel preview surface only.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
```

Then inspect the minimum relevant files:

```text
runtime/render_etf_report_from_state.py
runtime/delivery_html_overrides.py
send_report_runtime_html.py
runtime/equity_curve_png_contract.py
runtime/equity_curve_svg_contract.py
```

## Claim rule

Before editing, check whether this work package is already claimed or in progress.

If it is already claimed by another worker:

```text
stop and report the claim; change nothing
```

If unclaimed, claim narrowly by recording the claim in `control/NEXT_ACTIONS.md` or a package handover file before product-code edits.

## Scope

In scope:

- Add a deterministic cockpit preview renderer.
- Render a cockpit-first front page from existing runtime state.
- Write preview output only under `output/cockpit_preview/`.
- Preserve English and Dutch support.
- Add focused tests for the renderer if required.

Out of scope:

- production report replacement
- production send behavior
- email delivery changes
- portfolio state mutation
- pricing changes
- target-weight changes
- lane scoring changes
- fundability changes
- trade ledger changes
- valuation history mutation
- UCITS / ETF EU mapping
- broker availability
- PRIIPs/KID layer
- Box 3 / Dutch tax layer

## Required implementation direction

Create a new renderer, expected path:

```text
runtime/render_cockpit_front_page.py
```

The renderer should read existing artifacts, preferably through current runtime-state helpers:

```text
output/runtime/latest_etf_report_state_path.txt
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
```

It should output preview artifacts only:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.pdf
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.pdf
```

## Required cockpit content

The first preview should include:

```text
masthead
plain-language short summary
market climate / regime card
this week's action card
performance & risk card
main discipline point
```

The mock-up direction may be used as inspiration, but the renderer must not hardcode example values such as GLD -> GSG unless those are actually present in the runtime state.

## Design constraints

- Preserve determinism.
- Avoid external font/network dependencies in the render path.
- Keep current production report untouched.
- Keep the classic report and cockpit preview comparable side by side.
- Use reader-facing language; do not expose internal engine terms on the cockpit surface.

## Minimum tests/checks

Run focused checks appropriate to the implementation, plus:

```bash
python -m py_compile runtime/render_cockpit_front_page.py
pytest tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
git diff --check
```

If new tests are added, include them in the handover.

## Handover requirement

Write a handover under:

```text
control/handovers/HANDOVER_COCKPIT_SURFACE_01_PREVIEW_RENDERER_<yyyymmdd_hhmm>.md
```

The handover must include:

```text
package title
claim status
files changed
what was implemented
what was not implemented
tests/checks run
preview artifact paths, if generated
remaining risks
next recommended package
commit SHA
```

## Expected output

At closeout, the repo should have an isolated cockpit preview renderer while the current production report remains unchanged.
