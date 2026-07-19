# Work Package — WP_FRESH_REPORT_DELIVERY_GATE_DIAGNOSTIC

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Status: claimed / diagnostic in progress

## Trigger

Two explicitly authorized report-only production runs (`20260719_001444` and `20260719_002755`) built and persisted corrected runtime state but ended with `workflow_failure` before HTML/PDF delivery. Both delivery manifests are null and no email was sent.

## Scope

Isolate the first failing post-persistence boundary against the exact latest committed runtime state, without sending email or mutating canonical portfolio, ledger, valuation, pricing, historical report, or delivery state.

## Acceptance criteria

- run the persisted valuation validator against `etf_report_state_20260717_20260719_002755.json`;
- run ledger-idempotency validation;
- execute the guarded wrapper only against temporary copies with report execution authority false;
- validate the temporary guarded artifact;
- assert the cockpit lineage state remains `PAVE 0.0% → 4.94%` and `XLU 5.4908% → 0.52%`;
- use the first failing diagnostic step as the repair target;
- no email delivery and no canonical state mutation.
