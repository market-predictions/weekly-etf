# ETF Post-Execution Report Consistency — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_POST_EXECUTION_REPORT_CONSISTENCY`

## 2026-07-15 — Production surface contradiction identified

Run `20260715_175910` executed and persisted one guarded model rotation:

```text
URNM: Sell, -105.862854 shares, model weight 7.01% -> 2.01%
XBI: Buy, +35.634001 shares, model weight 0.00% -> 5.00%
```

The official state and trade ledger were correct, but the English and Dutch reports mixed executed-state evidence with stale no-action wording. The decision cockpit said no action occurred, while Section 14 showed the actual sale and purchase.

## 2026-07-15 — Output-authority design

Stable rule introduced:

```text
executed_model_changes is authoritative for all post-execution action wording and classification.
```

The report may use recommendation and lane data for research context, but an executed Buy/Sell may not be overwritten by stale `suggested_action` memory.

## 2026-07-15 — Implementation staged

Added `runtime/post_execution_report_surface.py` with:

- deterministic executed-change classification;
- English and Dutch action buckets;
- dynamic main takeaways;
- dynamic decision cockpits;
- dynamic post-execution rotation tables;
- executed-action labels for final action tables;
- a blocking cross-section consistency validator.

Staged integration targets:

```text
runtime/polish_runtime_reports.py
runtime/fix_report_output_contract.py
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/fix_executed_report_contract.py
```

The validator rejects:

- no-action wording when executed changes exist;
- a changed ticker in the wrong Section 2 action bucket;
- a changed ticker in the wrong Section 12 action column;
- a Section 13 row without the correct executed-action label.

## Validation pending

The exact execution artifact will be replayed without invoking model execution again:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
```

Corrected report delivery is not claimed until the focused tests, exact-artifact replay, PR merge, correction rerender/resend, delivery manifest and inbox receipt checks all pass.