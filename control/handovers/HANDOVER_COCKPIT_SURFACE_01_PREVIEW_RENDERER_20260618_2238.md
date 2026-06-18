# Handover — WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER

Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-front-page-v1`

## Package title

`WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER`

## Claim status

Claimed / in progress on `feature/cockpit-front-page-v1`.

## Layer

`output contract + operational runbook`

## Files changed

```text
control/NEXT_ACTIONS.md
runtime/render_cockpit_front_page.py
tests/test_cockpit_front_page_preview.py
control/handovers/HANDOVER_COCKPIT_SURFACE_01_PREVIEW_RENDERER_20260618_2238.md
```

## What was implemented

Added a preview-only cockpit front-page renderer at:

```text
runtime/render_cockpit_front_page.py
```

The renderer reads the latest runtime state pointer, valuation history, and client-safe regime context when available. It writes separate preview artifacts under:

```text
output/cockpit_preview/
```

It supports English and Dutch HTML previews and optional PDF rendering when WeasyPrint is available.

Suggested CLI:

```bash
python -m runtime.render_cockpit_front_page --output-dir output --html-only
python -m runtime.render_cockpit_front_page --output-dir output --language both
```

Added focused tests at:

```text
tests/test_cockpit_front_page_preview.py
```

The tests cover separate preview output, front-page markers, English/Dutch generation, basic client-surface language guardrails, non-overwrite of a classic report fixture, and no mutation of fixture state/history files.

## What was not implemented

No production report replacement.
No production send-path change.
No preview workflow yet.
No promotion into production front matter.
No ETF EU / UCITS work.
No broker, PRIIPs/KID, Box 3, or tax layer.

## Tests/checks run

Not run in this connector-only handoff environment.

Required next validation:

```bash
python -m py_compile runtime/render_cockpit_front_page.py
pytest tests/test_cockpit_front_page_preview.py tests/test_delivery_html_decision_cockpit.py tests/test_pdf_surface_decision_cockpit.py tests/test_report_decision_clarity.py tests/test_report_weight_basis_labels.py tests/test_report_bilingual_takeaway_parity.py
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
git diff --check
```

Optional smoke test:

```bash
python -m runtime.render_cockpit_front_page --output-dir output --html-only
ls -la output/cockpit_preview/
```

## Preview artifact paths

No live preview artifacts were generated in this environment.

Expected after local smoke test:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.html
```

PDF paths may also be created if PDF dependencies are available and `--html-only` is omitted.

## Mutation statement

The renderer is preview-only and writes to `output/cockpit_preview/`.

It does not intentionally change portfolio state, valuation history, trade ledger, pricing artifacts, runtime artifacts, run manifests, delivery manifests, or production report names.

## Remaining risks

The renderer still needs local/CI validation.
The first visual surface is an MVP and may need PDF spacing and typography tuning after review.
PDF output is optional for this package and depends on WeasyPrint availability.

## Recommended next package

After local validation passes:

```text
WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW
```

or:

```text
WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS
```

Do not promote the cockpit surface before side-by-side review and explicit approval.

## Commit SHA

```text
7f09167ffedddc8743b91c34cc106daebd4f3283 — claim package
ae31bbbef0b08fba0604ddf6216956041365af00 — add preview renderer
e51bf512fb9c18f7e04b89c2009a13194d4d677f — add focused tests
```
