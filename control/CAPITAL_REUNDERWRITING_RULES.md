# ETF Capital Re-underwriting Rules

## Purpose

This file is the ETF decision-framework addendum that converts the first-principles portfolio critique into deterministic operating rules.

It does **not** replace `etf.txt`. It tightens the decision layer between current-position scoring and the final action table.

## Core principle

Every holding must earn capital again each run.

The right question is not only:

> Should we keep what we already bought?

The required question is:

> If this position did not exist today, would we initiate it now, at this weight, with fresh capital?

## Mandatory capital re-underwriting layer

Run this layer after current-position scoring and before the final action table.

For every current holding, assess:

1. Fresh cash test
2. Thesis versus implementation split
3. Relative alternative duel when a position is replaceable or weakening
4. Contribution / drag test
5. Factor-overlap test
6. Hedge validity test where relevant
7. Cash policy test
8. Action-clock / inertia test
9. Replacement pricing and duel evidence

## Fresh cash test

For every holding, state internally and, where decision-relevant, in Section 10:

| Test | Allowed values |
|---|---|
| Would initiate today? | Yes / Smaller / No |
| Would initiate at current weight? | Yes / No |
| Fresh-cash implication | Add / Hold / Reduce / Replace / Close / Watch one more week |

Rules:
- If a holding would not be initiated today at any size, default action cannot remain unqualified Hold.
- If a holding would only be initiated smaller, it must be tagged Reduce candidate or Hold — under review.
- Any override must name the reason and the maximum review window.

## Thesis versus implementation split

Separate every position into:

| Score | Meaning |
|---|---|
| Thesis score | Is the long-term structural or macro thesis still valid? |
| Implementation score | Is this ETF, at this price, trend, weight, and vehicle quality still the right implementation? |

Rules:
- A valid thesis does not automatically justify keeping the current ETF or current weight.
- If thesis score is high but implementation score is weak, force a direct alternative duel.
- If both thesis and implementation are weak, default action must be Reduce or Close unless portfolio-level risk logic explicitly overrides it.

## Relative alternative duel

A position must be compared directly with a named alternative when any of these are true:

- it is listed as Hold but replaceable
- it is a Reduce candidate
- it is down more than 10% from average entry
- it has underperformed the portfolio for two consecutive runs
- an alternative ETF is named in the Structural Opportunity Radar or Final Action Table
- a ticker is named under `Best replacements to fund`

Minimum duel fields:

| Test | Current holding | Alternative | Winner |
|---|---:|---:|---|
| Latest verified close date | | | |
| Latest verified close price | | | |
| 1-month relative strength | | | |
| 3-month relative strength | | | |
| Liquidity / spread | | | |
| Theme purity | | | |
| Drawdown from recent high | | | |
| Portfolio differentiation | | | |
| Final verdict | | | |

If data is incomplete, say so and treat the duel as unresolved, not as permission for indefinite Hold.

## Replacement pricing and duel evidence

The report may mention a challenger as a **replacement candidate** only if it has at least a visible pricing and comparison status.

Rules:
- `Best replacements to fund` must not imply a fundable replacement unless the challenger has a latest verified close, close date, and comparison status.
- If the challenger has no verified close, the correct status is `Not fundable yet — pricing missing`.
- If the challenger has a verified close but no relative-strength comparison, the correct status is `Priced but duel incomplete`.
- If the challenger has verified close data and a completed duel, the correct status may be `Fundable replacement candidate`.
- A same-report switch from current holding to challenger requires current holding and challenger to share the same close-date basis or a clearly disclosed exception.
- Named alternatives in `Best replacements to fund`, `Final Action Table`, and Section 16 must be included in the pricing shortlist when ticker symbols are parseable.

Required compact report block when replacements are mentioned:

### Replacement pricing and duel status

| Current holding | Challenger | Current close | Challenger close | Close-date basis | Duel status | Decision implication |
|---|---|---:|---:|---|---|---|

This block may be compact, but it must exist when the report names fundable challengers.

## Factor-overlap test

Assess factor exposure, not only ticker count.

Required factor map:

| Factor | Exposure level | Main contributors | Concern |
|---|---|---|---|
| U.S. tech / AI sentiment | Low / Medium / High | | |
| U.S. equity beta | Low / Medium / High | | |
| Real-rate sensitivity | Low / Medium / High | | |
| Geopolitical resilience | Low / Medium / High | | |
| Non-U.S. equity | Low / Medium / High / Zero | | |
| Commodity / hard-asset exposure | Low / Medium / High | | |

