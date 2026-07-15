# WP_POST_EXECUTION_REPORT_CONSISTENCY

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-post-execution-report-consistency`
Layer: output contract + operational runbook
Status: implementation staged / validation pending

## Current issue

The production run `20260715_175910` correctly executed and persisted a guarded model mutation from URNM into XBI, but the final English and Dutch client surfaces contained contradictory legacy wording:

- Section 14 correctly showed the executed URNM sale and XBI purchase;
- Section 15 correctly showed the post-execution official holdings;
- Section 2 did not show URNM under Reduce;
- the decision cockpit said no portfolio action occurred;
- Section 12 treated URNM as Hold;
- Section 13 retained stale suggested-action labels instead of executed-action labels.

The state, trade ledger and execution artifact are correct. The defect is confined to the post-execution output contract.

## Root cause

1. `runtime/finalize_executed_etf_report.py` correctly overlays `executed_model_changes`, but intentionally clears the pre-execution rotation plan after official persistence.
2. Several downstream render and polish layers fall back to stale `suggested_action` fields when the rotation plan is absent.
3. `runtime/polish_runtime_reports.py` injects a static no-action cockpit and static takeaway.
4. The native Dutch renderer hard-codes `Verlagen: Geen` and `Sluiten: Geen`.
5. `runtime/fix_executed_report_contract.py` validates Section 14 and proposed/pending language but does not validate Sections 1, 2, 12 and 13 against `executed_model_changes`.

## Required change

1. Treat `executed_model_changes` as the authoritative post-execution action source.
2. Derive English and Dutch action buckets from the executed changes.
3. Render dynamic takeaways and decision cockpits that describe the executed mutation.
4. Render Section 2 with XBI under Add and URNM under Reduce.
5. Render Section 12 with the same executed buckets.
6. Render Section 13 with `Add — executed` / `Reduce — executed` and Dutch equivalents.
7. Preserve Section 14 as the official shares-and-weights execution table.
8. Add a blocking validator that rejects no-action wording or cross-section action contradictions whenever executed changes exist.
9. Replay the exact execution artifact `output/runtime/etf_model_execution_20260714_20260715_175910.json` and validate both languages.

## Files

```text
runtime/post_execution_report_surface.py
runtime/polish_runtime_reports.py
runtime/fix_report_output_contract.py
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/fix_executed_report_contract.py
tests/test_etf_post_execution_report_consistency.py
.github/workflows/validate-etf-post-execution-report-consistency.yml
control/work_packages/WP_POST_EXECUTION_REPORT_CONSISTENCY_20260715.md
control/ETF_POST_EXECUTION_REPORT_CONSISTENCY_CHANGELOG.md
control/POST_EXECUTION_REPORT_CONSISTENCY_STATUS_20260715.md
control/handovers/HANDOVER_POST_EXECUTION_REPORT_CONSISTENCY_20260715.md
```

## Authority rules

- `executed_model_changes` is authoritative for actions shown on a post-execution report.
- Official portfolio state is authoritative for post-execution shares, values and holdings.
- `suggested_action` remains research memory only after execution and may not override an executed Buy/Sell.
- A post-execution report with an executed change may not say that no action occurred.
- Sections 1/2/12/13/14/15 must describe one coherent executed state.
- A correction rerender/resend must use the existing execution artifact and must not execute the model mutation again.

## Validation plan

```text
python -m py_compile runtime/post_execution_report_surface.py runtime/polish_runtime_reports.py runtime/fix_report_output_contract.py runtime/render_etf_report_from_state.py runtime/render_etf_report_nl_from_state.py runtime/fix_executed_report_contract.py
python -m pytest -q tests/test_etf_post_execution_report_consistency.py
python -m runtime.finalize_executed_etf_report --artifact output/runtime/etf_model_execution_20260714_20260715_175910.json
```

The PR workflow must assert in both languages:

```text
cockpit: mutation executed and persisted
Section 2: Reduce URNM; Add XBI
Section 12: Reduce URNM; Add XBI
Section 13: URNM Reduce executed; XBI Add executed
Section 14: official shares/weight deltas preserved
Section 15: official post-execution holdings preserved
no no-action contradiction
```

## Completion boundary

The package is complete only after:

1. focused tests and exact-artifact replay pass;
2. PR merge succeeds;
3. corrected EN/NL reports are rerendered from the existing execution artifact without duplicate mutation;
4. corrected delivery manifests are persisted;
5. corrected inbox receipts are confirmed;
6. control state is updated with both the production mutation and correction evidence.