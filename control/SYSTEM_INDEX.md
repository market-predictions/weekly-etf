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
4. **Operational runbook** — how GitHub Actions and scripts execute validation, rendering, state refresh, discovery, pricing, and delivery.

## Session start rule

For ETF architecture, debugging, prompt, workflow, state, pricing, discovery, macro/thesis, or delivery work, read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution files

For handover-heavy sessions or when resuming after a pause, also read:

5. `control/ETF_SESSION_CHANGELOG.md`
6. the relevant specialized changelog, if any

## Canonical control files

- `control/ETF_SESSION_CHANGELOG.md` — broad session/worklog changelog for all meaningful ETF architecture, workflow, roadmap, validator, runtime, delivery, and handover-relevant changes.
- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md` — authoritative design contract for the pricing-lineage hardening cycle, including immutable audit identity, state persistence, exact close-date semantics, provider lineage, independent verification, and challenger pricing tiers.
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md` — central pricing-lineage changelog for regression review and implementation tracking.
- `docs/roadmaps/WEEKLY_ETF_MACRO_THESIS_ROADMAP_20260531.md` — approved phased roadmap for macro/thesis modernization. It is a roadmap, not immediate production authority.
- `MACRO_METHODOLOGY.md` — methodology and compliance boundary for macro/regime/thesis content before client-surface promotion.

## Canonical execution files

- `etf.txt` — production masterprompt for the Weekly ETF Review.
- `control/CAPITAL_REUNDERWRITING_RULES.md` — authoritative decision-framework addendum for fresh-cash tests, action clocks, hedge checks, factor-overlap checks, cash policy, and recommendation discipline.
- `control/LANE_DISCOVERY_CONTRACT.md` — authoritative discovery contract for broad ETF lane scanning, historical relative strength, and two-pass challenger pricing.
- `control/ETF_RUNTIME_STATE_CONTRACT.md` — runtime input/state authority contract.
- `config/etf_discovery_universe.yml` — broad investable ETF lane universe used by discovery.
- `config/macro_data_sources.yml` — shadow-mode macro audit source configuration for FRED, ECB, Treasury, and volatility inputs.
- `config/cb_calendar.yml` — static central-bank calendar/control fixture until vetted official live calendar coverage is added.
- `config/driver_catalog.yml` — closed, versioned Stage-1 macro/thesis driver catalog. Shadow-only; no client-facing or portfolio-action authority.
- `config/driver_beneficiary_map.yml` — curated Stage-1 driver-to-ETF-lane beneficiary map using existing ETF universe `taxonomy_tag` values. Shadow-only.
- `macro_sources/build_macro_data_audit.py` — run-scoped macro audit builder.
- `tools/validate_macro_data_audit.py` — macro audit contract validator.
- `schemas/macro_data_audit.schema.json` — macro audit schema shell.
- `schemas/macro_policy_pack.schema.json` — macro policy pack schema/compatibility contract for the legacy pack and future deterministic regime engine.
- `tools/validate_macro_policy_pack.py` — macro policy pack schema and compatibility validator. It must pass before lane discovery consumes `output/macro/latest.json`.
- `tools/validate_macro_compliance.py` — macro/regime/thesis compliance validator for predictive wording, uncited overlay, orphan macro figures, Stage-1 candidate leakage, and shadow/internal label leakage before any client-surface promotion.
- `runtime/build_thesis_candidates.py` — deterministic Stage-1 thesis candidate builder. Writes internal-only shadow artifacts and validates mapped lanes against `config/etf_discovery_universe.yml`.
- `runtime/fetch_etf_relative_strength.py` — historical relative-strength fetcher for discovery scoring.
- `runtime/discover_etf_lanes.py` — lane discovery runtime that writes the matching lane artifact.
- `runtime/score_etf_lanes.py` — deterministic lane scoring and promotion logic.
- `pricing/augment_challenger_pricing.py` — targeted second-pass challenger pricing augmenter.
- `runtime/build_macro_policy_pack.py` — legacy macro policy pack builder, now emitting schema-versioned compatibility fields and recording Phase 2 macro audit metadata as shadow-only input.
- `runtime/build_etf_report_state.py` — deterministic runtime state builder.
- `runtime/render_etf_report_from_state.py` — runtime-driven English/Dutch markdown renderer.
- `runtime/polish_runtime_reports.py` — post-render editorial polish layer.
- `runtime/link_runtime_report_tickers.py` — context-aware ticker linkification layer.
- `runtime/delivery_html_overrides.py` — delivery-layer HTML overrides for branded sections that require strict layout/clickable behavior.
- `tools/validate_etf_delivery_html_contract.py` — dynamic render-regression validator for delivery HTML.
- `send_report.py` — base HTML/PDF/email delivery logic and manifest handling.
- `send_report_runtime_html.py` — delivery entrypoint that applies runtime-state HTML overrides before PDF/email output.
- `etf-pro.txt` — premium English editorial delivery layer.
- `etf-pro-nl.txt` — Dutch companion delivery layer derived from the completed English report.
- `.github/workflows/send-weekly-report.yml` — production send workflow.
- `.github/workflows/validate-macro-compliance.yml` — isolated macro compliance validation workflow with safe and planted-failure fixtures.
- `.github/workflows/validate-thesis-candidates-shadow.yml` — isolated Stage-1 thesis candidate validation workflow. Not part of production report delivery.
- `.github/workflows/refresh-etf-state-from-report.yml` — explicit state refresh workflow.
- `.github/workflows/send-weekly-report-split-test.yml` — split-test delivery comparison workflow.
- `.github/workflows/lab-pyportfolioopt-optimization.yml` — lab-only optimizer workflow.

