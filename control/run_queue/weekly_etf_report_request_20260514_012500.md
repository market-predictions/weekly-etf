# Weekly ETF Review report request

requested_at_utc: 2026-05-14T01:25:00Z
requested_run_date: 2026-05-14
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled quality test run.

## Purpose
Validate the native Dutch report architecture after updating runtime bilingual validation to accept a native Dutch long-date report title.

## Architecture under test
The expected Dutch path is:

runtime state
→ native Dutch renderer
→ ticker linkify
→ native Dutch position-performance section
→ light safety cleanup only
→ Dutch language quality validator
→ bilingual numeric parity validation
→ HTML/PDF render validation
→ delivery HTML contract validation
→ email delivery

## Recent fix under validation
`send_report_runtime_html.py` now accepts native Dutch report-title dates such as:

- `Wekelijkse ETF-review Donderdag 14 mei 2026`

instead of requiring only an ISO title date such as:

- `2026-05-14`

The runtime parser should convert the Dutch long date back to ISO internally for delivery/parity checks while preserving the Dutch client-facing title.

## Hard Dutch-language requirements
- The Dutch report must start with native Dutch structure such as `Wekelijkse ETF-review`, `Kernsamenvatting`, `Portefeuille-acties`, `Regime-dashboard`, `Review huidige posities`, and `Huidige posities en cash`.
- The Dutch report title may use a Dutch long date, but validation and delivery must still preserve date/version parity with the English report.
- The Dutch report must not contain English cover/card labels such as PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY, Investor Report, Analyst Report, confidence, or Mixed / not yet decisive.
- Dutch tables must not contain English column headers such as Theme, Primary ETF, Why it matters, What needs to happen, Current status, Original Thesis, New weight, Funding source, or Action executed.
- Dutch tables must not contain half-translated phrases such as `Kapitaaluitgaven and`, `Investable maar`, `Volglijst only`, `SMH remains`, or `Useful only if`.
- Preserve acceptable investment terms and protected tokens: ETF, tickers, cash, hedge, drawdown, beta, capex, UCITS, USD, EUR, official product names, official index names, numeric values and URLs.
- The English report remains canonical for research and decision logic.
- The Dutch report must preserve bilingual numeric parity and portfolio-state parity with the English report.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
After the run, inspect:
1. Native Dutch renderer log output.
2. `ETF_OUTPUT_CONTRACT_FIX_SKIPPED` for the Dutch report.
3. `ETF_RUNTIME_POLISH_NL_SKIPPED` for the Dutch report.
4. `ETF_NL_LOCALIZATION_OK | native_dutch=True`.
5. Bilingual pair validation output.
6. Dutch language quality validator output.
7. Dutch markdown report, especially tables and executive cards.
8. Dutch delivery HTML/PDF cover, date header and chart labels.
9. Delivery manifest or receipt.
