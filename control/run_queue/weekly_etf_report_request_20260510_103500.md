# Weekly ETF report request

requested_at_utc: 2026-05-10T10:35:00Z
requested_run_date: 2026-05-10
mode: production-e2e-validation
reason: Retry after moving client-facing placeholder sanitizer into the standalone delivery HTML validator path.
expected_path: GitHub Actions send-weekly-report workflow
required_success_markers:
- ETF_DELIVERY_HTML_CONTRACT_OK
- RUNTIME_SECTION15_OK
- RUNTIME_EQUITY_CURVE_OK
- DELIVERY_OK
