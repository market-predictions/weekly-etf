# Weekly ETF fresh report request

requested_by: ChatGPT Project session
requested_at: 2026-06-12
reason: WP16-FOLLOWUP4 rerun after isolating the equity curve before pricing disclosure

verify_before_acceptance:
- GitHub Actions run success
- run manifest exists
- delivery manifest exists
- English and Dutch report artifacts exist
- Dutch equity curve renders visibly without clipping
- chart placeholder is positioned before pricing disclosure in generated Markdown
- no visible wp16-nl-equity-curve-guard text
- no macro content change
- no portfolio mutation
- no deterministic macro promotion
- no historical output mutation
