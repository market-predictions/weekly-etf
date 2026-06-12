# Weekly ETF fresh report request

requested_by: ChatGPT Project session
requested_at: 2026-06-12
reason: WP16-FOLLOWUP5 rerun after root-cause fix for Dutch equity-curve PNG rendering

verify_before_acceptance:
- GitHub Actions run success
- run manifest exists
- delivery manifest exists
- English and Dutch report artifacts exist
- Dutch equity curve PNG is opaque/visible and not blank or transparent in the lower chart area
- Dutch equity curve renders visibly in the PDF
- English equity curve remains visible
- no macro content change
- no portfolio mutation
- no deterministic macro promotion
- no historical output mutation
