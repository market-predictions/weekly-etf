# Decision — Cockpit current-runtime authority

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Status: accepted for preview lane
Promotion status: `not_promoted`

## Decision

The cockpit preview must present current post-execution runtime values whenever they are available.

Authority precedence for position weights is:

```text
current_weight_pct
then target_weight_pct
then previous_weight_pct
then weight_inherited_pct
```

Authority precedence for position market value is:

```text
market_value_eur
then previous_market_value_eur
```

A current numeric value of zero is authoritative. It must not be treated as missing and replaced by an older non-zero value.

## Executed-action surface

When the runtime state contains executed position deltas, the cockpit must identify the affected tickers and reader-facing action direction. It may not reduce an executed rotation to generic wording such as `action present`.

For the authoritative 2026-07-14 execution, the expected semantic result is:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

with the weight transitions derived from state:

```text
URNM 7.01% -> 2.01%
XBI 0.00% -> 5.00%
```

The tickers and values are regression evidence, not hardcoded template content.

## Boundary

This decision applies only to the cockpit preview and review presentation layer.

It does not authorize:

```text
production promotion
email delivery
portfolio model execution
new portfolio decisions
pricing changes
state mutation
trade-ledger mutation
delivery-manifest creation
```

## Evidence

```text
PR: #74
implementation_head: e605eb8de532eed44ec9c44a7be7c6705f128893
validation_run: 29525632206
validation_conclusion: success
focused_tests: 33 passed
protected_authority_hashes: identical before and after
promotion_status: not_promoted
```
