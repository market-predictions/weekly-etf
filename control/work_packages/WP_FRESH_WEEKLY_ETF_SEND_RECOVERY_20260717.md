# WP_FRESH_WEEKLY_ETF_SEND_RECOVERY

Date: 2026-07-17
Status: active

Recover the failed report delivery after run `20260717_154351`.

The existing `XLU -> PAVE` state change is already persisted and must not be repeated.

Acceptance:
- identify the failing post-render gate;
- make the smallest repair;
- validate the existing report package;
- send only after validation;
- require a delivery manifest and Gmail receipt.
