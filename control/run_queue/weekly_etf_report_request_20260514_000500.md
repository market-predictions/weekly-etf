# Weekly ETF Review report request

requested_at_utc: 2026-05-14T00:05:00Z
requested_run_date: 2026-05-14
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled Dutch quality test run.

## Purpose
This run validates the broader centralized Dutch HTML masthead validation fix after previous runs failed at the HTML/PDF render validation step.

## Required production path
Use the current validated runtime-driven bilingual baseline:

pricing audit
→ historical relative strength
→ macro policy research pack
→ first-pass lane discovery
→ targeted challenger pricing
→ replacement-duel pricing validation
→ final lane discovery
→ runtime ETF state
→ EN/NL markdown render
→ full valuation-history Section 7 equity curve
→ polish/linkify
→ Dutch localization contract pass
→ Dutch client-language scrub
→ equity-curve history validation
→ ETF position performance validation
→ ETF report content contract validation
→ Dutch language quality validation
→ persisted pricing audit validation
→ lane breadth proof validation
→ replacement-duel pricing proof validation
→ bilingual numeric parity validation
→ HTML/PDF render validation
→ delivery HTML contract validation
→ explicit state derivation validation
→ email delivery

## Recent fix under validation
`send_report.py` now centralizes Dutch masthead validation and accepts both English fallback and localized Dutch masthead terms, including:

- weekly etf review
- weekly etf pro review
- weekly etf intelligence
- wekelijkse etf-review
- wekelijkse etf review
- wekelijks etf-review
- wekelijks etf review
- beleggersrapport
- analistenrapport

The validator should now provide a useful HTML excerpt if masthead validation still fails.

## Hard requirements
- English HTML must retain a valid English masthead block.
- Dutch HTML/PDF may use Dutch cover labels and must pass Dutch masthead validation.
- No mixed English/Dutch decision sentences in the Dutch markdown or delivery HTML.
- No residual decision words such as `fundable`, `not fundable`, `funding`, `funding source`, `funding note`, `funding challengers`, `before funding`, or `after funding`.
- No partial localization artifacts such as `Aanhouden but replaceable`, `active review items`, `passive holds`, `but treat`, or ticker lists using English `and`.
- No English client-facing labels in the Dutch report such as Investor Report, Analyst Report, PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY.
- No internal workflow language such as runtime, workflow, manifest, artifact, output/, pricing_audit, state-led, placeholder.
- No low-quality literal translations such as verdiende leider, prijsbewijs, thesisfit, actiebias, reviewpositie, nuttige ballast, vers kapitaal.
- Preserve allowed professional terms: ETF, ticker, cash, hedge, drawdown, beta, capex, UCITS, USD, EUR, official product names, official index names and ticker symbols.
- Preserve bilingual numeric parity and portfolio-state parity.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.
