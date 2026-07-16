# WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Layer: operational runbook + delivery evidence contract
Status: validated_ready_for_merge

## Current issue

The successful 2026-07-14 correction required a one-shot bridge and separate recovery helper because the original correction workflow used obsolete mail settings, expected JSON delivery manifests instead of the production text receipt contract, and lacked a canonical recovery mode after delivery succeeded but persistence failed.

## Outcome

One deterministic runbook now provides three explicit modes:

```text
validate_only
recover_no_send
send
```

The modes share one contract module while retaining strict separation:

- `send` requires exact request and dispatch confirmation and an unused correction suffix;
- `recover_no_send` regenerates report assets and evidence without invoking the mail delivery entrypoint;
- `validate_only` performs no rendering, delivery, portfolio execution or state mutation.

## Implementation scope

```text
runtime/post_execution_correction_runbook.py
runtime/run_post_execution_correction_delivery.py
runtime/recover_post_execution_correction_evidence.py
.github/workflows/resend-corrected-post-execution-report.yml
.github/workflows/validate-post-execution-correction-runbook.yml
tools/validate_post_execution_correction_runbook.py
tests/test_post_execution_correction_runbook.py
control/decisions/POST_EXECUTION_CORRECTION_RUNBOOK_DECISION_20260716.md
```

The one-shot bridge is retired:

```text
.github/workflows/dispatch-corrected-etf-report-bridge.yml
```

## Authority rules

1. The canonical workflow uses the established `MRKT_RPRTS_*` production mail contract.
2. Delivery evidence authority is the persisted `DELIVERY_OK | mode=pro_bilingual` line plus the English and Dutch `*_delivery_manifest.txt` names recorded in that line.
3. A send requires `confirm_correction_resend` in both the request file and the manual workflow dispatch.
4. A send refuses an already-used correction suffix and cannot overwrite an existing correction package.
5. Recovery removes mail configuration, sets the explicit dry-run flag and uses render-only asset generation.
6. Recovery restores original bytes and fails if existing historical report artifacts would change.
7. Recovery may not overwrite a different historical receipt.
8. Current official portfolio-state and trade-ledger hashes are compared before and after each operation. Historical manifest hashes remain historical evidence rather than a permanent current-state constraint.

## Safety boundary

```text
cleanup_email_send: false
cleanup_portfolio_model_execution: false
cleanup_official_state_mutation: false
cleanup_official_trade_ledger_mutation: false
cleanup_historical_delivery_evidence_mutation: false
```

Only read-only PR validation was executed during this cleanup. Neither `send` nor `recover_no_send` was dispatched.

## Validation evidence

Exact validated implementation head before governance recording:

```text
head_sha: ef3c9628c422994b8a2f54455db2f640ad32b970
correction_runbook_validation_run: 29520376036
correction_runbook_validation_conclusion: success
post_execution_consistency_run: 29520376034
post_execution_consistency_conclusion: success
PR: #72
```

Validated gates:

- affected Python modules compile;
- focused tests pass;
- canonical workflow has no automatic push trigger;
- send path fails without exact dual confirmation;
- send path cannot overwrite an existing correction package;
- recovery source does not invoke the mail delivery entrypoint;
- recovery strips mail configuration;
- recovery protects existing historical report artifacts transactionally;
- persisted text receipt validates;
- closed correction manifest validates internally;
- one-shot bridge is absent;
- current official state and trade-ledger files remain unchanged during validation.

## Merge closeout

Pending final validation of the governance head and merge of PR #72. Final merge evidence will be recorded in a separate closeout update.
