# ETF Pricing Source Rules — NEW

## Purpose
This file defines the **pricing operating system** for ETF valuation in `daily-etf` without relying on paid APIs or broker-specific integrations.

The objective is to make ETF pricing:
- trustworthy
- repeatable
- auditable
- scalable to new tickers
- resilient to issuer-page gaps and public quote inconsistency

This file is the human-readable policy layer that supports:
- `control/ETF_INSTRUMENT_REGISTRY.csv`
- `output/pricing_evidence_log.csv`
- `prompts/as_is_split/02_INPUT_STATE_CONTRACT.md`
- `prompts/as_is_split/04_OPERATIONAL_RUNBOOK.md`

---

## Core rule
Do **not** treat ETF pricing as a hardcoded per-ticker list.
Treat pricing as a **framework** that can classify, validate, and onboard new instruments.

A new ETF may be analytically attractive before it is operationally pricing-ready.
That distinction must be preserved.

---

## Instrument onboarding states
Every ETF instrument must be classified into one of these operational states.

### 1. `candidate`
The ETF has appeared in analysis or thematic discovery, but has not yet passed pricing validation.

Allowed use:
- Structural Opportunity Radar
- Best New Opportunities
- watchlists

Not yet allowed use:
- live tracked portfolio holdings
- implemented portfolio weights
- section 15 current holdings table

### 2. `provisional`
The ETF has enough public pricing support to be usable in a live tracked portfolio, but source trust is still weaker than ideal.

Allowed use:
- live tracked portfolio if the thesis is strong and the evidence log is explicit
- action tables with caution

Required label:
- pricing must be logged as provisional or accepted fallback

### 3. `active_tracked`
The ETF has a stable pricing route and can be tracked operationally as a live portfolio instrument.

Allowed use:
- full portfolio implementation
- live revaluation
- carry-forward state
- equity-curve integration

### 4. `rejected_operationally`
The ETF may be analytically interesting, but current free public pricing is too inconsistent or too opaque.

Allowed use:
- mention in qualitative analysis only

Not allowed use:
- live tracked portfolio

---

## Source rule classes
Each instrument in the registry must have a `source_rule_class`.

### `issuer_first`
Use the issuer page first, then confirm with a public fallback source.

Use this when:
- issuer pages reliably show market price and/or closing price
- issuer pages are accessible without login or paid service

Examples:
- State Street / SPDR
- VanEck
- Global X
- Sprott

### `issuer_or_marketdata`
Try the issuer page first, but a public market-data page may be the main accepted source if the issuer page is incomplete.

Use this when:
- issuer data exists but is not always publication-ready for the run timing
- a strong public quote source is consistently available

### `quorum_required`
No single free source is trusted enough on its own.
Two independent public sources must agree within tolerance.

Use this when:
- issuer page is weak, stale, or not clearly actionable for market close
- public quote pages are usable but must be cross-checked

### `manual_review`
Automatic source selection is not yet trusted.
The ticker requires explicit human review before operational use.

Use this when:
- instrument is new and classification is unclear
- exchange/issuer mapping is ambiguous
- free source coverage is inconsistent

---

## Preferred source hierarchy
For ETF close valuation, the general hierarchy is:

1. official issuer or fund page with explicit market price / closing price and date
2. issuer market-price page or issuer summary page with dated market value data
3. reputable public market-data history page
4. reputable public fallback quote page
5. prior verified close only if current validation cannot be completed

For FX conversion (USD/EUR):
1. same-day reputable FX/central-bank/public source
2. latest ECB reference rate or equivalent public official reference
3. prior verified FX basis only if fresh basis cannot be verified

---

## Acceptance logic
Each ticker gets a pricing decision during the run.

### `accepted`
Use when:
- the selected source is consistent with the source rule class
- the as-of date is clear enough for the run
- the confirming source is within tolerance

### `accepted_fallback`
Use when:
- a perfect issuer-quality close is not available
- but a sufficiently strong fallback pair or fallback + issuer combination exists

### `carried_forward`
Use when:
- the ticker could not be repriced reliably in this run
- and the prior verified value is intentionally reused

### `manual_review_required`
Use when:
- pricing evidence is inconsistent
- the source date is unclear
- or source trust is too weak

A `manual_review_required` ticker should not newly enter the live portfolio in that run.

---

## Tolerance rules
Recommended starting tolerances:

### Issuer + confirmation source
Accept if relative difference is <= 0.50%

### Fallback + fallback
Accept if relative difference is <= 0.25%

### Above tolerance
Status should become:
- `manual_review_required`
- or `carried_forward` if already active and prior verified price exists

---

## Per-ticker fallback rule
Never freeze the entire portfolio solely because one ticker is unresolved.

If enough of the portfolio can be repriced, repricing must proceed **per ticker**.
Only unresolved tickers may be carried forward.

This means:
- pricing acceptance is ticker-level
- portfolio repricing is aggregated after ticker-level decisions
- carry-forward must be narrow, not portfolio-wide by default

---

## Theme vs instrument distinction
A theme may be valid before the ETF implementation is operationally ready.

Therefore a new instrument must pass two different gates:

### Gate 1 — investment thesis gate
Is the ETF relevant to the macro / geopolitical / structural view?

### Gate 2 — pricing operability gate
Can the ETF be valued repeatedly and credibly using free public sources?

If Gate 1 passes but Gate 2 fails:
- the theme may still appear in qualitative sections
- the instrument should not yet enter the live tracked portfolio

---

## Required evidence log fields
Every run should append one row per ticker to the pricing evidence log with at least:
- run_date
- target_price_date
- ticker
- issuer
- onboarding_state
- source_rule_class
- source_1_name
- source_1_asof
- source_1_price
- source_2_name
- source_2_asof
- source_2_price
- chosen_price
- chosen_fx_basis
- chosen_status
- acceptance_reason
- manual_review_flag

---

## Registry maintenance rule
The registry is allowed to start with the current tracked ETFs, but it must be able to grow over time.

When a new ticker appears:
1. classify it
2. attempt source discovery
3. assign onboarding state
4. record source rule class
5. log pricing evidence
6. only then allow it into live tracked holdings if status is good enough

---

## Operational prohibitions
Do not:
- hardcode the entire pricing system around the current six tickers only
- accept a new ticker into live holdings without a pricing trail
- freeze the full portfolio because one ticker is missing
- silently reuse a stale total NAV
- treat the chart as authoritative if the holdings arithmetic says otherwise

---

## Default implementation direction
Use this file together with:
- `control/ETF_INSTRUMENT_REGISTRY.csv`
- `output/pricing_evidence_log.csv`
- valuation sanity checks in the input/state contract
- fail-loud delivery checks in the operational runbook
