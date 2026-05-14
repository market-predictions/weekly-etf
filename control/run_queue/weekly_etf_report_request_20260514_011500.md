# Weekly ETF Review report request

requested_at_utc: 2026-05-14T01:15:00Z
requested_run_date: 2026-05-14
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled quality test run.

## Purpose
Validate the new native Dutch report architecture. The Dutch companion report must now be rendered directly from runtime state using Dutch templates, not generated as a translated or patched copy of the English markdown.

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

## Recent changes under validation
- Added `runtime/render_etf_report_nl_from_state.py` as a native Dutch state-based renderer.
- Switched `runtime/render_etf_report_from_state.py` so `render_nl(state)` uses the native Dutch renderer.
- Updated `runtime/add_etf_position_performance_section.py` to use native Dutch mappings for the Dutch performance table.
- Updated `runtime/fix_report_output_contract.py` so it skips destructive English-heading patching for native Dutch output.
- Updated `runtime/polish_runtime_reports.py` so the Dutch polish layer is a no-op for native Dutch reports.
- Updated `runtime/apply_nl_localization.py` so native Dutch output only receives light safety cleanup, not broad English-to-Dutch replacement passes.

## Hard Dutch-language requirements
- The Dutch report must start with Dutch structure such as `Wekelijkse ETF-review`, `Kernsamenvatting`, `Portefeuille-acties`, `Regime-dashboard`, `Review huidige posities`, and `Huidige posities en cash`.
- The Dutch report must not contain English cover/card labels such as PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY, Investor Report, Analyst Report, confidence, or Mixed / not yet decisive.
- Dutch tables must not contain English column headers such as Theme, Primary ETF, Why it matters, What needs to happen, Current status, Original Thesis, New weight, Funding source, or Action executed.
- Dutch tables must not contain half-translated phrases such as `Kapitaaluitgaven and`, `ondersteunen` inside English clauses, `Investable maar`, `Volglijst only`, `SMH remains`, or `Useful only if`.
- The Dutch report must preserve acceptable investment terms and protected tokens: ETF, tickers, cash, hedge, drawdown, beta, capex, UCITS, USD, EUR, official product names, official index names, numeric values and URLs.
- The English report remains canonical for research and decision logic.
- The Dutch report must preserve bilingual numeric parity and portfolio-state parity with the English report.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
After the run, inspect:
1. Native Dutch renderer log output.
2. `ETF_OUTPUT_CONTRACT_FIX_SKIPPED` for the Dutch report.
3. `ETF_RUNTIME_POLISH_NL_SKIPPED` for the Dutch report.
4. `ETF_NL_LOCALIZATION_OK | native_dutch=True`.
5. Dutch language quality validator output.
6. Dutch markdown report, especially tables and executive cards.
7. Dutch delivery HTML/PDF cover, date header and chart labels.
8. Delivery manifest or receipt.
