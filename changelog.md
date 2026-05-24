# Weekly ETF OS — Changelog

This file records meaningful codebase, workflow, rendering, state-contract, pricing, and delivery changes for `market-predictions/weekly-etf`.

## 2026-05-24 — Treat DBC as optional RS duel proxy

### What changed
- Updated `tools/validate_replacement_duel_rs_coverage.py` so `DBC` is no longer a hard-required GLD challenger for the 1m/3m relative-strength gate.
- `GSG` remains the required broad-commodity challenger and `BIL` remains the required cash-like ballast challenger for GLD.
- `DBC` remains configured in the replacement-duel target map and can still be used when relative-strength data is available.

### Why
A fresh production run failed before report rendering because `DBC` lacked 1m/3m yfinance return data. That should not block the entire ETF production run when the required GLD replacement-duel coverage is still available through `GSG` and `BIL`. This keeps the RS quality gate intact for strategic required duels while treating source-fragile secondary proxies as optional.

### Affected files
- `tools/validate_replacement_duel_rs_coverage.py`
- `changelog.md`

### Validation / evidence
- Previous workflow failure: `Replacement duel RS coverage failed: required strategic tickers lack 1m/3m returns: DBC`. Next validation step is a fresh ETF production run.

---

## 2026-05-24 — Keep valuation history as first Section 7 table

### What changed
- Updated `runtime/add_etf_pricing_basis_section.py` so the explicit closing-price disclosure is inserted after the Section 7 valuation-history table rather than before it.

### Why
The equity-curve parser and validator intentionally treat the first table in Section 7 as the portfolio valuation history. Placing the new pricing-basis table before that table caused the validator to parse the wrong table and report `Section 7 has only 0 point(s)`. The disclosure remains visible in Section 7, but no longer breaks the existing equity-curve contract.

### Affected files
- `runtime/add_etf_pricing_basis_section.py`
- `changelog.md`

### Validation / evidence
- Previous workflow failure: `ETF equity curve history validation failed ... Section 7 has only 0 point(s); expected at least 3.` Next validation step is a fresh ETF production run.

---

## 2026-05-24 — Fix pricing-basis disclosure validator after ticker linkification

### What changed
- Updated `tools/validate_etf_pricing_basis_disclosure.py` so it normalizes TradingView markdown links back to plain ticker symbols before checking whether each holding row is present.

### Why
The pricing-basis disclosure was inserted before the ticker-linkification step. By validation time, cells such as `SPY` had become `[SPY](https://www.tradingview.com/chart/?symbol=SPY)`. The validator still looked only for raw `| SPY |` table cells, causing a false failure that looked like missing prices even though the pricing pass itself had completed.

### Affected files
- `tools/validate_etf_pricing_basis_disclosure.py`
- `changelog.md`

### Validation / evidence
- Previous workflow failure: `missing pricing row for PAVE, SMH, PPA, SPY, URNM, GLD` in both EN/NL reports after ticker-linkification. Next validation step is a fresh ETF production run.

---

## 2026-05-23 — Add explicit closing-price disclosure to ETF report

### What changed
- Added `runtime/add_etf_pricing_basis_section.py` to inject an explicit EN/NL Section 7 disclosure table showing each holding's close date used, close price used, currency, pricing source, and pricing status.
- Added `tools/validate_etf_pricing_basis_disclosure.py` to fail the workflow if the latest EN/NL reports do not show per-holding close-price basis and EUR/USD FX basis.
- Updated `.github/workflows/send-weekly-report.yml` so the pricing-basis disclosure is inserted before polish/localization/linkification and validated before delivery.

### Why
The latest report showed the portfolio valuation date and equity curve, but it was still not clear which actual closing prices were used for each ETF holding. The report should make the pricing basis audit visible to the reader, not only persist it in `output/pricing/`.

### Affected files
- `runtime/add_etf_pricing_basis_section.py`
- `tools/validate_etf_pricing_basis_disclosure.py`
- `.github/workflows/send-weekly-report.yml`
- `changelog.md`

### Validation / evidence
- Next validation step is a fresh ETF production run. The report should include `Closing prices used in this report` / `Gebruikte slotkoersen in dit rapport` in Section 7.

---

## 2026-05-21 — Use earlier ETF close availability cutoff

### What changed
- Updated `pricing/run_pricing_pass.py` so `US_CLOSE_AVAILABLE_UTC` is now `20:45` instead of `22:30`.

### Why
A fresh ETF run after the regular U.S. cash close still selected the previous trading day because the close-date resolver waited until 22:30 UTC. The new 20:45 UTC cutoff lets evening-Europe runs use the just-completed U.S. close while still leaving a buffer after the regular market close.

### Affected files
- `pricing/run_pricing_pass.py`
- `changelog.md`

### Validation / evidence
- Next validation step is a fresh ETF production run. It should request the latest completed close rather than falling back to the previous trading day when run after 20:45 UTC.
