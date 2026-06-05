# Weekly ETF report request

Date: 2026-06-05

Purpose:

Trigger a fresh Weekly ETF Pro production run after fixing the remaining Dutch delivery-surface enum leakage.

The `_10` reports confirmed:

- Current Position Review score completeness remains fixed.
- Dutch stale GLD conclusion wording is fixed.
- Remaining issue: Dutch PDF still shows `No / under review` in the Review huidige posities fresh-cash column for DFEN and XLU.

Root cause:

The delivery HTML/PDF position-review panel is regenerated from runtime state by `runtime.delivery_html_overrides`, bypassing the markdown scrubbed table. Therefore the fix must exist at delivery-runtime level, not only in markdown scrubbing.

Patch under verification:

- `sitecustomize.py` now extends the delivery HTML override fresh-cash enum map with:
  - `no / under review` -> `Nee / onder herbeoordeling`
  - `no` -> `Nee`
- `sitecustomize.py` also adds `No / under review` to Dutch delivery forbidden tokens.

Validation focus after completion:

- Dutch PDF/HTML must not contain `No / under review`.
- Dutch Review huidige posities must show `Nee / onder herbeoordeling` for DFEN and XLU.
- Current Position Review / Review huidige posities must keep numeric scores for every active ETF.
- Dutch stale GLD current-surface wording must remain cleaned.
- Delivery evidence remains SMTP-send manifest evidence only, not inbox receipt.
