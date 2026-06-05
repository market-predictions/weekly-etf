# Weekly ETF report request

Date: 2026-06-05

Purpose:

Trigger a fresh Weekly ETF Pro production run after fixing the Dutch client-surface validation order for stale GLD wording.

The previous run correctly failed before delivery because `tools/validate_etf_dutch_client_surface_clean.py` detected stale GLD current-surface phrases in the Dutch report:

- `GLD blijft een hedgepositie onder herbeoordeling`
- `GLD moet zijn hedgefunctie bewijzen`
- `GLD: hedge-validiteitstest vereist`
- `Herbeoordeling goudhedge`
- `Houd GLD onder herbeoordeling`

This request verifies that the validator now applies the central client-surface scrub before enforcing the stricter stale-GLD block.

Validation focus after completion:

- Dutch stale GLD current-surface wording must be scrubbed before validation.
- Section 7A must keep semantic thesis labels.
- GSG must use commodity-breadth hedge thesis wording in English and Dutch.
- Delivery evidence remains SMTP-send manifest evidence only, not inbox receipt.
