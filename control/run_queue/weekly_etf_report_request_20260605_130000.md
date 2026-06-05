# Weekly ETF report request

Date: 2026-06-05

Purpose:

Trigger a fresh Weekly ETF Pro production run after report-surface hardening for:

- Section 7A semantic thesis fallback validation
- stale GLD current-surface scrub hardening
- Dutch stale GLD client-surface validation

Expected workflow:

`Send weekly ETF Pro report`

Validation focus after completion:

- Section 7A must not contain ticker-only or generic thesis cells.
- GSG must use commodity-breadth hedge thesis wording, not `Rotation destination`.
- Dutch Section 7A must use the Dutch semantic GSG thesis, not `Rotatiebestemming`.
- GLD must not appear as a current active holding, current hedge review, current action item, or current replacement source when not active.
- Delivery evidence remains SMTP-send manifest evidence only, not inbox receipt.
