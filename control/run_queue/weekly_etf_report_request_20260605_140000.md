# Weekly ETF report request

Date: 2026-06-05

Purpose:

Trigger a fresh Weekly ETF Pro production run after the remaining Dutch client-surface cleanup.

The `_09` reports confirmed that the Current Position Review score issue is fixed:

- English Current Position Review has numeric scores for every active ETF.
- Dutch Review huidige posities has numeric scores for every active ETF.

Remaining issues observed in the Dutch PDF:

- stale linked GLD wording in the conclusion: `GLD moet bewijzen dat het nog steeds een stabiliserende hedgefunctie heeft`
- English enum leakage in the Dutch current-position table: `No / under review`

Patch under verification:

- `runtime/scrub_nl_client_language.py` now normalizes stale linked GLD phrases in native Dutch reports.
- `runtime/scrub_nl_client_language.py` now normalizes `No / under review` to `Nee / onder herbeoordeling`.

Validation focus after completion:

- Current Position Review / Review huidige posities must keep numeric scores for every active ETF.
- Dutch report must not contain stale current-surface GLD wording.
- Dutch report must not contain `No / under review`.
- Section 7A must retain semantic thesis labels.
- Delivery evidence remains SMTP-send manifest evidence only, not inbox receipt.
