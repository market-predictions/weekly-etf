# Pricing State Authority Migration

## Purpose

This migration removes markdown reports as the primary holdings authority for ETF pricing passes.

Historically:
- `pricing/run_pricing_pass.py`
- parsed Section 15 from the latest markdown report.

That created architectural fragility:
- trigger placeholders could become the latest report
- partially-rendered markdown could break pricing
- pricing depended on presentation output

## New authority order

Pricing holdings authority becomes:

1. `output/etf_portfolio_state.json`
2. markdown Section 15 only as fallback

## Migration strategy

Phase 1:
- add portfolio-state-first parsing
- keep markdown fallback for compatibility

Phase 2:
- remove markdown holdings parsing entirely
- render Section 15 directly from runtime state

## Operational impact

This prevents:
- broken report placeholders from corrupting pricing
- pricing recursion through markdown
- report-render failures from breaking pricing state

It also enables:
- deterministic runtime synthesis
- report-independent pricing audits
- safer bilingual rendering