Rules:
- If a single factor exceeds roughly 40% effective exposure, the report must call it concentration, not diversification.
- If non-U.S. equity exposure is zero, the report must say whether that is an intentional U.S. exceptionalism bet.
- If SPY and SMH are both large weights, explicitly test whether SPY still diversifies or merely duplicates U.S. tech/AI sentiment.

## Hedge validity test

For any hedge or ballast position, assess:

| Hedge test | Allowed values |
|---|---|
| Did it protect during equity stress? | Yes / No / Unclear |
| Did it protect during geopolitical or inflation stress? | Yes / No / Unclear |
| Is the current price verified? | Yes / No |
| Is the drawdown acceptable for a hedge? | Yes / No |
| Does it still diversify the portfolio? | Yes / No / Unclear |
| Better hedge candidate? | Ticker / None / Unresolved |

Rules:
- A hedge down more than 10% with unverified current pricing must be tagged Hedge review.
- A hedge that fails realized ballast behavior cannot remain full-size without explicit override.
- Hedge logic must not be used as a vague reason to ignore poor implementation.

## Cash policy test

Cash must be classified each run:

| Cash type | Meaning |
|---|---|
| Tactical reserve | Deliberately held for pullback |
| Uninvested residual | Leftover from whole-share implementation |
| Risk reserve | Held because regime uncertainty is elevated |
| Deployment candidate | Should be allocated this run |

Rules:
- If cash is above 3% and at least one lane is Actionable now, explain why cash is not deployed.
- If cash is above 5%, call it a meaningful portfolio position.
- Do not let residual cash hide as an unexplained drag.

## Action-clock / inertia test

A weak or replaceable position cannot remain indefinitely in ambiguous Hold.

Rules:
- A position may not remain `Hold but replaceable` for more than two consecutive runs without a direct decision: upgrade, reduce, replace, or close.
- A position down more than 10% and still below a 4.00 total score must be re-underwritten from scratch.
- A position underperforming the portfolio by more than 7 percentage points for two consecutive runs must be re-underwritten.
- Any override must include a next-review trigger and a maximum review window.

## Deterministic action triggers

| Trigger | Required action |
|---|---|
| Holding underperforms portfolio by >7% for two consecutive runs | Re-underwrite |
| Holding is down >10% and trend/implementation score is weak | Reduce or explicit override |
| Holding is replaceable for two consecutive runs | Direct alternative duel |
| Hedge is down >10% and fails ballast test | Reduce / replace / justify |
| Cash >3% and an Actionable now lane exists | Deploy or explain reserve |
| Single factor exposure >40% | Explicit concentration warning |
| No non-U.S. exposure | Explicit U.S. exceptionalism statement |
| Replacement challenger named without verified close | Mark not fundable yet or remove from fundable language |

## Required report integration

### Section 2 — Portfolio Action Snapshot
If `Best replacements to fund` mentions challengers, include or immediately follow it with `Replacement pricing and duel status`.

### Section 6 — Bottom Line
Mention the single most important discipline issue if one exists:
- concentration
- cash deployment
- hedge validity
- replaceable holding
- loss-making holding requiring re-underwriting
- unpriced or incompletely priced replacement duel

### Section 10 — Current Position Review
Add, where practical:
- Would initiate today?
- Would initiate at current weight?
- Thesis score
- Implementation score
- Best alternative
- Required next action
- Replacement duel status where a challenger is named

### Section 13 — Final Action Table
If the fixed table cannot be extended without rendering risk, encode discipline in `Short Reason` and ensure the machine-readable scorecard stores the full fields.

### Section 16 — Continuity Input
Carry forward:
- positions under review
- replaceable timer
- best alternative
- hedge review status
- factor concentration note
- cash policy note
- replacement duel status

## Machine-readable state requirement

Every canonical English pro report should be derivable into:

`output/etf_recommendation_scorecard.csv`

This scorecard is the explicit memory layer for:
- fresh cash test
- thesis score
- implementation score
- replaceable status
- action-clock timer
- best alternative
- contribution drag
- factor overlap
- hedge validity
- required next action
- override reason
- replacement close status
- replacement duel status

The scorecard is report-derived for now, but it is the bridge toward independent implementation-state authority.
