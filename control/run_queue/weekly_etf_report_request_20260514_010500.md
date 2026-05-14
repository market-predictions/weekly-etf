# Weekly ETF Review report request

requested_at_utc: 2026-05-14T01:05:00Z
requested_run_date: 2026-05-14
mode: production_quality_test
report_type: weekly_etf_pro_bilingual
request_source: ChatGPT

## Request
Generate and publish a fresh bilingual Weekly ETF Pro Review as a controlled Dutch quality test run.

## Purpose
This run validates the broader residual English artifact-verb cleanup after the previous run failed on `remains` in the Dutch PDF-audit scrub / Dutch language quality path.

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
→ Dutch PDF-audit leak scrub
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

## Recent fix under validation
`runtime/scrub_nl_pdf_audit_leaks.py` was broadened from a narrow linked-ticker phrase fix into a residual English artifact-verb sweep. It should now normalize both ticker-linked and non-ticker residual English verbs, including:

- remains / remain
- needs / need
- requires / require
- offers / offer
- creates / create
- trails / trail
- confirms / confirm
- supports / support

The specific linked ticker rules should still preserve markdown links while localizing the surrounding phrase.

## Hard Dutch-language requirements
- No residual linked or plain ticker phrases such as `SMH remains`, `[SMH](...) remains`, `GLD remains`, `PPA remains`, `PAVE remains`, `] remains`, or ` remains ` in the Dutch report.
- No residual generic English artifact verbs such as remains, remain, needs, creates, offers, requires, trails, confirms, or supports in Dutch client-facing text.
- No English date header such as Wednesday, Thursday, May, June, etc. in the Dutch report or Dutch delivery HTML.
- No English cover/card labels such as PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY, Investor Report or Analyst Report in Dutch output.
- No English executive-card values such as confidence, Mixed / not yet decisive, or Keep the current allocation disciplined.
- No English table headers such as Theme, Primary ETF, Why it matters, What needs to happen, Current status, Original Thesis, New weight or Funding source.
- No residual section/table terms such as AI compute infrastructure, Capital spending, Neetable, SPY plus SMH creates, Structural case is credible, US equities or not promoted this week.
- No residual PDF-audit terms such as Core U.S. large-cap exposure, Cyber spend, Direct replacement duel, Grid buildout, Growth engine, Hedge ballast, Investable maar, Needs supply-chain, Useful only if, Volglijst only or Zero allocation.
- No residual decision words such as fundable, not fundable, funding, funding source, funding note, funding challengers, before funding, or after funding.
- No partial localization artifacts such as Aanhouden but replaceable, active review items, passive holds, but treat, Neene, Toevoegened, Verlagend, or Sluitend.
- No English valuation-history comments such as Inaugural model portfolio established, Fresh per-ticker repricing, Fresh six-of-six, Fresh five-of-six, Latest close basis, or carried forward.
- No English analyst/continuity appendix phrases such as Original Thesis, Thesis changes, Replacement challengers, Balanced growth with resilience bias, Defense thesis valid, or Hedge role must be proven.
- Preserve accepted professional terms: ETF, tickers, cash, hedge, drawdown, beta, capex, UCITS, USD, EUR, official product names, official index names and ticker symbols.
- Preserve bilingual numeric parity and portfolio-state parity.
- Do not claim delivery success unless the workflow emits a real delivery manifest or receipt.

## Review after run
After the run, inspect:
1. Dutch PDF-audit scrub output,
2. Dutch language validator output,
3. Dutch markdown report,
4. Dutch delivery HTML/PDF cover and date header,
5. radar tables and action tables,
6. valuation-history comments,
7. analyst/continuity appendix,
8. delivery manifest or receipt.
