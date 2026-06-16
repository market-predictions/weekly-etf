# Weekly ETF fresh report send request

requested_at_local: 2026-06-16 23:15 Europe/Amsterdam
requested_at_utc: 2026-06-16 21:15 UTC
repository: market-predictions/weekly-etf
workflow: Send weekly ETF Pro report
trigger_type: run_queue_push
source_handover: control/handovers/HANDOVER_WEEKLY_ETF_20260616_SEND_RUN_HTML_GUARD.md

## Purpose

Start a new production workflow run for the user request:

```text
Send fresh weekly ETF reports
```

This is a new run-queue trigger, not a rerun of failed jobs #251 or #252.

## Guard expectations

The current patches should make delivery/PDF validators bind to the explicit current report paths instead of stale lexicographic delivery HTML artifacts.

Expected workflow path if green:

1. Validate ETF delivery HTML contract
2. Send email
3. Write ETF delivery manifest summary
4. Write final ETF run manifest
5. Validate ETF manifest evidence
6. Commit ETF run artifacts back to main

## Authority boundaries

```text
deterministic_regime_engine_promoted=false
production_report_narrative_authority=false
portfolio_action_authority=false
```

Delivery success must not be claimed unless workflow and delivery/final manifest evidence exist. SMTP sendmail success is not an inbox receipt.
