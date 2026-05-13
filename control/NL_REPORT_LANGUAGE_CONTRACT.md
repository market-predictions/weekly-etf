# Dutch ETF Report Language Contract

## Purpose

The Dutch Weekly ETF Review must read as a native, premium Dutch investor report for professional readers at Dutch banks, wealth managers, and investment firms.

The Dutch report is not a literal translation layer. It is a Dutch companion generated from the same analytical state as the English report.

## Non-negotiable rules

1. No mixed English/Dutch sentences.
2. No client-facing workflow, runtime, artifact, source-file, or validator language.
3. No literal financial-English calques that sound unnatural in Dutch.
4. Tickers, ETF names, official index names, currencies, and accepted market terms may remain in English.
5. Section titles, table headers, table enum values, action labels, status labels, and decision text must use controlled Dutch wording.
6. The cover and executive summary must be fully Dutch, unless the product is explicitly labelled bilingual.
7. The Dutch report must preserve numeric and portfolio-state parity with the English canonical report.
8. The Dutch report must not introduce independent research conclusions.

## Allowed English terms

These terms may remain untranslated when used naturally in Dutch investment language:

- ETF / ETFs
- ticker / tickers
- cash
- hedge
- drawdown
- beta
- capex
- risk-on / risk-off
- AI
- semiconductor
- outperformance
- UCITS
- USD / EUR
- S&P 500, Nasdaq 100, Russell 2000 and other official index names
- official ETF product names
- ticker symbols such as SPY, SMH, PPA, PAVE, URNM, GLD

## Terms that must not appear client-facing

The Dutch client report must not contain:

- Keep / Require / Force / Add / Hold / Reduce / Close as action words
- Existing / New / Yes / No / None as table enum values
- under review, current status, duel required, funding, fresh cash
- Section, runtime, state-led, output/, pricing_audit, manifest, workflow, render, artifact
- live repo state, production path, report scaffold, placeholder
- earned leader, price proof, thesisfit, actiebias, reviewpositie

## Preferred institutional Dutch style

Use compact, decision-oriented Dutch:

- “aanhouden” rather than “hold”
- “nieuw kapitaal” or “aanvullende allocatie” rather than “fresh cash”
- “vervangingsanalyse” rather than “replacement duel”
- “onder herbeoordeling” rather than “under review”
- “volglijst” rather than “watchlist” when a Dutch term reads better
- “best onderbouwde kernpositie” rather than “verdiende leider”
- “koersbevestiging” rather than “prijsbewijs”
- “aansluiting op de beleggingscase” rather than “thesisfit”

## Report-generation rule

The English report remains the analytical source of truth. The Dutch report must be generated through a controlled Dutch localization/template layer using `runtime/nl_localization.py`, not through one-off ad hoc phrase replacements in validators or delivery scripts.

## Quality gate

`tools/validate_etf_dutch_language_quality.py` must fail the workflow when the Dutch report contains mixed-language decision sentences, untranslated table labels, internal workflow language, or known low-quality literal translations.
