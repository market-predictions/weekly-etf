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

For ETF architecture, debugging, prompt, workflow, state, pricing, discovery, or delivery work, read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution files

## Canonical execution files

- `etf.txt` — production masterprompt for the Weekly ETF Review.
- `control/CAPITAL_REUNDERWRITING_RULES.md` — authoritative decision-framework addendum for fresh-cash tests, action clocks, hedge checks, factor-overlap checks, cash policy, and recommendation discipline.
- `control/LANE_DISCOVERY_CONTRACT.md` — authoritative discovery contract for broad ETF lane scanning and novelty/challenger rules.
- `control/ETF_RUNTIME_STATE_CONTRACT.md` — runtime input/state authority contract.
- `config/etf_discovery_universe.yml` — broad investable ETF lane universe used by discovery.
- `runtime/discover_etf_lanes.py` — lane discovery runtime that writes the matching lane artifact.
- `runtime/score_etf_lanes.py` — deterministic lane scoring and promotion logic.
- `runtime/build_etf_report_state.py` — deterministic runtime state builder.
- `runtime/render_etf_report_from_state.py` — runtime-driven English/Dutch markdown renderer.
- `runtime/polish_runtime_reports.py` — post-render editorial polish layer.
- `runtime/link_runtime_report_tickers.py` — context-aware ticker linkification layer.
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
- `output/lane_reviews/` — machine-readable lane assessment artifacts created by the lane discovery engine.
- `output/runtime/` — normalized runtime state artifacts.

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
- Do not use markdown as the primary pricing or holdings database once runtime state is available.
- Do not treat the Structural Opportunity Radar as a static memory list; run the lane discovery engine before runtime state build.

## Current direction of travel

ETF is moving toward:

- GitHub as external source of truth
- ChatGPT Project as workbench
- explicit pricing/state artifacts
- runtime-derived English canonical report plus Dutch companion
- lane discovery artifacts for breadth, novelty, and challenger discipline
- recommendation scorecard artifacts for capital discipline
- lab-only optimization as a QA/research surface, not a production allocator
