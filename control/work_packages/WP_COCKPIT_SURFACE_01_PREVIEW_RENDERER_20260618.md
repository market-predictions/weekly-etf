# Work Package — WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER

Repository:

```text
market-predictions/weekly-etf
```

Do not touch:

```text
market-predictions/weekly-etf-eu
market-predictions/weekly-index
market-predictions/weekly-fx
```

## Layer

```text
input/state contract
output contract
operational runbook
```

## Reconciled status — 2026-07-16

```text
historical_implementation_status: implemented_and_merged
historical_implementation_pr: 52
current_runtime_revalidation_status: validated_ready_for_merge
current_runtime_revalidation_pr: 74
promotion_status: not_promoted
selected_path: iteration
```

The original `not_started` status was stale. The renderer and manual preview workflow were implemented in June 2026 and merged through PR #52. This file retains the original package purpose while recording the factual implementation and current-runtime validation status.

## Historical implementation sequence

```text
WP01 — preview renderer: merged in PR #52
WP02 — manual preview workflow: merged in PR #52
WP03 — visual/state-safety contracts: merged in PR #53
WP04 — side-by-side review: merged in PR #54
WP05 — promotion decision review: merged in PR #55
WP06 — iteration path decision: merged in PR #56
WP07 — source/provenance iteration: merged in PR #57
```

WP05 recorded:

```text
decision: not_promoted_needs_iteration
promotion_status: not_promoted
```

WP06 selected:

```text
selected_path: iteration_path
```

## Original purpose

Create an isolated cockpit-first preview renderer for the US Weekly ETF report while keeping the production report intact.

The package established:

```text
runtime/render_cockpit_front_page.py
.github/workflows/render-cockpit-preview.yml
tests/test_cockpit_front_page_preview.py
output/cockpit_preview/
```

The cockpit remains a parallel presentation surface. It has no portfolio, pricing, execution, delivery or promotion authority.

## Current-runtime defect found in 2026-07 revalidation

The June renderer selected continuity fields before post-execution authority:

```text
previous_weight_pct before current_weight_pct
previous_market_value_eur before market_value_eur
```

It also reduced an executed rotation to generic wording:

```text
Portfolio action — Action present in runtime state.
Portefeuilleactie — Actie aanwezig volgens runtime state.
```

This was incorrect for the authoritative 2026-07-14 executed state:

```text
URNM: Sell -122.008961 shares; 7.01% -> 2.01%
XBI: Buy +40.491749 shares; 0.00% -> 5.00%
```

## Current authority contract

The preview renderer now applies:

```text
current_weight_pct
then target_weight_pct
then previous_weight_pct
then weight_inherited_pct
```

For market value:

```text
market_value_eur
then previous_market_value_eur
```

A legitimate current value of zero is authoritative and must not fall through to an older non-zero value.

Executed-action wording is derived from the current runtime state. For the July 14 execution the preview renders semantically parallel wording:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

with the executed weight transitions shown in the action note.

## Output boundary

Preview output remains restricted to:

```text
output/cockpit_preview/
```

Side-by-side review output remains restricted to:

```text
output/cockpit_review/
```

Generated output is workflow-artifact evidence only and is not report delivery evidence.

## Safety boundary

```text
production_promotion: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
preview_only: true
```

## Validation evidence

Implementation head:

```text
head_sha: e605eb8de532eed44ec9c44a7be7c6705f128893
workflow_run: 29525632206
conclusion: success
```

Validated gates:

- 33 focused cockpit and report-surface tests passed;
- production delivery HTML contract passed;
- macro/thesis leakage validator passed;
- bilingual July 14 cockpit preview rendered;
- URNM reduction and XBI addition were found in English and Dutch output;
- side-by-side review retained `promotion_status: not_promoted`;
- nine protected authority files and pointer targets had identical SHA-256 values before and after;
- no email, model execution, production report replacement or authority mutation occurred.

## Next package

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```

WP08 must review the corrected current-runtime cockpit against the current classic report. It remains preview-only and may not promote the cockpit without a separate explicit decision.
