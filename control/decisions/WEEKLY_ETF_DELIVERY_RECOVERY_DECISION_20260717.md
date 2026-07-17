# Decision — Persisted-execution delivery recovery

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Status: accepted

## Decision

When a production run has already persisted an authoritative portfolio execution but fails later in the render, validation or delivery layer, recovery must reuse the persisted execution package and must not restart the full production workflow.

The recovery sequence is:

```text
persisted official execution
→ fail-closed package validation and rerender
→ SMTP delivery
→ delivery manifest
→ successful run manifest
→ independent inbox receipt confirmation
```

## Authority rules

1. The persisted portfolio state, trade ledger and execution artifact remain authoritative.
2. Pricing, discovery and guarded execution are not repeated.
3. A protected-file hash mismatch fails recovery before delivery.
4. Existing sendreceipt artifacts fail closed against duplicate sends.
5. SMTP return without exception is transport evidence, not final inbox evidence.
6. Delivery success may be claimed only after both the delivery manifest and an independently observed inbox receipt exist.

## Output-contract rule

Dutch delivery-language validation must inspect visible client text. CSS selectors, class names and non-visible implementation identifiers are not client-facing language. A visible English term must still fail.

## Applied case

```text
run_id: 20260717_154351
persisted_rotation: XLU -> PAVE
repeat_portfolio_execution: false
language_fix_PR: #89
recovery_workflow_PR: #90
delivery_evidence_commit: ddc745fddf0e80a31c4309658743f6435a4d486b
final_status: delivered_and_inbox_confirmed
```

## Consequence

Future late-stage delivery failures should use a genericized version of this recovery pattern rather than creating another run-specific full execution. A separate future package may generalize the current run-specific helper after the position-count constraint is reconciled.
