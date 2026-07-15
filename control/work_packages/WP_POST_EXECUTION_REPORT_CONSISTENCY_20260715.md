# WP_POST_EXECUTION_REPORT_CONSISTENCY

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Branch: `agent/fix-post-execution-report-consistency`
Layer: output contract + operational runbook
Status: validated / merge ready

## Current issue

Production run `20260715_175910` correctly executed and persisted a guarded model mutation from URNM into XBI, but the first delivered English and Dutch client surfaces contained contradictory legacy wording. Section 14 and official state showed the execution, while the decision cockpit and other action sections retained stale no-action or hold language.

## Authoritative execution evidence

```text
run_id: 20260715_175910
report_date: 2026-07-14
source_execution_artifact: output/runtime/etf_model_execution_20260714_20260715_175910.json
URNM: Sell -122.008961 shares; model weight 7.01% -> 2.01%
XBI: Buy +40.491749 shares; model weight 0.00% -> 5.00%
```

The execution artifact, official portfolio state and official trade ledger agree on these quantities. Earlier intermediate quantities are not authoritative.

## Root cause

1. Post-execution finalization exposes `executed_model_changes` and clears the pre-execution rotation plan.
2. Downstream renderer and polish layers could fall back to stale `suggested_action` values.
3. Markdown and HTML decision-cockpit layers could inject static no-action wording.
4. The executed-report validator did not enforce semantic agreement across Sections 1, 2, 12, 13, 14 and 15 and the delivery cockpit.

## Implemented change

1. `executed_model_changes` is authoritative for all post-execution action wording.
2. English and Dutch Add, Reduce, Close, Hold and replaceable-review buckets are derived from executed state.
3. URNM renders as `Reduce — executed` / `Verlagen — uitgevoerd`.
4. XBI renders as `Add — executed` / `Toevoegen — uitgevoerd`.
5. Sections 1, 2, 12, 13, 14 and 15 are aligned.
6. Delivery HTML cockpit content is derived from corrected Markdown instead of static no-action copy.
7. A blocking semantic validator rejects cross-section contradictions.
8. A dedicated correction-resend workflow reuses the existing execution artifact and proves portfolio-state and trade-ledger immutability.

## Files

```text
runtime/post_execution_report_surface.py
runtime/decision_cockpit_html.py
runtime/polish_runtime_reports.py
runtime/fix_report_output_contract.py
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/fix_executed_report_contract.py
send_report_runtime_html.py
tests/test_etf_post_execution_report_consistency.py
tests/test_etf_decision_cockpit_html.py
.github/workflows/validate-etf-post-execution-report-consistency.yml
.github/workflows/resend-corrected-etf-report.yml
control/work_packages/WP_POST_EXECUTION_REPORT_CONSISTENCY_20260715.md
control/ETF_POST_EXECUTION_REPORT_CONSISTENCY_CHANGELOG.md
control/POST_EXECUTION_REPORT_CONSISTENCY_STATUS_20260715.md
control/handovers/HANDOVER_POST_EXECUTION_REPORT_CONSISTENCY_20260715.md
```

## Authority rules

- `executed_model_changes` is authoritative for post-execution action classification.
- Official portfolio state is authoritative for post-execution shares, values and holdings.
- Official trade ledger is authoritative for executed share deltas.
- `suggested_action` remains research memory only after execution.
- A report with executed changes may not state that no action occurred.
- A correction resend must reuse the existing execution artifact and must not execute the model mutation again.

## Validation evidence

Final read-only workflow run:

```text
workflow: Validate ETF post-execution report consistency
run_id: 29442287444
conclusion: success
```

Passed gates:

- compile affected production modules;
- focused Markdown and delivery-HTML regression tests;
- exact execution-artifact replay without model re-execution;
- portfolio-state hash unchanged;
- trade-ledger hash unchanged;
- English and Dutch action-surface consistency;
- English and Dutch delivery-cockpit consistency.

## Merge boundary

This package is validated and ready for PR merge. Merge does not complete corrected delivery. After merge, the dedicated correction workflow must be triggered once with explicit confirmation. Delivery closure still requires corrected EN/NL artifacts, positive delivery manifests, a correction manifest and inbox receipt confirmation.