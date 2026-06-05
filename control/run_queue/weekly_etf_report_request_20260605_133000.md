# Weekly ETF report request

Date: 2026-06-05

Purpose:

Trigger a fresh Weekly ETF Pro production run after fixing the Current Position Review score surface.

Issue observed in the successful run:

- Current Position Review showed raw `n/a` scores for active holdings such as CIBR, DFEN, GSG, IEFA and XLU.
- This was confusing in a client-facing review table because active holdings should either show a comparable position-discipline score, a live lane score, or a clear pending-score status.

Patch under verification:

- `runtime/fix_report_output_contract.py` now renders:
  - position score when `total_score` exists
  - live lane score when the position score is not yet available but lane scoring exists
  - `current score pending` only where no comparable score exists yet

Validation focus after completion:

- Current Position Review should not show raw `n/a` score cells.
- CIBR, GSG and IEFA should show lane-score based values if position scores are unavailable.
- DFEN and XLU may show `current score pending` only if no current comparable lane score exists.
- Section 7A must retain semantic thesis labels.
- GLD must not appear as a current active holding, current hedge review, current action item, or current replacement source when not active.
- Delivery evidence remains SMTP-send manifest evidence only, not inbox receipt.
