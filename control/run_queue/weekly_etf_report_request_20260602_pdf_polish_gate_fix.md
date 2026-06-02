# Weekly ETF production rerun request

Purpose: trigger production validation after fixing the replacement-duel PDF-polish sanitizer.

Expected proof:
- ETF_PDF_POLISH_CONTRACT_OK appears in the client-surface gate logs.
- English delivery HTML no longer has stale replacement-duel section number 11.
- Dutch delivery HTML no longer has duplicate Vervangingsanalyse surface.
- Pricing-lineage gate remains passed.

Delivery success must still not be claimed without a delivery receipt or user confirmation.
