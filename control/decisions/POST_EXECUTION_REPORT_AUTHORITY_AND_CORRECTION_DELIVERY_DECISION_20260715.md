# Decision — Post-Execution Report Authority and Correction Delivery

Date: 2026-07-15
Repository: `market-predictions/weekly-etf`
Status: adopted

## Decision

For a post-execution ETF report, `executed_model_changes` is the authoritative action-classification source for every client-facing action surface.

Official portfolio state remains authoritative for holdings, shares, values and weights. Official trade ledger remains authoritative for executed share deltas.

Research-memory fields such as `suggested_action` may provide context but may not override an executed Buy, Sell, Reduce, Close or Add.

## Output-contract consequence

When executed changes exist, all of these surfaces must describe the same state:

```text
Section 1 main takeaway
Section 2 action snapshot
Section 2A decision cockpit
Section 12 rotation plan
Section 13 final action table
Section 14 official-state changes
Section 15 current holdings
English delivery HTML/PDF
Dutch delivery HTML/PDF
```

A report with executed changes may not state that no portfolio action occurred.

## Correction-delivery consequence

A report-surface correction after an already persisted model mutation must:

1. reuse the existing execution artifact;
2. avoid portfolio-selection reruns and duplicate model execution;
3. prove official portfolio state and trade ledger remain unchanged;
4. require explicit send confirmation;
5. distinguish rendering, SMTP delivery-layer evidence and inbox-receipt evidence;
6. avoid duplicate resend when SMTP already succeeded but evidence persistence failed;
7. support non-sending evidence recovery from an actual successful delivery transcript.

## Evidence

This decision was proven by the July 14 correction package:

```text
production_execution_run: 20260715_175910
implementation_validation_run: 29442287444
corrected_delivery_run: 29455717158
recovery_and_persistence_run: 29455966433
persistence_commit: d829e89329656b29be4c1d9b3b4aca75ba46f3b4
```

Final manifest:

```text
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

## Scope boundary

This decision governs post-execution output consistency and correction delivery. It does not change the decision framework, pricing authority, lane scoring, fundability rules, rotation thresholds or portfolio-mutation policy.
