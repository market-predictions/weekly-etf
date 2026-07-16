# Weekly ETF Cockpit-First Surface Roadmap

Date: 2026-06-18
Status reconciled: 2026-07-16
Repository: `market-predictions/weekly-etf`

## Purpose

Develop a cockpit-first product surface for the US Weekly ETF Review while keeping the current production report intact.

The cockpit is a separate preview and review lane until an explicit promotion decision authorizes a production change.

## Stable boundary

In scope:

- US Weekly ETF presentation surface;
- runtime-state-derived cockpit HTML/PDF previews;
- bilingual English/Dutch presentation;
- visual and state-safety contracts;
- source/provenance clarity;
- side-by-side review against the classic report;
- explicit promotion decision packages.

Out of scope:

- `market-predictions/weekly-etf-eu`;
- UCITS mapping or EU investability;
- broker availability, PRIIPs/KID or Dutch tax handling;
- portfolio decisions, target weights or fundability changes;
- pricing logic or pricing authority changes;
- trade-ledger, valuation-history or recommendation-scorecard mutation;
- model execution;
- production delivery or email behavior;
- silent replacement of the classic report.

## Authority model

The cockpit is a presentation layer only.

It may read current authority from:

```text
output/runtime/latest_etf_report_state_path.txt
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/macro/latest.json
```

It may write generated preview/review artifacts only under:

```text
output/cockpit_preview/
output/cockpit_review/
```

It must not mutate:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/pricing/
output/runtime/
output/run_manifests/
output/delivery/
```

## Four-layer distinction

### 1. Decision framework

The cockpit should allow a reader to identify quickly:

- current market regime;
- what was executed this week;
- what was not executed;
- current performance and main risk;
- main discipline point;
- next decision trigger.

It summarizes existing authority and may not create a new portfolio decision.

### 2. Input/state contract

Current post-execution runtime values override pre-execution, previous, inherited or editorial-memory values.

Current authority precedence for cockpit holdings is:

```text
current_weight_pct
then target_weight_pct
then previous_weight_pct
then weight_inherited_pct
```

Market-value precedence is:

```text
market_value_eur
then previous_market_value_eur
```

A legitimate current value of zero is authoritative.

Historical values may appear only when explicitly labelled as historical.

### 3. Output contract

Cockpit preview filenames remain separate from production report filenames:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.pdf
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.pdf
```

Side-by-side review artifacts remain under:

```text
output/cockpit_review/
```

Generated workflow artifacts are preview/review evidence, not delivery evidence.

### 4. Operational runbook

Cockpit work remains package- and claim-controlled.

Every package must:

1. read `control/SYSTEM_INDEX.md`, `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md` and this roadmap;
2. check for an active claim or overlapping PR;
3. use a narrow branch and handover;
4. run focused tests and listed production validators;
5. prove protected authority files unchanged;
6. preserve `promotion_status: not_promoted` unless a separate explicit decision changes it;
7. avoid SMTP, model execution and production delivery paths.

## Historical roadmap and factual completion status

### WP01 — Preview renderer

```text
status: implemented_and_merged
PR: #52
```

Delivered:

- deterministic runtime-state-driven cockpit renderer;
- bilingual HTML and optional PDF output;
- preview-only filenames and output directory;
- no production report replacement.

### WP02 — Manual preview workflow

```text
status: implemented_and_merged
PR: #52
```

Delivered:

- `workflow_dispatch`-only preview rendering;
- read-only repository permission;
- artifact upload only;
- no SMTP, send or state-persistence step.

### WP03 — Visual and state-safety contracts

```text
status: implemented_and_merged
PR: #53
```

Delivered tests proving:

- required English/Dutch cockpit components;
- preview-only output paths and names;
- no production report overwrite;
- no state, pricing, runtime, run-manifest or delivery mutation;
- no delivery or inbox claims.

### WP04 — Side-by-side review

```text
status: implemented_and_merged
PR: #54
promotion_status: not_promoted
```

Delivered a deterministic review layer under `output/cockpit_review/`.

### WP05 — Promotion decision review

```text
status: implemented_and_merged
PR: #55
decision: not_promoted_needs_iteration
promotion_status: not_promoted
```

No production, delivery or state change was authorized.

### WP06 — Iteration or promotion path

```text
status: implemented_and_merged
PR: #56
selected_path: iteration_path
promotion_status: not_promoted
```

The safe iteration path was selected because no coordinator approval existed for promotion.

### WP07 — Source/provenance iteration

```text
status: implemented_and_merged
PR: #57
promotion_status: not_promoted
```

Delivered visible bilingual evidence context for runtime state, valuation history, pricing audit, macro pack, run manifest, preview-only status and no-delivery status.

## July 2026 current-runtime revalidation

Package:

```text
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION
PR: #74
status: validated_governance_reconciliation_in_progress
```

The revalidation did not recreate WP01. It found three correctness defects in the existing renderer:

1. previous weights were selected before current weights;
2. previous market values were selected before current market values;
3. executed rotations were described only as a generic action-present state.

The renderer now derives the July 14 execution as:

```text
EN: URNM reduced · XBI added
NL: URNM afgebouwd · XBI toegevoegd
```

and shows the authoritative transitions:

```text
URNM 7.01% -> 2.01%
XBI 0.00% -> 5.00%
```

The original visual direction, preview paths, provenance section, classic-report separation and no-promotion status remain intact.

Validation evidence:

```text
implementation_head: e605eb8de532eed44ec9c44a7be7c6705f128893
workflow_run: 29525632206
conclusion: success
focused_tests: 33 passed
production_delivery_html_contract: passed
macro_thesis_leakage_validator: passed
protected_authority_hashes_before_after: identical
email_send: false
portfolio_model_execution: false
promotion_status: not_promoted
```

## Next package — WP08

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
status: next_after_PR_74_closeout
layer: decision framework + output contract
promotion_status: not_promoted
```

### Goal

Compare the current classic July 14 report with the corrected current-runtime cockpit after the provenance iteration.

### Required dimensions

- decision clarity;
- executed-action clarity;
- current-weight accuracy;
- performance/risk accuracy;
- source/provenance clarity;
- English/Dutch semantic parity;
- readability and density;
- visual hierarchy;
- premium look and feel;
- preservation of audit evidence.

### Acceptance

- current classic and cockpit artifacts can be reviewed side by side;
- the review uses current runtime authority rather than June fixtures;
- review output remains under `output/cockpit_review/`;
- `promotion_status` remains `not_promoted`;
- no email, model execution, pricing, state, ledger or delivery mutation occurs;
- an explicit review conclusion and next package are recorded.

WP08 is not a promotion package. Any attachment, front-page or replacement path requires a subsequent explicit decision.

## Stable decision

The production report remains intact. Cockpit development remains a forked preview/review lane. Promotion requires explicit authority and evidence from a separate decision package.
