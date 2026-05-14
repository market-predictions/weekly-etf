# Weekly ETF Review report request

requested_at_utc: 2026-05-14T00:15:00Z
requested_run_date: 2026-05-14
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled Dutch quality test run.

## Purpose
This run validates the broader Dutch report-quality improvements after adding centralized Dutch table/section mappings and routing the Dutch scrubber through them.

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
→ Dutch report-date localization
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

## Recent fixes under validation
- Added `runtime/nl_table_section_mappings.py` as a centralized mapping layer for Dutch table headers, enum values, radar phrases, action/decision phrases, valuation-history comments and analyst/continuity appendix text.
- Routed `runtime/scrub_nl_client_language.py` through the centralized table/section mapping layer.
- Added generic Dutch date localization using `runtime/nl_dates.py` and `runtime/localize_nl_report_dates.py`.
- Centralized Dutch delivery HTML cover/date/chart localization in `runtime/client_facing_sanitizer.py`.
- Delivery HTML validation now checks Dutch output against the same centralized sanitizer contract.

## Hard Dutch-language requirements
- No English date header such as Wednesday, Thursday, May, June, etc. in the Dutch report or Dutch delivery HTML.
- No English cover/card labels such as PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY, Investor Report or Analyst Report in Dutch output.
- No English executive-card values such as confidence, Mixed / not yet decisive, or Keep the current allocation disciplined.
- No English table headers such as Theme, Primary ETF, Why it matters, What needs to happen, Current status, Original Thesis, New weight or Funding source.
- No residual decision words such as fundable, not fundable, funding, funding source, funding note, funding challengers, before funding, or after funding.
- No partial localization artifacts such as Aanhouden but replaceable, active review items, passive holds, but treat, Neene, Toevoegened, Verlagend, or Sluitend.
- No English valuation-history comments such as Inaugural model portfolio established, Fresh per-ticker repricing, Fresh six-of-six, Fresh five-of-six, Latest close basis, or carried forward.
- No English analyst/continuity appendix phrases such as Original Thesis, Thesis changes, Replacement challengers, Balanced growth with resilience bias, Defense thesis valid, or Hedge role must be proven.
- Preserve accepted professional terms: ETF, tickers, cash, hedge, drawdown, beta, capex, UCITS, USD, EUR, official product names, official index names and ticker symbols.
- Preserve bilingual numeric parity and portfolio-state parity.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
After the run, inspect:
1. Dutch language validator output,
2. Dutch markdown report,
3. Dutch delivery HTML/PDF cover and date header,
4. radar tables and action tables,
5. valuation-history comments,
6. analyst/continuity appendix,
7. delivery manifest or receipt.
