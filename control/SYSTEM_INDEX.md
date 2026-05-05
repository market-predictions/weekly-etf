# ETF Review OS — System Index

This file is the first entry point for serious work on the `weekly-etf` system.

## Purpose

This repository contains:
1. execution files that generate and deliver reports
2. control files that define authority, architecture, and next actions
3. production output/state files
4. lab-only research files that must not become production authority without explicit review

## Four-layer operating model

Always distinguish:

1. **Decision framework** — what the ETF review is trying to decide.
2. **Input/state contract** — where authoritative facts come from and how conflicts are resolved.
3. **Output contract** — how the final English/Dutch reports must be structured and rendered.
4. **Operational runbook** — how GitHub Actions and scripts execute validation, rendering, state refresh, and delivery.

## Session start rule

For ETF architecture, debugging, prompt, workflow, state, pricing, or delivery work, read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution files

## Canonical execution files

- `etf.txt` — production masterprompt for the Weekly ETF Review.
- `control/CAPITAL_REUNDERWRITING_RULES.md` — authoritative decision-framework addendum for fresh-cash tests, action clocks, hedge checks, factor-overlap checks, cash policy, and recommendation discipline.
- `etf-pro.txt` — premium English editorial delivery layer.
- `etf-pro-nl.txt` — Dutch companion delivery layer derived from the completed English report.
- `send_report.py` — HTML/PDF/email delivery logic and manifest handling.
- `.github/workflows/send-weekly-report.yml` — production send workflow.
- `.github/workflows/refresh-etf-state-from-report.yml` — explicit state refresh workflow.
- `.github/workflows/send-weekly-report-split-test.yml` — split-test delivery comparison workflow.
- `.github/workflows/lab-pyportfolioopt-optimization.yml` — lab-only optimizer workflow.

## Canonical state files

- `output/etf_portfolio_state.json` — current machine-readable ETF portfolio state.
- `output/etf_valuation_history.csv` — machine-readable valuation history.
- `output/etf_trade_ledger.csv` — machine-readable executed-change ledger.
- `output/etf_recommendation_scorecard.csv` — machine-readable recommendation discipline and capital re-underwriting memory.
- `output/pricing/` — persisted pricing audits.
- `output/lane_reviews/` — machine-readable lane assessment artifacts.

## State-model scripts

- `tools/write_etf_minimum_state.py`
- `tools/write_etf_trade_ledger.py`
- `tools/write_etf_recommendation_scorecard.py`

## Lab-only files

- `tools/generate_pyportfolioopt_optimization_lab.py`
- `tools/fetch_etf_optimizer_prices_yfinance.py`
- `docs/ETF_OPTIMIZATION_LAB.md`
- `lab_inputs/`
- `lab_outputs/`

Lab outputs are never production truth unless explicitly promoted through a reviewed architecture decision.

## Non-negotiable discipline

- Do not collapse decision framework, state contract, output contract, and runbook back into one opaque prompt.
- Do not weaken the ETF executive look and feel.
- Do not treat prior report prices as current prices when fresh pricing is feasible.
- Do not let the Dutch companion become an independent research pass.
- Do not claim email delivery without a receipt or manifest.
- Do not let `Hold but replaceable` become indefinite inertia; apply `control/CAPITAL_REUNDERWRITING_RULES.md`.

## Current direction of travel

ETF is moving toward:

- GitHub as external source of truth
- ChatGPT Project as workbench
- explicit pricing/state artifacts
- English canonical report plus Dutch companion
- lane assessment artifacts for breadth discipline
- recommendation scorecard artifacts for capital discipline
- lab-only optimization as a QA/research surface, not a production allocator
