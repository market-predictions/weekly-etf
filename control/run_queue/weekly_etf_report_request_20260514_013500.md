# Weekly ETF Review report request

requested_at_utc: 2026-05-14T01:35:00Z
requested_run_date: 2026-05-14
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled quality test run.

## Purpose
Validate the native Dutch report architecture after fixing the bilingual numeric parity validator so it recognizes native Dutch numeric table headers in Section 15 and Section 7.

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
`send_report_runtime_html.py` now extends the legacy parity validator alias maps at runtime so native Dutch client-facing labels are canonicalized to the same numeric fields as the English report.

Native Dutch labels that must be accepted include:

- `Prijs lokaal` / `Lokale prijs` → `price (local)`
- `Marktwaarde lokaal` / `Lokale marktwaarde` → `market value (local)`
- `Marktwaarde EUR` / `Marktwaarde in EUR` → `market value (eur)`
- `Gewicht %` / `Weging %` → `weight %`
- `Aantal stukken` → `shares`
- `Portefeuillewaarde EUR` / `Portefeuillewaarde in EUR` → `portfolio value (eur)`
- `Toelichting` → `comment`
- `Startkapitaal EUR`, `Belegde marktwaarde EUR`, `Totale portefeuillewaarde EUR` as Section 15 label variants.

## Hard Dutch-language requirements
- The Dutch report must start with native Dutch structure such as `Wekelijkse ETF-review`, `Kernsamenvatting`, `Portefeuille-acties`, `Regime-dashboard`, `Review huidige posities`, and `Huidige posities en cash`.
- The Dutch report title may use a Dutch long date, but validation and delivery must still preserve date/version parity with the English report.
- Dutch numeric tables may use native Dutch client-facing labels; the validator must compare the underlying canonical numeric fields, not force English-shaped column labels.
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
5. Bilingual pair validation output, especially Section 15 numeric parity.
6. Dutch language quality validator output.
7. Dutch markdown report, especially tables and executive cards.
8. Dutch delivery HTML/PDF cover, date header and chart labels.
9. Delivery manifest or receipt.
