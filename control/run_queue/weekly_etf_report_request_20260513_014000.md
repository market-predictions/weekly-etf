# Weekly ETF Review report request

requested_at_utc: 2026-05-13T01:40:00Z
requested_run_date: 2026-05-13
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled Dutch quality test run.

## Purpose
This run validates the new Dutch client-language scrub layer added after the previous run failed on residual English decision wording around `fundable` and `funding`.

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

## Dutch quality checks under validation
- Validate `runtime/scrub_nl_client_language.py` runs after `runtime/apply_nl_localization.py` and before `tools/validate_etf_dutch_language_quality.py`.
- Validate residual English allocation and decision terms are scrubbed before Dutch quality validation.
- Validate the Dutch language quality validator remains strict.
- Validate Dutch markdown, delivery HTML, and PDF do not expose internal or mixed-language terms.

## Hard Dutch-language requirements
- No mixed English/Dutch decision sentences.
- No residual decision words such as `fundable`, `not fundable`, `funding`, `funding source`, `funding note`, `funding challengers`, `before funding`, or `after funding`.
- No partial localization artifacts such as `Aanhouden but replaceable`, `active review items`, `passive holds`, `but treat`, or ticker lists using English `and`.
- No English client-facing labels such as Investor Report, Analyst Report, PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY.
- No English table labels such as Theme, Primary ETF, Why it matters, Current status, Existing, Yes, No, None, Hold, Add.
- No internal workflow language such as runtime, workflow, manifest, artifact, output/, pricing_audit, state-led, placeholder.
- No low-quality literal translations such as verdiende leider, prijsbewijs, thesisfit, actiebias, reviewpositie, nuttige ballast, vers kapitaal.
- Preserve allowed professional terms: ETF, ticker, cash, hedge, drawdown, beta, capex, UCITS, USD, EUR, official product names, official index names and ticker symbols.
- Preserve bilingual numeric parity and portfolio-state parity.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Recent fixes under validation
- Added `runtime/scrub_nl_client_language.py`.
- Wired `python -m runtime.scrub_nl_client_language --output-dir output` into `.github/workflows/send-weekly-report.yml` immediately after Dutch localization.
