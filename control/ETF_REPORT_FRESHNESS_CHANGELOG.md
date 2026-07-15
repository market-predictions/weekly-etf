# ETF Report Freshness and Standalone HTML — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`

## 2026-07-16 — Client-surface freshness defect identified

The `260714_03` English and Dutch reports correctly reflected the executed URNM-to-XBI rotation, but retained stale editorial memory in other sections.

Confirmed defects:

- persistent AI and gold conditions appeared under `What changed / Wat veranderde`;
- the 2026-06-11 ECB rate event was described as happening `this week` in the 2026-07-14 report;
- IEFA was funded at approximately 24% while non-U.S. exposure was described as absent/watchlist-only;
- PPA was described as the current defense implementation although official state contained DFEN;
- standalone HTML depended on a MIME CID for the equity graph;
- Dutch output contained mixed-language fragments.

## 2026-07-16 — Authority decisions

```text
What changed / Wat veranderde is delta-only.
Current runtime positions override static portfolio-memory wording.
Dated events may use relative-week wording only inside the report-week window.
Standalone HTML must be self-contained and may not depend on MIME CID resources.
```

PPA may remain as a challenger or candidate; only stale incumbent/current-position wording is replaced.

## 2026-07-16 — Implementation started

Added:

```text
runtime/report_freshness_contract.py
runtime/standalone_html_equity_embed.py
tools/apply_report_freshness_integration_patch.py
tools/apply_report_freshness_followup_patch.py
tools/render_report_freshness_preview.py
tests/test_report_freshness_and_html_equity.py
control/work_packages/WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH_20260716.md
```

Planned integration points:

```text
runtime/build_macro_policy_pack.py
runtime/macro_report_surface.py
runtime/link_runtime_report_tickers.py
send_report_runtime_html.py
```

## Validation status

Pending focused CI and exact-artifact `_04` replay. No email delivery is authorized by this package.