## Canonical state files

- `output/etf_portfolio_state.json` — current machine-readable ETF portfolio state.
- `output/etf_valuation_history.csv` — machine-readable valuation history.
- `output/etf_trade_ledger.csv` — machine-readable executed-change ledger.
- `output/etf_recommendation_scorecard.csv` — machine-readable recommendation discipline and capital re-underwriting memory.
- `output/pricing/` — persisted pricing audits.
- `output/run_manifests/` — intended location for immutable ETF run manifests once `ETF_PRICING_LINEAGE_CONTRACT_V1` is implemented.
- `output/market_history/etf_relative_strength.json` — historical market-strength metrics used by discovery scoring when available.
- `output/lane_reviews/` — machine-readable lane assessment artifacts created by the lane discovery engine.
- `output/runtime/` — normalized runtime state artifacts.
- `output/macro/macro_data_audit_<reference_date>_<run_id>.json` — run-scoped shadow-mode macro audit artifact.
- `output/macro/latest_macro_data_audit_path.txt` — pointer to the latest macro audit artifact.
- `output/macro/latest.json` — current schema-versioned macro policy pack consumed by lane discovery.
- `output/macro/validation/latest_macro_regime_shadow_validation.json` — repo-visible proof for the isolated deterministic macro-regime shadow workflow.
- `output/macro/latest_thesis_candidates.json` — internal Stage-1 thesis candidate artifact when explicitly built. Shadow-only; not a report input or portfolio-action authority.

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
- Do not treat priced challengers as automatically fundable; challenger pricing only enables fairer comparison.
- Do not repair branded sections that require strict layout/clickable behavior through markdown post-processing; render them from runtime state at the delivery HTML layer and protect them with the delivery HTML validator.
- Do not describe ETF pricing lineage as solved merely because the closing-price disclosure table is visible; the lineage contract requires immutable audit identity, explicit manifest linkage, state persistence, and audit-to-report validation.
- Do not let Phase 2 macro audit values change regime, confidence, lane scoring, fundability, or client-facing wording until later regime/compliance/bilingual gates explicitly promote them.
- Do not allow predictive macro/regime/thesis wording, uncited overlay claims, orphan macro figures, Stage-1 candidate leakage, or shadow/internal labels onto the client surface.
- Do not treat Stage-1 thesis candidates as fundable, reportable, or portfolio-action authority.

## Current direction of travel

ETF is moving toward:

- GitHub as external source of truth
- ChatGPT Project as workbench
- explicit pricing/state artifacts
- immutable pricing audit and run manifest lineage
- runtime-derived English canonical report plus Dutch companion
- delivery HTML as the authority for branded strict-layout sections
- lane discovery artifacts for breadth, novelty, market strength, and challenger discipline
- valuation-grade challenger pricing only when a challenger is replacement-ready or fundable
- recommendation scorecard artifacts for capital discipline
- provenance-backed macro audit artifacts in shadow mode
- schema-versioned macro policy pack compatibility before deterministic regime promotion
- methodology and compliance gates before client-surface macro/thesis expansion
- Stage-1 thesis candidates as internal-only shadow artifacts before Stage-2 confirmation and fundable integration
- lab-only optimization as a QA/research surface, not a production allocator
