# Weekly ETF OS — Changelog

This file records meaningful codebase, workflow, rendering, state-contract, pricing, and delivery changes for `market-predictions/weekly-etf`.

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
