# WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Layer: operational runbook + delivery evidence contract
Status: in_progress

## Current issue

The successful 2026-07-14 correction required a one-shot bridge and separate recovery helper because the original correction workflow used obsolete mail settings, expected JSON delivery manifests instead of the production text receipt contract, and lacked a canonical recovery mode after delivery succeeded but persistence failed.

## Goal

Provide one deterministic runbook with three explicit modes:

```text
validate_only
recover_no_send
send
```

The modes share one contract module while retaining strict separation:

- `send` requires exact request and dispatch confirmation;
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
```

The one-shot bridge is retired:

```text
.github/workflows/dispatch-corrected-etf-report-bridge.yml
```

## Authority rules

1. The canonical workflow uses the established `MRKT_RPRTS_*` production mail contract.
2. Delivery evidence authority is the persisted `DELIVERY_OK | mode=pro_bilingual` line plus the English and Dutch `*_delivery_manifest.txt` names recorded in that line.
3. A send requires `confirm_correction_resend` in both the request file and the manual workflow dispatch.
4. Recovery removes mail configuration, sets the explicit dry-run flag and uses render-only asset generation.
5. Recovery may not overwrite a different historical receipt.
6. The official portfolio state and trade ledger remain byte-for-byte unchanged.

## Safety boundary

```text
cleanup_email_send: false
cleanup_portfolio_model_execution: false
cleanup_official_state_mutation: false
cleanup_official_trade_ledger_mutation: false
cleanup_historical_delivery_evidence_mutation: false
```

Only the read-only PR validation workflow is authorized during this cleanup.

## Required gates

- affected Python modules compile;
- focused tests pass;
- canonical workflow has no automatic push trigger;
- send path fails without exact dual confirmation;
- recovery source does not invoke the mail delivery entrypoint;
- persisted text receipt validates;
- closed correction manifest validates;
- one-shot bridge is absent;
- official state hash is unchanged;
- official trade-ledger hash is unchanged.

## Closeout evidence

Pending PR validation and merge.
