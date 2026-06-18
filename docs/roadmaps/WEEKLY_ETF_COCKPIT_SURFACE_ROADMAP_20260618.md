# Weekly ETF Cockpit-First Surface Roadmap

Date: 2026-06-18
Repository: `market-predictions/weekly-etf`
Status: approved roadmap anchor / production report remains intact

## Purpose

This roadmap starts a new product-surface production cycle for the US Weekly ETF Review.

The goal is to build a cockpit-first front-page preview layer while keeping the current production report intact.

The current production report remains the stable source of delivery. The cockpit-first surface is developed as a separate branch and preview artifact until explicitly promoted.

## Scope boundary

In scope:

- US ETF report only.
- Cockpit-first front page and product surface.
- Runtime-state-derived preview HTML/PDF.
- Side-by-side QA against the current report.
- Work-package discipline, claims, handovers, and promotion decision gates.

Out of scope:

- `market-predictions/weekly-etf-eu`.
- UCITS mapping.
- Dutch broker availability.
- PRIIPs/KID execution layer.
- Box 3 / Dutch tax execution layer.
- EU ticker substitutions.
- EU investability scoring.
- Portfolio state changes.
- Pricing changes.
- Target-weight changes.
- Lane-scoring or fundability changes.
- Trade-ledger or execution behavior changes.
- Delivery behavior changes.

The ETF EU / UCITS execution-mapping work is a separate parallel track and must not be folded into this US cockpit-surface roadmap.

## Authority model

The cockpit-first surface is a presentation layer only.

It may read:

```text
output/runtime/latest_etf_report_state_path.txt
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

It may write preview artifacts only under:

```text
output/cockpit_preview/
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

The cockpit must answer, quickly and plainly:

- Where are we in the market regime?
- What are we doing this week?
- What are we not doing?
- What is the main active risk?
- What is the next decision trigger?

The cockpit must not create new portfolio authority. It summarizes the current runtime state and existing report decisions.

### 2. Input/state contract

The cockpit must be generated from existing runtime and valuation artifacts. It must not hardcode example trades, example tickers, or mock-up values.

### 3. Output contract

The preview output must create separate cockpit artifacts without replacing the current report:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_cockpit_<token>_<seq>.pdf
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_<token>_<seq>.pdf
```

### 4. Operational runbook

The cockpit work must be developed as work packages, with claim status and handover notes. No worker should implement a package before checking the control files and confirming that the package is not already claimed.

## Six-step roadmap

### Step 1 — Create isolated branch and preview lane

Create a branch for cockpit-surface development:

```text
feature/cockpit-front-page-v1
```

The branch must not modify production send behavior. The current report on `main` remains the stable production report.

Deliverables:

- branch plan
- preview artifact naming rules
- first work-package claim/handover convention

Acceptance:

- production report remains untouched
- no send workflow behavior change
- no state/pricing/scoring mutation

### Step 2 — Add deterministic cockpit renderer

Add a renderer that turns runtime state into a cockpit-first HTML/PDF preview.

Expected file:

```text
runtime/render_cockpit_front_page.py
```

The renderer should produce the first-page structure inspired by `etf_review_front.html`:

- masthead
- short plain-language summary
- market climate / regime card
- this week's action card
- performance & risk card
- main discipline point

Acceptance:

- generated from runtime state, not hardcoded mock-up data
- English and Dutch variants render
- output goes only to `output/cockpit_preview/`

### Step 3 — Add manual-only preview workflow

Add a manual-only GitHub Actions workflow for rendering cockpit previews.

Expected file:

```text
.github/workflows/render-cockpit-preview.yml
```

The workflow must not send email and must not update portfolio state.

Acceptance:

- workflow is `workflow_dispatch` only
- no SMTP/email step
- no trade-ledger or portfolio-state mutation
- preview artifacts are committed or uploaded according to an explicit decision in the package

### Step 4 — Add visual and state-safety contract tests

Add tests and validators proving that the cockpit preview exists separately and does not damage production output.

Test coverage should prove:

- current production report still renders
- cockpit preview exists separately
- cockpit preview contains the expected front-page components
- no delivery-manifest claims are changed
- no portfolio state files are modified
- English and Dutch surfaces are both present

Acceptance:

- focused test suite passes
- existing production validators remain green
- no state mutation is detected

### Step 5 — Side-by-side comparison review

Produce side-by-side review artifacts:

```text
classic PDF
cockpit preview PDF
```

Review dimensions:

- readability
- density
- visual hierarchy
- decision clarity
- trust/provenance clarity
- premium look and feel
- preservation of audit evidence

Acceptance:

- coordinator can compare old and new without losing the production report
- explicit visual QA notes are recorded in a handover file
- no promotion yet unless explicitly approved

### Step 6 — Promotion decision

Only after side-by-side review, decide whether the cockpit becomes:

```text
A. extra attachment
B. first page of the existing report
C. replacement for current front matter
D. rejected / continue as experiment
```

Default recommendation for first promotion is option A: extra attachment.

Acceptance:

- explicit promotion decision recorded
- no silent replacement of production report
- delivery evidence remains evidence-bound
- no inbox receipt is claimed unless separately proven

## Work-package operating regime

Every cockpit-surface package must follow this pattern:

1. Read `control/SYSTEM_INDEX.md`, `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and this roadmap.
2. Check whether the package is already claimed or in progress.
3. If unclaimed, claim it by updating the relevant control/handover file or by following the package-specific claim instruction.
4. Keep the scope narrow.
5. Run only the relevant focused tests plus any listed validators.
6. Do not touch production portfolio/pricing/scoring/execution/delivery behavior unless explicitly authorized.
7. Write a handover under `control/handovers/` or the package-specific handover path.
8. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` only with factual status.

## Initial work packages

### WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER

Layer: output contract + operational runbook

Goal: create the isolated cockpit preview renderer and output path, without changing the production report or delivery behavior.

Status: not_started

### WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW

Layer: operational runbook

Goal: add a manual-only preview workflow that renders cockpit artifacts without sending email or mutating state.

Status: blocked until WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER is complete

### WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS

Layer: output contract + operational runbook

Goal: add visual/state-safety tests for the cockpit preview lane.

Status: blocked until WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER is complete

### WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW

Layer: decision framework + output contract

Goal: compare current report versus cockpit preview and decide whether the surface is good enough for promotion review.

Status: blocked until WP_COCKPIT_SURFACE_02_PREVIEW_WORKFLOW and WP_COCKPIT_SURFACE_03_VISUAL_CONTRACTS are complete

### WP_COCKPIT_SURFACE_05_PROMOTION_DECISION

Layer: decision framework

Goal: decide whether the cockpit surface remains experimental, becomes an extra attachment, becomes the first page, or replaces the current front matter.

Status: blocked until WP_COCKPIT_SURFACE_04_SIDE_BY_SIDE_REVIEW is complete

## Stable decision

The current report remains intact. Cockpit-first development proceeds as a forked surface branch and preview lane. Promotion requires an explicit decision.
