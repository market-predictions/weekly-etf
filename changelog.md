# Weekly ETF OS — Changelog

This file records meaningful codebase, workflow, rendering, state-contract, pricing, and delivery changes for `market-predictions/weekly-etf`.

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
