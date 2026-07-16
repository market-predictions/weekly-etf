# Handover — Post-execution correction runbook

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Package: `WP_POST_EXECUTION_CORRECTION_RUNBOOK_CLEANUP`
Status: closed

## Canonical files

```text
.github/workflows/resend-corrected-post-execution-report.yml
runtime/post_execution_correction_runbook.py
runtime/run_post_execution_correction_delivery.py
runtime/recover_post_execution_correction_evidence.py
```

Modes:

```text
validate_only
recover_no_send
send
```

## Stable rules

- the workflow is manual-only;
- the guarded send mode requires confirmation in both request and dispatch;
- a previously used correction suffix is rejected;
- the established `MRKT_RPRTS_*` configuration is authoritative;
- the bilingual positive text receipt and its two `.txt` manifest names are evidence authority;
- recovery removes mail configuration and uses render-only generation;
- recovery restores original report files if regeneration would change historical evidence;
- state and ledger hashes are checked before and after every operation.

## Evidence

```text
PR #72
merge_commit: 7e3a4516418e7a0413ea1d4b8b21a66d9dab8fb7
final_validated_head: b4aa326eefc42784537cb5baba76544ac59618ed
runbook_validation_run: 29520607344
post_execution_consistency_run: 29520608204
```

## Baselines

`_03` remains the latest verified client package. `_04` remains non-delivered review evidence.

## Next action

Select and claim the next ETF roadmap package. The recommended continuation is validation of `WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER`, with output restricted to `output/cockpit_preview/` and no production promotion.
