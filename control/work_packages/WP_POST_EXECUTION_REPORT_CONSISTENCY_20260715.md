# WP_POST_EXECUTION_REPORT_CONSISTENCY

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Layer: output contract + operational runbook
Status: closed

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

1. Post-execution finalization exposed `executed_model_changes` and cleared the pre-execution rotation plan.
2. Downstream renderer and polish layers could fall back to stale `suggested_action` values.
3. Markdown and HTML decision-cockpit layers could inject static no-action wording.
4. The executed-report validator did not enforce semantic agreement across Sections 1, 2, 12, 13, 14 and 15 and the delivery cockpit.
5. The first correction runbook used obsolete SMTP secret names and expected JSON delivery manifests although the production sender emits text manifests.

## Implemented change

1. `executed_model_changes` is authoritative for all post-execution action wording.
2. English and Dutch Add, Reduce, Close, Hold and replaceable-review buckets are derived from executed state.
3. URNM renders as `Reduce — executed` / `Verlagen — uitgevoerd`.
4. XBI renders as `Add — executed` / `Toevoegen — uitgevoerd`.
5. Sections 1, 2, 12, 13, 14 and 15 are aligned.
6. Delivery HTML cockpit content is derived from corrected Markdown.
7. A blocking semantic validator rejects cross-section contradictions.
8. Correction delivery reuses the existing execution artifact and proves portfolio-state and trade-ledger immutability.
9. A non-sending evidence-recovery path can regenerate and persist report assets from an already successful delivery transcript without sending duplicate emails.

## Stable authority rules

- `executed_model_changes` is authoritative for post-execution action classification.
- Official portfolio state is authoritative for post-execution shares, values and holdings.
- Official trade ledger is authoritative for executed share deltas.
- `suggested_action` remains research memory only after execution.
- A report with executed changes may not state that no action occurred.
- A correction rerender must reuse the existing execution artifact and must not execute the model mutation again.
- A successful send may be claimed only from a positive delivery-layer receipt; inbox delivery requires a separate inbox receipt.

## Validation evidence

```text
implementation_validation_run: 29442287444
implementation_validation_conclusion: success
corrected_delivery_run: 29455717158
corrected_delivery_receipt: DELIVERY_OK | mode=pro_bilingual
recovery_and_persistence_run: 29455966433
recovery_and_persistence_conclusion: success
```

Validated and verified:

- focused Markdown and delivery-HTML tests passed;
- exact execution-artifact replay did not execute another model mutation;
- English and Dutch reports consistently show URNM reduced and XBI added;
- no stale no-action wording remains;
- English and Dutch HTML/PDF render succeeded;
- English and Dutch SMTP delivery returned without exception;
- English and Dutch messages were confirmed in the Gmail inbox with PDF attachments;
- official portfolio-state SHA-256 was unchanged before/after correction;
- official trade-ledger SHA-256 was unchanged before/after correction.

## Final artifacts

```text
output/weekly_analysis_pro_260714_03.md
output/weekly_analysis_pro_260714_03_clean.md
output/weekly_analysis_pro_260714_03_delivery.html
output/weekly_analysis_pro_260714_03.pdf
output/weekly_analysis_pro_260714_03_equity_curve.png
output/weekly_analysis_pro_nl_260714_03.md
output/weekly_analysis_pro_nl_260714_03_clean.md
output/weekly_analysis_pro_nl_260714_03_delivery.html
output/weekly_analysis_pro_nl_260714_03.pdf
output/weekly_analysis_pro_nl_260714_03_equity_curve.png
output/delivery/weekly_etf_correction_delivery_receipt_2026-07-14_29455717158.txt
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

## Closeout

PR #59 was merged as `907598eff2a08a5d27b8bd2238610ecc83a31d76`.

Corrected artifacts and verified delivery evidence were persisted on `main` in commit `d829e89329656b29be4c1d9b3b4aca75ba46f3b4`.

All implementation, correction, rendering, delivery, persistence, immutability and inbox-receipt gates are satisfied. The work package is closed.
