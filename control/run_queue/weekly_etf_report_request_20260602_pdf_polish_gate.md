# Weekly ETF production rerun request

Purpose: trigger production validation after wiring the PDF-polish contract into the existing client-surface gate.

Expected proof:
- Validate ETF delivery HTML contract runs.
- tools/validate_etf_client_surface_clean.py runs.
- tools/validate_etf_client_surface_clean.py calls the PDF-polish contract internally.
- Logs include ETF_PDF_POLISH_CONTRACT_OK.
- Pricing-lineage gate remains passed.

Delivery success must still not be claimed without a delivery receipt or user confirmation.
